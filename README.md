# IINA Remote Projects

从 Android 手机远程控制 Mac 上 IINA 播放器的完整项目集合。

## 子项目总览

| 目录 | 项目 | 语言 | 说明 |
|------|------|------|------|
| `macos/` | macOS Menu Bar App | Swift | 菜单栏小工具，负责启动 Go Server、配对码显示 |
| `android/` | Android 遥控器 App | Kotlin | Android 端 UI，扫描、配对、遥控播放器 |
| `server/` | Go HTTP Server | Go | 核心逻辑，IINA IPC 通信、配对认证 |
| `figma/` | UI 设计稿 | Sketch/Figma | 界面设计源文件 |

## 整体架构

```
Android App  ←→  Go Server  ←→  IINA (mpv)
 (Kotlin)        (Go :8765)     (:8080 IPC)
                      ↑
              macOS Menu Bar App
               (Swift/ObjC)
```

- **通信**：HTTP REST API，JWT 认证（7天有效）
- **配对**：首次连接输入 6 位验证码，生成设备 Token
- **发现**：Android 扫描局域网 8765 端口

## 快速开始

### 1. 构建 Go Server

```bash
cd server/
chmod +x BUILD.sh
./BUILD.sh
# 产物: iina-remote-server（通用二进制，Intel + Apple Silicon）
```

### 2. 启动 macOS Menu Bar App

```bash
cd macos/
xcodegen generate
xcodebuild -project IINARemote.xcodeproj -scheme IINARemote -configuration Debug build
# App 安装在 ~/Library/Developer/Xcode/DerivedData/
```

### 3. 确保 IINA 开启 IPC

IINA → 设置 → 高级 → 启用 IPC 服务器

或在终端运行：
```bash
open -a IINA --args --input-ipc-server
```

### 4. 安装 Android App

```bash
adb install android/app/build/outputs/apk/debug/app-debug.apk
```

## 核心文档位置

- **总览** → `README.md`（本文件）
- **总体设计** → `docs/SPEC.md`
- **API 文档** → `server/README.md`
- **macOS 开发** → `macos/README.md`
- **Android 开发** → `android/README.md`
- **UI 设计** → `figma/README.md`
- **进度记录** → `docs/PROGRESS.md`
- **实施计划** → `docs/IMPLEMENTATION_PLAN.md`
- **IINA 控制方法** → `docs/CONTROL_METHODS.md`

## 技术栈

- **Server**: Go 1.21+，gorilla/mux，golang-jwt
- **macOS**: Swift 5.9，AppKit，Xcode 15+
- **Android**: Kotlin，Jetpack Compose，Retrofit，OkHttp
- **设计**: Sketch / Figma

## 相关文档（原始目录）

原始开发文档散落在各子项目中，接收项目后请先阅读：

1. `android/SPEC.md` — 功能规格
2. `android/CONTROL_METHODS.md` — IINA 控制方法
3. `android/IMPLEMENTATION_PLAN.md` — 实施计划
4. `android/PROGRESS.md` — 进度记录
5. `android/ROADMAP.md` — 路线图
6. `server/README.md` — Server 部署和 API 说明
