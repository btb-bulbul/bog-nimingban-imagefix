# 粉岛图片兼容修复版（非官方）

基于 [tiamed/bog-nimingban](https://github.com/tiamed/bog-nimingban) 的粉岛 1.2.0，由 GPT 排查、修改，修复了近期粉岛APP无法查看图片的问题。感谢原作者开发和开源粉岛。

已向原项目提交问题反馈。本仓库提供临时修复的脚本与说明。

## 下载安装

前往本仓库的 [Releases](https://github.com/btb-bulbul/bog-nimingban-imagefix/releases/latest)，在 Assets 中下载 `bog-nimingban-v1.2.0-imagefix-coexist.apk`。

- 修复版与原版共存安装，两个版本的数据、饼干和个性化设置不互通。**不建议为了安装它卸载原版**。

<details>
<summary>修改脚本与本地复现</summary>

## 修复内容

论坛近期调整图片请求策略后，旧客户端图片请求返回 403。请求对比发现：图片请求需要论坛 Referer，默认 `okhttp/4.9.2` User-Agent 即使带 Referer 也返回 403。

本修复版：

1. 仅对论坛图片请求补充 `Referer: https://bog.ac/` 和 `User-Agent: BOG-nimingban/1.2.0 (Android; ImageFix)`。
2. 覆盖 React Native 图片显示、尺寸获取、预加载，以及 Expo 文件下载和缓存下载路径。
3. 将 1.2.0 安装包的 API 基址由 HTTP 改为 HTTPS，与作者仓库最新源码保持一致。
4. 停用原项目 OTA 更新，避免远程旧代码覆盖本地修复。
5. 调整包名、Provider authorities 和资源包命名空间以支持共存；保留原有业务类名。

## 验证及边界

- 已在一台 OPPO PFEM10 / Android 16 手机上确认帖子列表、缩略图及点开后的大图正常显示。
- 已运行 JavaScript 语法与图片桥接模拟测试，并验证 APK 签名、ZIP 完整性及对齐。
- 保存、分享、长图浏览及其他 Android 版本尚未完整实机验证。

## 修改脚本

仓库保存实际修改脚本，原始完整源码请见上游仓库。本次交付是对 1.2.0 安装包内的 JavaScript bundle 和 Android 元数据进行修补。

Windows 上复现需要 Python 3、Node.js、JDK 的 Java/keytool，以及 Android SDK Build Tools 35.0.0。将原始 `bog-nimingban-v1.2.0.apk` 放在本仓库目录的上一级。默认 SDK 路径为 `%USERPROFILE%/AppData/Local/Android/Sdk`。

```powershell
python build_patch.py --coexist
node verify_patch.js
```

脚本在本地生成新的签名密钥；自行生成的密钥与本仓库已发布安装包的密钥不同，因此自行构建的 APK 不能直接覆盖本仓库发布版。

</details>

## 许可与来源

原项目 Copyright (c) 2022 tiamed，采用 MIT 许可，完整文本见 [LICENSE](LICENSE)。本仓库新增的修改脚本同样按 MIT 许可提供。

发布的 APK 内保留原来的关于页面和项目相关内容，并附有：

- `assets/BOG-ORIGINAL-LICENSE.txt`：原作者版权声明与完整 MIT 许可。
- `assets/BOG-IMAGEFIX-NOTICE.txt`：非官方性质及修改说明。
