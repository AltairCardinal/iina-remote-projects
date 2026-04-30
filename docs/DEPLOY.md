# 交付物清单

## 1. Go Server 二进制
**文件**: `iina-remote-server/iina-remote-server`  
**大小**: 18MB  
**平台**: macOS 通用二进制（Intel + Apple Silicon）  
**依赖**: 无（完全静态链接）  

**运行方式**:
```bash
cd iina-remote-server
./iina-remote-server \
  --port 8765 \
  --pairing-dir ~/Library/ApplicationSupport/IINARemote \
  --iina-url http://localhost:8080
```

**重新编译**（需要 Go 1.21+）:
```bash
chmod +x BUILD.sh
./BUILD.sh
```

## 2. macOS Menu Bar App

需要 Xcode（App Store 免费安装）。

### 构建步骤

1. 安装 Xcode（App Store）
2. 安装 XcodeGen：
   ```bash
   brew install xcodegen
   ```
3. 生成项目：
   ```bash
   cd iina-remote-macos
   xcodegen generate
   ```
4. 编译：
   ```bash
   xcodebuild -project IINARemote.xcodeproj -scheme IINARemote -configuration Debug build
   ```
5. 运行：
   ```bash
   open ~/Library/Developer/Xcode/DerivedData/IINARemote-*/Build/Products/Debug/IINA\ Remote.app
   ```

**提示**: 如果 Go server 二进制不在预期路径，Menu Bar App 会显示"占位模式"（无实际控制功能）。确保先构建 Go server：
```bash
cd ../iina-remote-server && ./BUILD.sh
# 二进制自动复制到 App bundle
```

### 预构建 App（待实现）

如需跳过编译，提供你的 Mac 型号，我可以帮你交叉编译打包成 `.app` 压缩包。

## 3. Android App APK

**文件**: `iina-remote-android/app/build/outputs/apk/debug/app-debug.apk`  
**大小**: 17MB  

安装到手机：
```bash
adb install iina-remote-android/app/build/outputs/apk/debug/app-debug.apk
```

或者直接把 APK 文件传到手机安装（需要允许"未知来源"）。

---

## 一句话总结

| 组件 | 状态 | 下一步 |
|------|------|--------|
| Go Server | ✅ 可用 | `./iina-remote-server` 直接跑 |
| macOS App | ⚠️ 需要 Xcode 编译 | 安装 Xcode 后执行上述步骤 |
| Android App | ✅ APK 已生成 | 传到手机安装 |
