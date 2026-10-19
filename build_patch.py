from pathlib import Path
import hashlib
import re
import struct
import subprocess
import sys
import zipfile

root = Path(__file__).parent
original = root.parent / 'bog-nimingban-v1.2.0.apk'
sdk_tools = Path.home() / 'AppData/Local/Android/Sdk/build-tools/35.0.0'
coexist = '--coexist' in sys.argv

def disable_updates(data):
    """Change only the Expo Updates ENABLED boolean in binary Android XML."""
    data = bytearray(data)
    strings = []
    pos = 8
    changed = 0
    while pos < len(data):
        kind, header_size, size = struct.unpack_from('<HHI', data, pos)
        if kind == 1:
            count, _, flags, strings_start = struct.unpack_from('<IIII', data, pos + 8)
            assert not flags & 0x100, 'Expected UTF-16 Android manifest'
            for index in range(count):
                offset = struct.unpack_from('<I', data, pos + header_size + index * 4)[0]
                start = pos + strings_start + offset
                length = struct.unpack_from('<H', data, start)[0]
                assert length < 0x8000
                text = data[start + 2:start + 2 + length * 2].decode('utf-16le')
                if coexist and (text == 'fun.tiamed' or text.startswith('fun.tiamed.') and text not in ('fun.tiamed.MainApplication', 'fun.tiamed.MainActivity')):
                    text = text.replace('fun.tiamed', 'fun.tiamfx', 1)
                    data[start + 2:start + 2 + length * 2] = text.encode('utf-16le')
                strings.append(text)
        elif kind == 0x102:
            name_index = struct.unpack_from('<I', data, pos + 20)[0]
            if strings[name_index] == 'meta-data':
                attr_start, attr_size, attr_count = struct.unpack_from('<HHH', data, pos + 24)
                attrs = {}
                for index in range(attr_count):
                    attr_pos = pos + 16 + attr_start + index * attr_size
                    _, name, raw, value_size, _, value_type, value = struct.unpack_from('<IIIHBBI', data, attr_pos)
                    attrs[strings[name]] = (attr_pos, value_type, value)
                name_attr = attrs.get('name')
                if name_attr and name_attr[1] == 3 and strings[name_attr[2]] == 'expo.modules.updates.ENABLED':
                    value_pos, value_type, _ = attrs['value']
                    assert value_type == 0x12
                    struct.pack_into('<I', data, value_pos + 16, 0)
                    changed += 1
        pos += size
    assert changed == 1
    return bytes(data)

def patch_resource_package(data):
    data = bytearray(data)
    pos = struct.unpack_from('<H', data, 2)[0]
    changed = 0
    while pos < len(data):
        kind, _, size = struct.unpack_from('<HHI', data, pos)
        if kind == 0x200:
            name = bytes(data[pos + 12:pos + 268]).decode('utf-16le').rstrip('\0')
            assert name == 'fun.tiamed', name
            data[pos + 12:pos + 268] = 'fun.tiamfx'.encode('utf-16le').ljust(256, b'\0')
            changed += 1
        pos += size
    assert changed == 1
    return bytes(data)

