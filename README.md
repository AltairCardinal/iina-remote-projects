# IINA Remote

从 Android 手机远程控制 Mac 上 [IINA 播放器](https://iina.io) 的完整解决方案。

[Interactive Prototype](https://htmlpreview.github.io/?https://github.com/AltairCardinal/iina-remote-projects/blob/master/figma/index.html) | [English](#english) | [中文](#中文)

---

## 核心功能

- **远程控制** — 播放/暂停、音量调节、进度拖动、播放列表管理
- **文件浏览** — 从手机端浏览并打开 Mac 上的媒体文件
- **配对连接** — 扫码或输入验证码安全配对设备
- **多语言支持** — 中文、English

## 快速预览

点击上方 **Interactive Prototype** 链接，无需安装即可体验完整的 UI 交互（文件浏览、配对流程、播放控制）。

## 项目结构

```
iina-remote-projects/
├── android/          Android 遥控器 App (Kotlin + Jetpack Compose)
├── macos/            macOS Menu Bar App (Swift + AppKit)
├── server/           Go HTTP Server (IINA IPC 通信核心)
├── figma/            UI 设计稿 + 交互原型
└── docs/             技术文档
```

## 技术架构

```
Android App  ←→  Go Server  ←→  IINA (mpv)
  (Kotlin)       (Go :8765)     (:8080 IPC)
                      ↑
              macOS Menu Bar App
               (Swift/ObjC)
```

- **通信**：HTTP REST API + WebSocket，JWT 认证（7天有效）
- **配对**：首次连接输入 6 位验证码，生成设备 Token
- **发现**：Android 扫描局域网 8765 端口

## 快速开始

### 前置要求

- macOS 13+
- Xcode 15+
- Go 1.21+
- Android Studio / JDK 21
- IINA 播放器

### 1. 构建 Go Server

```bash
cd server/
chmod +x BUILD.sh
./BUILD.sh
```

### 2. 构建 macOS Menu Bar App

```bash
cd macos/
xcodegen generate
xcodebuild -project IINARemote.xcodeproj -scheme IINARemote -configuration Debug build
```

### 3. 配置 IINA IPC

IINA → 设置 → 高级 → 启用 IPC 服务器

或终端运行：
```bash
open -a IINA --args --input-ipc-server=/tmp/iina.sock
```

### 4. 安装 Android App

```bash
adb install android/app/build/outputs/apk/debug/app-debug.apk
```

## 文档

| 文档 | 说明 |
|------|------|
| `docs/SPEC.md` | 功能规格说明 |
| `docs/CONTROL_METHODS.md` | IINA 控制方法详解 |
| `server/README.md` | Server API 文档 |
| `android/README.md` | Android 开发指南 |
| `macos/README.md` | macOS 开发指南 |

## 技术栈

| 平台 | 技术 |
|------|------|
| Server | Go 1.21+, gorilla/mux, golang-jwt |
| macOS | Swift 5.9, AppKit, Xcode 15+ |
| Android | Kotlin, Jetpack Compose, Retrofit |
| UI Design | Figma |

## License

本项目采用 [GNU Affero General Public License v3.0](https://opensource.org/licenses/AGPL-3.0) 开源。

---

## English

### IINA Remote

Remote control your [IINA player](https://iina.io) on Mac from your Android phone.

### Features

- **Remote Control** — Play/pause, volume, seek, playlist management
- **File Browser** — Browse and open media files on Mac from your phone
- **Pairing** — Secure device pairing via QR code or 6-digit code
- **i18n** — Chinese, English

### Architecture

```
Android App  ←→  Go Server  ←→  IINA (mpv)
  (Kotlin)       (Go :8765)     (:8080 IPC)
                      ↑
              macOS Menu Bar App
               (Swift/ObjC)
```

### Tech Stack

| Platform | Tech |
|----------|------|
| Server | Go 1.21+, gorilla/mux, golang-jwt |
| macOS | Swift 5.9, AppKit, Xcode 15+ |
| Android | Kotlin, Jetpack Compose, Retrofit |
| UI Design | Figma |

### License

This project is open source under [GNU Affero General Public License v3.0](https://opensource.org/licenses/AGPL-3.0).
