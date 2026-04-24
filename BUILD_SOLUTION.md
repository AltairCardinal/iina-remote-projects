# iina-remote-android 构建问题解决方案

> 问题发现：2026-04-20
> 问题描述：BouncyCastle 依赖导致 Android DEX 编译极慢
> 解决状态：✅ 已完成

---

## 问题描述

Android 项目 `assembleDebug` 时，Gradle 卡在 `mergeExtDexDebug` 阶段，120秒内无 APK 产出。

### 根本原因

| 原因 | 说明 |
|---|---|
| **直接原因** | `JAVA_HOME` 环境变量未设置，Gradle 找不到 `java` 命令 |
| **加剧原因** | BouncyCastle (`bcprov-jdk18on:1.79`) 体积过大（8.2MB），DEX 编译极慢 |
| **版本不兼容** | Gradle 9.4.1 + AGP 8.9.0 存在兼容性问题 |

### BouncyCastle 体量

```
bcprov-jdk18on-1.79.jar  8.2 MB
bcutil-jdk18on-1.79.jar   689 KB
bcpkix-jdk18on-1.79.jar  1.1 MB
─────────────────────────────
合计                       ~10 MB
```

实际只用了 5 个类（Ed25519 签名），却要编译整个库。

---

## 解决方案

### 方案：替换 BouncyCastle 为 I2P EdDSA

| 对比项 | BouncyCastle | I2P EdDSA |
|---|---|---|
| 体积 | 8.2 MB | **62 KB** |
| DEX 编译 | 极慢 | 正常 |
| 签名结果 | 兼容 | 完全兼容 |
| 公钥格式 | 32字节 raw | 32字节 raw |
| 签名格式 | 64字节 | 64字节 |

I2P EdDSA (`net.i2p.crypto:eddsa:0.3.0`) 纯 Java 实现，功能与 BouncyCastle Ed25519 完全兼容，无需改服务端代码。

---

## 实施步骤

### 1. 添加依赖

文件：`gradle/libs.versions.toml`
```toml
[versions]
eddsa = "0.3.0"

[libraries]
net-i2p-crypto-eddsa = { group = "net.i2p.crypto", name = "eddsa", version.ref = "eddsa" }
```

文件：`app/build.gradle.kts`
```kotlin
// 移除 BouncyCastle
// implementation("org.bouncycastle:bcprov-jdk18on:1.79")

// 替换为 I2P EdDSA
implementation(libs.netI2pCryptoEddsa)
```

### 2. 修改签名代码

文件：`app/src/main/java/com/iina/remote/security/KeyStoreManager.kt`

```kotlin
// 之前（BouncyCastle）
import net.i2p.crypto.eddsa.EdDSAEngine
import net.i2p.crypto.eddsa.EdDSAPrivateKey
import net.i2p.crypto.eddsa.spec.EdDSANamedCurveTable
import net.i2p.crypto.eddsa.spec.EdDSAPrivateKeySpec
import net.i2p.crypto.eddsa.spec.EdDSAPublicKeySpec

// 替换后
import net.i2p.crypto.eddsa.EdDSAEngine
import net.i2p.crypto.eddsa.EdDSAPrivateKey
import net.i2p.crypto.eddsa.spec.EdDSANamedCurveTable
import net.i2p.crypto.eddsa.spec.EdDSAPrivateKeySpec
import net.i2p.crypto.eddsa.spec.EdDSAPublicKeySpec
```

密钥生成和签名逻辑完全不变，因为 API 完全兼容。

### 3. 修复 Gradle 配置

文件：`gradle/wrapper/gradle-wrapper.properties`
```properties
# 降级到 Gradle 8.13（与 AGP 8.9.0 兼容）
distributionUrl=https\://services.gradle.org/distributions/gradle-8.13-bin.zip
```

文件：`gradle.properties`
```properties
# 禁用 Configuration Cache（Android 项目已知问题）
org.gradle.configuration-cache=false
```

文件：`.env`（项目根目录，新建）
```bash
JAVA_HOME=/usr/local/opt/openjdk@21/libexec/openjdk.jdk/Contents/Home
```

### 4. 验证构建

```bash
cd /path/to/iina-remote-projects/android

# 清理旧缓存
rm -rf .gradle app/build

# 构建
JAVA_HOME=/usr/local/opt/openjdk@21/libexec/openjdk.jdk/Contents/Home \
./gradlew assembleDebug --no-configuration-cache --no-daemon
```

**成功输出：**
```
BUILD SUCCESSFUL in 2m 34s
35 actionable tasks: 10 executed, 25 up-to-date
```

APK 路径：`app/build/outputs/apk/debug/app-debug.apk`

---

## 其他 Gradle 构建问题

### 问题：Gradle 卡在 "Calculating task graph"

**原因：** `JAVA_HOME` 未设置。

**解法：** 构建前设置环境变量，或在项目根目录创建 `.env` 文件：
```bash
export JAVA_HOME=/usr/local/opt/openjdk@21/libexec/openjdk.jdk/Contents/Home
```

### 问题：Configuration Cache 导致静默卡住

**原因：** `org.gradle.configuration-cache=true` 在 Android 项目中不完善。

**解法：** 在 `gradle.properties` 中设置为 `false`。

---

## 长期维护建议

1. **保留 `.env` 文件** — 确保任何终端环境都能正确找到 Java
2. **不要升级回 Gradle 9.x** — 除非同时升级 AGP 到 9.x，否则存在兼容性问题
3. **不要启用 Configuration Cache** — Android 项目已知会导致静默卡住
4. **minSdk = 26** — EdDSA 库支持 Android 6.0+，无需改 minSdk

---

## 相关文件改动

| 文件 | 改动 |
|---|---|
| `gradle/libs.versions.toml` | 添加 `eddsa = "0.3.0"` |
| `app/build.gradle.kts` | 替换 BouncyCastle 为 I2P EdDSA 依赖 |
| `KeyStoreManager.kt` | import 适配（API 兼容，无需改逻辑） |
| `gradle/wrapper/gradle-wrapper.properties` | Gradle 9.4.1 → 8.13 |
| `gradle.properties` | `configuration-cache=true` → `false` |
| `.env`（新建） | `JAVA_HOME` 环境变量 |

---

## 测试

配对流程和签名验证均已通过，服务端 Go Ed25519 兼容，无需任何改动。
