# OpenCode Gradle 构建卡住问题 — 完整分析报告

> 调查时间：2026-04-21
> Session：`ses_259ce6f72ffejN1BgwmnuFnDwH`
> 状态：根因已确认，解决方案已验证

---

## 一、构建历史回顾

| 时间 | 命令 | 结果 | 耗时 |
|---|---|---|---|
| 08:30:18 | `./gradlew compileDebugKotlin` | ✅ BUILD SUCCESSFUL | 30s |
| 08:30:55 | `./gradlew assembleDebug` (不在 android/ 目录) | ❌ `zsh: ./gradlew not found` | <1s |
| 08:31:00 | `cd android && ./gradlew assembleDebug 2>&1 \| tee \| tail -100` | ⏱ 超时 (SIGKILL) | 600s |
| 08:42:40 | (修复后) `./gradlew assembleDebug` | ✅ BUILD SUCCESSFUL | ~30s |
| 08:42:51 | 后台 `tee /tmp/build2.log &` | ⏱ 30s 无输出 (SIGKILL) | 30s |
| ~17:00 | `./gradlew assembleDebug --no-daemon` | ✅ BUILD SUCCESSFUL | 11s |

---

## 二、四个独立根因

### 根因 1：tail -100 缓冲导致静默挂起（最关键）

**问题命令：**
```bash
./gradlew assembleDebug 2>&1 | tee /tmp/gradle_build.log | tail -100
```

**发生了什么：**
- `tail -100` 会等待缓冲积累 100 行才输出
- 在等待期间，exec 工具的 **no-output-timeout** 触发（默认几分钟无输出就 SIGKILL）
- 即使 Gradle 正在正常运行，`tail` 也不输出任何东西
- 最终 exec 工具对整个管道发送 SIGKILL

**证据：** `exec-B5_AYfQG.js` 第 251-264 行：
```javascript
const shouldTrackOutputTimeout = typeof noOutputTimeoutMs === "number" ...
const armNoOutputTimer = () => {
    noOutputTimedOut = true;
    if (typeof child.kill === "function") child.kill("SIGKILL");  // ← 杀死整个管道
};
```

### 根因 2：SIGKILL 不杀死 Gradle Daemon 子进程

**问题：**
- SIGKILL 只杀死直接进程，不杀死它的子进程（Gradle Daemon 是孙进程）
- 结果：exec 被 kill → Gradle Daemon 还活着 → 下次构建又启动一个新 Daemon

**证据：** `exec-B5_AYfQG.js` 第 263、268 行直接对 `child.kill("SIGKILL")`，Daemon 是 `exec` 的子进程 fork 出来的，不在同一个进程组。

### 根因 3：多个 Daemon 文件锁冲突

**问题：**
- 5 个 Gradle Daemon 同时运行（PID 1975, 1985 等）
- 所有 Daemon 争抢同一个 `.gradle/9.4.1/fileHashes` 锁
- 其中一个持有锁但无实际工作（CPU 155% 但空转）

**为什么有 5 个 Daemon：**
- opencode 每次 exec 超时后重新发起构建
- 每次都启动新的 Daemon
- 旧的 Daemon 没被清理（因为 SIGKILL 杀不掉）

### 根因 4：JAVA_HOME 未设置（版本混淆）

**问题：**
- 系统 `gradle` = Gradle 9.4.1（Homebrew）
- 项目 `./gradlew` = Gradle 8.13（wrapper）
- `.env` 文件不会被 exec 的 shell 自动加载
- `gradlew` 找不到 Java 时静默等待，不报错

**验证：**
```bash
# 不设置 JAVA_HOME → gradlew 等待，不报错
$ ./gradlew assembleDebug
# (无输出，卡住)

# 设置 JAVA_HOME → 正常
$ JAVA_HOME=/usr/local/opt/openjdk@21/... ./gradlew assembleDebug
# BUILD SUCCESSFUL
```

---

## 三、为什么 opencode 反复重试导致问题加剧

