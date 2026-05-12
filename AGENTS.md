# AGENTS.md

## Repo layout

Each top-level dir (`server/`, `macos/`, `android/`, `figma/`) is a **separate git submodule**. Changes inside a submodule must be committed in both the submodule and the parent repo.

## Build order matters

The macOS app's post-build script copies `server/iina-remote-server` into the app bundle. **Build server first**, then macos.

### Debug Build

```bash
# Server (Intel)
cd server && ./BUILD.sh

# macOS (requires XcodeGen + Xcode 15+)
cd ../macos && xcodegen generate && xcodebuild -project IINARemote.xcodeproj -scheme IINARemote -configuration Debug build

# Android (JDK 21, minSdk 26, targetSdk 35)
cd ../android && ./gradlew assembleDebug
```

### Release Build

```bash
# All platforms (from project root)
./BUILD_RELEASE.sh

# Or build individually:
# Server
cd server && go build -ldflags "-X main.version=1.0.0" -o iina-remote-server .

# macOS
cd ../macos && xcodegen generate && xcodebuild -project IINARemote.xcodeproj -scheme IINARemote -configuration Release build

# Android
cd ../android && ./gradlew assembleRelease
```

## Build Version System

All platforms use the same version format: `1.0.0`

### Version generation

| Platform | How | Output |
|----------|-----|--------|
| **Server** | `BUILD.sh` `date +%y%m%d%H%M` | `main.version` variable |
| **macOS** | `preBuildScripts` generates `VersionInfo.swift` | `VersionInfo.marketingVersion` |
| **Android** | Gradle shell `date` command | `versionName` |

### Build verification

After building, verify the version:

```bash
# Server
./iina-remote-server --version

# macOS: check status bar menu → "版本 1.0.0"

# Android: Settings → About → version 1.0.0
```

## Build artifact reporting

Every build must report artifacts without truncation. Rules:

1. **Never use `tail` or output truncation** — report full build output or use `grep` to extract specific lines
2. **Always include `finalizedBy reportBuildInfo`** — Android build uses `finalizedBy` to ensure reporting task runs even on UP-TO-DATE builds
3. **Report must include**:
   - Build version number
   - Artifact path(s) (APK/Binary/App location)

## macOS post-build deployment

The macOS build includes a post-build script that **automatically stops running instances** before deploying:

1. Stops any running `iina-remote-server` process
2. Quits the running `IINA Remote` macOS app
3. Copies the new server binary into the app bundle
4. Ad-hoc codesigns the binary
5. **Copies the entire app bundle to `/Applications/`**

This ensures the new binary can be copied even if the old server is running.

## Go server quirks

- `BUILD.sh` sets `GOPROXY=https://goproxy.cn,direct` and `GOSUMDB=off` (China mirror). Override if needed.
- `BUILD.sh` auto-detects Go via `which go`.
- The binary is ad-hoc codesigned in the macOS post-build script; without this, macOS Hardened Runtime blocks the Go server.
- Server also listens on `port+1` (127.0.0.1 only) for an internal pair-code endpoint.

## No tests or lint exist

There are **zero tests** and no lint/typecheck/CI configs in any sub-project. Run builds to verify.

## TDD workflow (mandatory)

**Any development must follow strict Red-Green TDD:**

1. **Plan first** — before writing any code, plan the complete test flow: what to test, edge cases, test order.
2. **Red** — write a failing test that captures the expected behavior.
3. **Green** — write the minimal code to make the test pass.
4. **Refactor** — clean up while keeping tests green.
5. **Repeat** — incrementally add tests and implementation.

Do not write production code without a corresponding failing test. Do not skip the planning step.

## macOS app specifics

- LSUIElement app (no Dock icon). Uses XcodeGen (`project.yml`) to generate `.xcodeproj`.
- If `.xcodeproj` already exists, `xcodegen generate` will overwrite it.
- `project.yml` includes `MACOSX_DEPLOYMENT_TARGET: "13.0"`, `SWIFT_VERSION: "5.9"`.
- Debug build outputs to `macos/build/Debug/IINA Remote.app`
- Release build outputs to `macos/build/Release/IINA Remote.app`
- After building, copy the app to `/Applications` for daily use:
  ```bash
  # Debug
  cp -r macos/build/Debug/IINA\ Remote.app /Applications/
  # Release
  cp -r macos/build/Release/IINA\ Remote.app /Applications/
  ```

## Android app specifics