with zipfile.ZipFile(original) as apk:
    bundle = apk.read('assets/index.android.bundle').decode('utf-8')
    replacements = [
        ('baseURL:"http://bog.ac/"', 'baseURL:"https://bog.ac/"'),
        ('y=(0,p.default)(t.source),v=', 'y=__bogImageSource((0,p.default)(t.source)),v='),
        ('return y.default.getSize(t).then(', 'return (__bogIsImageUrl(t)?y.default.getSizeWithHeaders(t,__bogImageOptions(t,{}).headers):y.default.getSize(t)).then('),
        ('return y.default.getSizeWithHeaders(t,n).then(', 'return y.default.getSizeWithHeaders(t,(__bogImageOptions(t,{headers:n})||{}).headers).then('),
        ('return new H(e,t,n,i,s)', 'return new H(e,t,__bogImageOptions(e,n),i,s)'),
        ('p.default.downloadAsync(e,t,v({sessionType:h.FileSystemSessionType.BACKGROUND},n))', 'p.default.downloadAsync(e,t,v({sessionType:h.FileSystemSessionType.BACKGROUND},__bogImageOptions(e,n)))'),
        ('return n&&n(o),y.default.prefetchImage(t,o)', 'return n&&n(o),__bogIsImageUrl(t)?y.default.getSizeWithHeaders(t,__bogImageOptions(t,{}).headers).then(function(){return true}):y.default.prefetchImage(t,o)'),
    ]
    for before, after in replacements:
        assert bundle.count(before) == 1, (before, bundle.count(before))
        bundle = bundle.replace(before, after)
    patched_bundle = (root / 'image_headers.js').read_text(encoding='utf-8') + '\n' + bundle
    bundle_path = root / 'index.android.patched.js'
    bundle_path.write_text(patched_bundle, encoding='utf-8')
    subprocess.run(['node', '--check', str(bundle_path)], check=True)
    unsigned = root / 'bog-nimingban-v1.2.0-imagefix-unsigned.apk'
    with zipfile.ZipFile(unsigned, 'w') as output:
        for entry in apk.infolist():
            if re.match(r'META-INF/(?:MANIFEST\.MF|[^/]+\.(?:SF|RSA|DSA|EC))$', entry.filename, re.I):
                continue
            data = apk.read(entry.filename)
            if entry.filename == 'assets/index.android.bundle':
                data = patched_bundle.encode('utf-8')
            elif entry.filename == 'AndroidManifest.xml':
                data = disable_updates(data)
            elif coexist and entry.filename == 'resources.arsc':
                data = patch_resource_package(data)
            output.writestr(entry, data)
        output.writestr('assets/BOG-ORIGINAL-LICENSE.txt', (root / 'LICENSE').read_bytes())
        output.writestr('assets/BOG-IMAGEFIX-NOTICE.txt', (
            'Unofficial local image compatibility patch for bog-nimingban 1.2.0.\n'
            'Original project: https://github.com/tiamed/bog-nimingban\n'
            'Original copyright: Copyright (c) 2022 tiamed. MIT license included.\n'
            'Modified with GPT assistance: forum image Referer/User-Agent headers; '
            'HTTPS API base; disabled original OTA updates; separate package and resource '
            'namespace for coexistence. Signed with a separate local key.\n'
            'This build is not an official release and does not share original app data.\n'
        ).encode('utf-8'))

aligned = root / 'bog-nimingban-v1.2.0-imagefix-aligned.apk'
subprocess.run([str(sdk_tools / 'zipalign.exe'), '-f', '-p', '4', str(unsigned), str(aligned)], check=True)
key = root / 'imagefix-signing.p12'
if not key.exists():
    subprocess.run(['keytool', '-genkeypair', '-keystore', str(key), '-storetype', 'PKCS12', '-storepass', 'bog-imagefix-local', '-keypass', 'bog-imagefix-local', '-alias', 'imagefix', '-keyalg', 'RSA', '-keysize', '2048', '-validity', '10000', '-dname', 'CN=BOG Local Image Fix'], check=True)
final = root.parent / ('bog-nimingban-v1.2.0-imagefix-coexist.apk' if coexist else 'bog-nimingban-v1.2.0-imagefix.apk')
subprocess.run(['cmd.exe', '/c', str(sdk_tools / 'apksigner.bat'), 'sign', '--ks', str(key), '--ks-pass', 'pass:bog-imagefix-local', '--out', str(final), str(aligned)], check=True)
subprocess.run(['cmd.exe', '/c', str(sdk_tools / 'apksigner.bat'), 'verify', '--verbose', str(final)], check=True)
subprocess.run([str(sdk_tools / 'zipalign.exe'), '-c', '-v', '4', str(final)], check=True, stdout=subprocess.DEVNULL)
with zipfile.ZipFile(original) as source, zipfile.ZipFile(final) as patched:
    changed = [name for name in patched.namelist() if name in source.namelist() and not name.startswith('META-INF/') and source.read(name) != patched.read(name)]
    expected = {'AndroidManifest.xml', 'assets/index.android.bundle'}
    if coexist:
        expected.add('resources.arsc')
    assert set(changed) == expected, changed
    assert patched.testzip() is None
    assert patched.read('assets/BOG-ORIGINAL-LICENSE.txt') == (root / 'LICENSE').read_bytes()
print('Changed entries:', changed)
print('Output:', final)
print('SHA256:', hashlib.sha256(final.read_bytes()).hexdigest())