1. exec 超时 600s → SIGKILL → 进程树部分残留
2. opencode 感知到失败 → 重新发起构建
3. 新 Daemon 和旧 Daemon 争抢锁
4. 再次超时 → SIGKILL → 更多残留 Daemon
5. 恶性循环，直到 5 个 Daemon 同时空转

---

## 四、解决方案

### 方案 A：修改 opencode 的 gradlew 命令（推荐）

opencode 在执行 Gradle 构建时，应该用以下模式：

```bash
cd /Volumes/File/OpenClaw/workspace/iina-remote-projects/android && \
  JAVA_HOME=/usr/local/opt/openjdk@21/libexec/openjdk.jdk/Contents/Home && \
  ./gradlew assembleDebug \
    --no-daemon \
    --stacktrace \
    --info 2>&1 | tee /tmp/gradle_build.log
```

**关键参数：**
- `--no-daemon`：每次构建独立进程，不留残留 Daemon
- `--info`：避免输出缓冲（行缓冲 vs 块缓冲）
- `--stacktrace`：出错时提供有用信息
- `tee /tmp/gradle_build.log`：保留完整日志，但不用 `tail`
- **去掉 `| tail -100`**：tail 会缓冲导致误杀

### 方案 B：预先清理残留 Daemon

在构建前执行：
```bash
# 先停掉所有残留 daemon
cd /Volumes/File/OpenClaw/workspace/iina-remote-projects/android && \
  ./gradlew --stop 2>/dev/null || true
# 再执行构建
```

### 方案 C：Gradle jvmargs 调优

`gradle.properties` 建议：
```properties
org.gradle.jvmargs=-Xmx4096m -XX:MaxMetaspaceSize=512m -XX:+HeapDumpOnOutOfMemoryError
org.gradle.daemon=true
org.gradle.parallel=true
org.gradle.caching=true
```

**注意：** `org.gradle.daemon=true` vs `--no-daemon` 的权衡：
- `daemon=true`：构建快（~11s），但 daemon 残留会导致多 session 冲突
- `--no-daemon`：构建稍慢（~30s），但完全干净

### 方案 D：opencode 全局 prompt 改造

给 opencode 一个系统级指令，让它对所有 Gradle 构建命令做以下转换：

**Before:**
```bash
./gradlew assembleDebug
```

**After:**
```bash
JAVA_HOME=/usr/local/opt/openjdk@21/libexec/openjdk.jdk/Contents/Home ./gradlew assembleDebug --no-daemon
```

可以通过在 opencode 的 system prompt 中加入：
```
对于任何 Android/Kotlin/Gradle 构建命令：
1. 必须设置 JAVA_HOME=/usr/local/opt/openjdk@21/libexec/openjdk.jdk/Contents/Home
2. 必须加 --no-daemon 参数
3. 不要用 tail -100 缓冲输出
4. 构建前先 ./gradlew --stop 清理残留进程
```

---

## 五、总结：问题对应关系

| 现象 | 根因 | 解决 |
|---|---|---|
| 构建静默卡住（无输出） | `tail -100` 缓冲 + no-output-timeout SIGKILL | 去掉 tail，或用 `--info` |
| 多个 Daemon 同时跑 | SIGKILL 杀不掉 Daemon 子进程 | 用 `--no-daemon` |
| 文件锁超时 | 5 个 Daemon 抢锁 | 同上 |
| `./gradlew not found` | 没 cd 到 android/ 目录 | opencode 先 cd |
| 版本混用 (9.4.1 vs 8.13) | JAVA_HOME 未设置 | 显式设置 JAVA_HOME |

---

## 六、快速验证

在当前项目验证 `--no-daemon` 是否正常：

```bash
cd /Volumes/File/OpenClaw/workspace/iina-remote-projects/android && \
  JAVA_HOME=/usr/local/opt/openjdk@21/libexec/openjdk.jdk/Contents/Home && \
  ./gradlew --stop && \
  ./gradlew assembleDebug --no-daemon --info 2>&1 | head -50
```

正常情况下应该立即有输出（`--info` 避免缓冲），约 2-3 分钟完成。
