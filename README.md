# 粉岛图片兼容修复版（非官方）

基于 [tiamed/bog-nimingban](https://github.com/tiamed/bog-nimingban) 的粉岛 1.2.0，由用户在 GPT 协助下排查、修改。感谢原作者开发和开源粉岛。

**这不是原作者发布的版本，也未获得原作者背书。** 已向原项目提交问题反馈，尚不确定作者是否已阅读；是否发布官方更新以原项目为准。本仓库提供临时修复的脚本与说明。

## 下载安装

前往本仓库的 [Releases](https://github.com/btb-bulbul/bog-nimingban-imagefix/releases/latest)，在 Assets 中下载 `bog-nimingban-v1.2.0-imagefix-coexist.apk`。无需网盘会员；访问速度取决于网络。

- 修复版与原版共存安装，**不要为了安装它卸载原版**。
- 两个版本的数据、饼干和个性化设置不互通。原版内置备份仅包含部分数据，不包含完整偏好设置。
- 两个版本目前名称和图标相同，请通过 Android 应用信息的包名区分：原版 `fun.tiamed`，修复版 `fun.tiamfx`。
- 修复版使用独立签名；后续使用同一修复版签名更新可保留修复版数据，不能直接覆盖原版。

## 修复内容

论坛近期调整图片请求策略后，旧客户端图片请求返回 403。请求对比发现：图片请求需要论坛 Referer，默认 `okhttp/4.9.2` User-Agent 即使带 Referer 也返回 403。

本修复版：

1. 仅对论坛图片请求补充 `Referer: https://bog.ac/` 和 `User-Agent: BOG-nimingban/1.2.0 (Android; ImageFix)`。
2. 覆盖 React Native 图片显示、尺寸获取、预加载，以及 Expo 文件下载和缓存下载路径。
3. 将 1.2.0 安装包的 API 基址由 HTTP 改为 HTTPS，与作者仓库最新源码保持一致。
4. 停用原项目 OTA 更新，避免远程旧代码覆盖本地修复。
5. 调整包名、Provider authorities 和资源包命名空间以支持共存；保留原有业务类名。

没有新增广告、统计、额外的数据上传或代理服务器。原有应用功能与原有联网行为仍然存在。

## 验证及边界

- 已在一台 OPPO PFEM10 / Android 16 手机上确认帖子列表、缩略图及点开后的大图正常显示。
- 已运行 JavaScript 语法与图片桥接模拟测试，并验证 APK 签名、ZIP 完整性及对齐。
- 保存、分享、长图浏览及其他 Android 版本尚未完整实机验证；本版本不保证解决所有问题。
- 论坛以后更改接口或规则，仍可能影响可用性。正常浏览请遵守论坛规则。

初次发布 APK 的 SHA-256：

```text
44bcad33912cec624ce2785867b2e480570949a1ac4318ed4ec88dbe563ef7c1
```

## 修改脚本

仓库保存实际修改脚本，不包含作者原始 APK、私钥或个人数据。原始完整源码请见上游仓库。本次交付是对 1.2.0 安装包内的 JavaScript bundle 和 Android 元数据进行修补，并非声称从上游源码完成全量重编译。

Windows 上复现需要 Python 3、Node.js、JDK 的 Java/keytool，以及 Android SDK Build Tools 35.0.0。将原始 `bog-nimingban-v1.2.0.apk` 放在本仓库目录的上一级。默认 SDK 路径为 `%USERPROFILE%/AppData/Local/Android/Sdk`。

```powershell
python build_patch.py --coexist
node verify_patch.js
```

脚本在本地生成新的签名密钥；自行生成的密钥与本仓库已发布安装包的密钥不同，因此自行构建的 APK 不能直接覆盖本仓库发布版。不要上传本地生成的密钥。

## 许可与来源

原项目 Copyright (c) 2022 tiamed，采用 MIT 许可，完整文本见 [LICENSE](LICENSE)。本仓库新增的修改脚本同样按 MIT 许可提供。

发布的 APK 内保留原来的关于页面和项目相关内容，并附有：

- `assets/BOG-ORIGINAL-LICENSE.txt`：原作者版权声明与完整 MIT 许可。
- `assets/BOG-IMAGEFIX-NOTICE.txt`：非官方性质及修改说明。