- Kotlin, Jetpack Compose, single-activity with Compose Navigation.
- Uses version catalog (`gradle/libs.versions.toml`) for dependencies.
- `compileSdk = 35`, Java 21 compatibility.

## Android Build Troubleshooting

### 正确构建方式

**重要：始终使用 `--no-daemon` 参数**

```bash
cd /Volumes/File/OpenClaw/workspace/iina-remote-projects/android
./gradlew assembleDebug --no-daemon
```

### Gradle Daemon Hang 问题

**症状**：构建在 `dexBuilderDebug`、`mergeExtDexDebug` 或 `mergeDebugGlobalSynthetics` 阶段卡住，CPU 占用 100-200%+ 但 30+ 分钟无进展。

**根因**：Gradle Daemon 进程卡死（可能运行了数小时），后续所有 `./gradlew` 调用都连接到这个卡死的进程，导致全部 hang。

**排查步骤**：

1. 检查是否有残留的 Gradle daemon 进程：
   ```bash
   ps aux | grep -E "gradle|java" | grep -v grep
   ```

2. 如果有长时间运行的 java 进程（数小时），说明 daemon 卡死了

3. 杀掉所有残留进程：
   ```bash
   pkill -9 -f "GradleDaemon"
   pkill -9 -f "kotlin"
   ```

4. 清理 Gradle 缓存和残留文件：
   ```bash
   rm -rf ~/.gradle/caches/8.13
   rm -rf ~/.gradle/daemon
   rm -rf android/.gradle
   rm -rf android/app/.gradle
   rm -rf android/app/build
   ```

5. 确认 `gradle.properties` 中有 `org.gradle.daemon=false`：
   ```properties
   org.gradle.jvmargs=-Xmx4096m -Dfile.encoding=UTF-8
   org.gradle.daemon=false
   org.gradle.parallel=true
   org.gradle.caching=true
   ```

6. 使用 `--no-daemon` 重新构建：
   ```bash
   ./gradlew assembleDebug --no-daemon
   ```

### 环境要求

- **Java**: JDK 21 (需要 JAVA_HOME 指向 `/Users/altair/.jdks/jdk-21.0.10+7/Contents/Home`)
- **Gradle**: 使用项目 wrapper (`./gradlew`)，不要使用系统 Gradle
- **内存**: 4GB heap 适合 Android + Compose 项目

## Key docs to read before editing

| File | Why |
|------|-----|
| `docs/CONTROL_METHODS.md` | Explains IPC socket vs AppleScript dual-control approach |
| `docs/SPEC.md` | Full feature spec |
| `docs/MPV_IPC_REFERENCE.md` | mpv IPC properties and commands (tested working) |
| `server/README.md` | All API endpoints and pairing flow |

## Figma prototype must stay in sync

`figma/index.html` is an interactive HTML prototype. **Whenever Android app interactions change (UI layout, navigation flow, control behavior, screen structure), the same changes must be applied to `figma/index.html`** so the prototype always matches the real app.

## IINA is required at runtime

The Go server talks to IINA via IPC socket at `/tmp/iina.sock`. IINA must be launched with `--input-ipc-server=/tmp/iina.sock` (via command line) or have IPC enabled in IINA → Settings → Advanced.

## mpv IPC important notes

- **Mute**: Use `mute` property, NOT `ao-mute`
- **Playlist navigation**: Only works when playlist has multiple items
- **Delay changes**: Use `add <property> <delta>` for relative changes

## IINA Control Priority Rule

**Any IINA control must use IPC first, AppleScript second.**

When implementing any new IINA control feature:

1. **Always prefer IPC** — IPC is faster, more reliable, and doesn't require IINA to be in foreground
2. **Reference `docs/mpv-ipc-full-spec.md`** for complete IPC command/property specifications
3. **Reference `docs/MPV_IPC_REFERENCE.md`** for quick reference of tested working commands
4. **Only use AppleScript as fallback** when IPC is unavailable

This rule applies to all IINA control code in `server/iina/applescript.go`.

## Bug Investigation Rule

**When debugging bugs, do not rely on any fallback path — the primary path must be fixed.**

1. **Do not assume fallback behavior is acceptable** — a bug in the primary path is still a bug even if a fallback exists
2. **Do not use fallbacks as justification** — "there's a fallback" is not a valid reason to skip fixing the main issue
3. **Trace the full code path** — including all branches (if/else, try/catch, fallback paths)
4. **Fix the root cause** — if a fallback exists because the primary path is broken, fix the primary path

This applies to all bug investigation: IPC vs AppleScript fallback, optimistic update vs polling overwrite, etc.
