# 长期计划
1. android app制作由macOS app搭建的web服务器提供的网页版，这样iOS也能用
2. 主机端添加setup流程
3. ~~添加多语言支持~~ ✅ 已完成
4. ~~添加github的readme.md~~ ✅ 已完成
5. 添加项目文档，用于说明如何使用与如何二次开发
6. 添加对所有主流播放器的支持

# Bug列表
- 无

# 已完成功能

## 多语言支持 (i18n)
- [x] Android: values-en/strings.xml + values/strings.xml
- [x] Android: runtime language switching via LocaleManager
- [x] macOS: zh-Hans.lproj + en.lproj Localizable.strings
- [x] macOS: LocalizedString.swift with runtime switching
- [x] Figma: i18n.js prototype

## IINA 音量条重构
- [x] Split VolumeSliderState into IinaVolumeSliderState and SystemVolumeSliderState
- [x] Fix mute: dragging muted slider to non-zero auto-unmutes
- [x] Fix mute: click unmute sends both mute() and setVolume()

## 其他
- [x] 添加 Mute 字段到 Server Status/FullStatus
- [x] 添加 fullscreen loading dialog when opening files
- [x] Refactor code structure across all subprojects
