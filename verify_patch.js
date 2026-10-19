const fs = require('fs');
const vm = require('vm');
const assert = require('assert');
const bundle = fs.readFileSync(__dirname + '/index.android.patched.js', 'utf8');
const context = vm.createContext({console});
vm.runInContext(fs.readFileSync(__dirname + '/image_headers.js', 'utf8'), context);
const image = 'http://bog.ac/image/large/example.jpg';
assert.equal(context.__bogImageOptions(image, {}).headers.Referer, 'https://bog.ac/');
assert.equal(context.__bogImageOptions(image, {}).headers['User-Agent'], 'BOG-nimingban/1.2.0 (Android; ImageFix)');
const external = {uri: 'https://example.com/image/test.jpg', headers: {Authorization: 'test'}};
assert.strictEqual(context.__bogImageSource(external), external);
const local = {uri: 'file:///cache/test.jpg'};
assert.strictEqual(context.__bogImageSource(local), local);
const original = {uri: image, headers: {Accept: 'image/*'}};
assert.equal(context.__bogImageSource(original).headers.Accept, 'image/*');
assert.equal(original.headers.Referer, undefined);
assert.equal(context.__bogImageSource([original])[0].headers.Referer, 'https://bog.ac/');
assert.equal(context.__bogIsImageUrl('https://bog.ac.evil.com/image/test'), false);

// Execute the modified React Native Image module with its native bridge mocked.
const calls = [];
const native = {
  getSize: url => {calls.push(['plain', url]); return Promise.resolve({width: 5, height: 7});},
  getSizeWithHeaders: (url, headers) => {calls.push(['headers', url, headers]); return Promise.resolve({width: 5, height: 7});},
  prefetchImage: (url, id) => {calls.push(['prefetch', url, id]); return Promise.resolve(true);}
};
const dependencies = {
  1: value => value && value.__esModule ? value : {default: value},
  32: (obj, key, value) => {obj[key] = value; return obj;},
  273: value => value,
  274: 'NativeImage',
  130: {forwardRef: fn => fn},
  181: {create: value => value},
  184: {Consumer: 'AnalyticsConsumer'},
  275: {},
  277: {Consumer: 'TextConsumer'},
  172: value => value,
  155: value => value,
  278: native,
  276: 'InlineImage',
  185: {jsx: (type, props) => ({type, props})}
};
let imageModule;
context.__d = (factory, id, ids) => {
  assert.equal(id, 272);
  const module = {exports: {}};
  factory({}, id => dependencies[id], null, null, module, module.exports, ids);
  imageModule = module.exports;
};
const moduleLine = bundle.split('\n').find(line => line.includes('},272,['));
assert(moduleLine);
vm.runInContext(moduleLine, context);
(async () => {
  await imageModule.getSize(image, (width, height) => assert.equal(width * height, 35));
  assert.equal(calls.at(-1)[0], 'headers');
  assert.equal(calls.at(-1)[2].Referer, 'https://bog.ac/');
  await imageModule.getSize(external.uri, () => {});
  assert.equal(calls.at(-1)[0], 'plain');
  await imageModule.prefetch(image);
  assert.equal(calls.at(-1)[0], 'headers');
  let rendered = imageModule({source: original}, null);
  rendered = rendered.props.children(null);
  rendered = rendered.props.children(false);
  assert.equal(rendered.props.headers.Referer, 'https://bog.ac/');
  assert.equal(rendered.props.src[0].uri, image);
  console.log('PASS: forum image render, dimensions, prefetch, header preservation, arrays, local/external asset isolation');
})().catch(error => {console.error(error); process.exitCode = 1;});
