# IINA Remote

从 Android 手机远程控制 Mac 上 [IINA 播放器](https://iina.io) 的完整解决方案。

## 快速预览

[交互原型演示](https://raw.githack.com/AltairCardinal/iina-remote-projects/master/docs/prototype.html) — 无需安装，直接在浏览器中体验完整 UI 交互

---

## 核心功能

- **远程控制** — 播放/暂停、音量调节、进度拖动、播放列表管理
- **文件浏览** — 从手机端浏览并打开 Mac 上的媒体文件
- **配对连接** — 扫码或输入验证码安全配对设备
- **多语言支持** — 中文、English

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
               (内置 Server)
```

- **通信**：HTTP REST API + WebSocket，JWT 认证（7天有效）
- **配对**：首次连接输入 6 位验证码，生成设备 Token
- **发现**：Android 扫描局域网 8765 端口

## 下载预构建版本

无需自行编译，直接下载使用：

| 平台 | 下载 | 说明 |
|------|------|------|
| **macOS** | `IINA-Remote.app.zip` | Menu Bar App，**内置 Go Server**，下载即用 |
| **Android** | `app-debug.apk` | 安装到手机即可 |
| **Server** | `iina-remote-server` | 独立 Server 二进制（跨平台），供无 macOS 用户使用 |

**注意**：macOS App 已包含 Server，无需单独下载 Server。

## 快速开始

### 前置要求

- macOS 13+
- Xcode 15+
- Go 1.21+
- Android Studio / JDK 21
- IINA 播放器

### 构建

#### 调试构建

```bash
# Server
cd server/ && ./BUILD.sh

# macOS
cd ../macos/ && xcodegen generate && xcodebuild -project IINARemote.xcodeproj -scheme IINARemote -configuration Debug build

# Android
cd ../android/ && ./gradlew assembleDebug
```

#### 发布构建

```bash
# 所有平台
./BUILD_RELEASE.sh

# 或分别构建
cd server/ && go build -ldflags "-X main.version=0.8.$(date +%y%m%d%H%M)" -o iina-remote-server .
cd ../macos/ && xcodegen generate && xcodebuild -project IINARemote.xcodeproj -scheme IINARemote -configuration Release build
cd ../android/ && ./gradlew assembleRelease
```

### 配置 IINA IPC

IINA → 设置 → 高级 → 启用 IPC 服务器

或终端运行：
```bash
open -a IINA --args --input-ipc-server=/tmp/iina.sock
```

### 4. 安装 Android App

```bash
# Debug
adb install android/app/build/outputs/apk/debug/app-debug.apk

# Release
adb install android/app/build/outputs/apk/release/app-release.apk
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

## 开发路线图

以下是我们计划的未来功能开发方向：

### 🔄 进行中

| 功能 | 说明 | 状态 |
|------|------|------|
| **网页版遥控端** | 由 Server 提供，扫码即可访问。已实现 Android App 逻辑的 Web 版本，配对流程尚未跑通 | 🔄 开发中 |

### 📋 计划中

| 功能 | 说明 |
|------|------|
| **初次启动配置向导** | 首次启动时引导用户配置：媒体目录选择、界面语言偏好 |
| **多播放器支持** | 扩展支持其他主流播放器（如 VLC、MPV） |
| **Windows 支持** | 开发 Windows 版 Server 与配套工具 |

### ✅ 已完成

- [x] Android 遥控 App
- [x] macOS Menu Bar App
- [x] Go Server 核心服务
- [x] 多语言支持
- [x] 文件浏览与播放控制

---

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
               (Built-in Server)
```

- **Communication**: HTTP REST API + WebSocket, JWT authentication (7 days)
- **Pairing**: 6-digit verification code on first connection
- **Discovery**: Android scans LAN port 8765

## Download Pre-built Binaries

| Platform | Download | Description |
|----------|----------|-------------|
| **macOS** | `IINA-Remote.app.zip` | Menu Bar App with **built-in Go Server** |
| **Android** | `app-debug.apk` | Install on your phone |
| **Server** | `iina-remote-server` | Standalone server binary (cross-platform) for non-macOS users |

**Note**: macOS app already includes the server, no need to download separately.

### Tech Stack

| Platform | Tech |
|----------|------|
| Server | Go 1.21+, gorilla/mux, golang-jwt |
| macOS | Swift 5.9, AppKit, Xcode 15+ |
| Android | Kotlin, Jetpack Compose, Retrofit |
| UI Design | Figma |

### License

This project is open source under [GNU Affero General Public License v3.0](https://opensource.org/licenses/AGPL-3.0).

---

## Roadmap

### 🔄 In Progress

| Feature | Description | Status |
|---------|-------------|--------|
| **Web Remote UI** | Served by Server, accessible via QR code. Android app logic converted to web version, pairing flow not yet working | 🔄 In Progress |

### 📋 Planned

| Feature | Description |
|---------|-------------|
| **Initial Setup Wizard** | First-launch setup: media folder selection, language preference |
| **Multi-Player Support** | Extend support to other mainstream players (VLC, MPV) |
| **Windows Support** | Windows Server and companion tools |

### ✅ Completed

- [x] Android Remote App
- [x] macOS Menu Bar App
- [x] Go Server core service
- [x] Multi-language support
- [x] File browser and playback control
