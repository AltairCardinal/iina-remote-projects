#!/usr/bin/env kotlin

/**
 * Standalone Pairing Test Script
 * Run with: kotlin PairingTest.kt
 * Requires: Kotlin compiler + BouncyCastle
 *
 * Or compile and run:
 *   kotlinc -include-runtime -d pairing_test.jar PairingTest.kt
 *   java -jar pairing_test.jar
 */

import java.io.*
import java.net.*
import java.security.*
import java.security.spec.*
import java.util.*
import javax.crypto.*
import javax.crypto.spec.*
import org.bouncycastle.jce.provider.BouncyCastleProvider()
import org.bouncycastle.util.encoders.Base64

// Install BouncyCastle
Security.addProvider(BouncyCastleProvider())

println("=== IINA Remote Pairing Test ===")
println()

// Configuration - EDIT THESE VALUES
var HOST = "192.168.1.100"
var PORT = 8765
var PAIR_CODE = "123456"
var DEVICE_NAME = "Test Device"

fun log(msg: String) {
    println("[LOG] $msg")
}

fun error(msg: String) {
    println("[ERROR] $msg")
}

// Parse command line args
args.forEachIndexed { index, arg ->
    when (arg) {
        "-h" -> HOST = args.getOrElse(index + 1) { HOST }
        "-p" -> PORT = args.getOrElse(index + 1) { "8765" }.toIntOrNull() ?: 8765
        "-c" -> PAIR_CODE = args.getOrElse(index + 1) { "123456" }
        "-n" -> DEVICE_NAME = args.getOrElse(index + 1) { DEVICE_NAME }
        "--help" -> {
            println("Usage: kotlin PairingTest.kt [options]")
            println("Options:")
            println("  -h <host>    Server host (default: $HOST)")
            println("  -p <port>    Server port (default: $PORT)")
            println("  -c <code>    Pair code (default: $PAIR_CODE)")
            println("  -n <name>    Device name (default: $DEVICE_NAME)")
            println()
            println("Example:")
            println("  kotlin PairingTest.kt -h 192.168.1.100 -p 8765 -c ABC123")
            System.exit(0)
        }
    }
}

log("Configuration:")
log("  Host: $HOST:$PORT")
log("  Code: $PAIR_CODE")
log("  Name: $DEVICE_NAME")
println()

// Generate Ed25519 key pair
log("Step 1: Generating Ed25519 key pair...")
val keyGen = KeyPairGenerator.getInstance("Ed25519")
val keyPair = keyGen.generateKeyPair()
val publicKey = keyPair.public
val privateKey = keyPair.private
val publicKeyBytes = publicKey.encoded
val publicKeyB64 = Base64.toBase64String(publicKeyBytes)
log("  Public key (base64): ${publicKeyB64.take(32)}...")
log("  Key generated successfully!")
println()

// Generate device ID
val deviceId = UUID.randomUUID().toString()
log("Step 2: Generated Device ID: $deviceId")
println()

// HTTP request helper
fun httpGet(path: String): String? {
    return try {
        val url = URL("http://$HOST:$PORT$path")
        val conn = url.openConnection() as HttpURLConnection
        conn.requestMethod = "GET"
        conn.connectTimeout = 10000
        conn.readTimeout = 10000
        conn.connect()
        val response = conn.inputStream.bufferedReader().readText()
        log("  GET $path -> ${conn.responseCode}")
        conn.disconnect()
        response
    } catch (e: Exception) {
        error("  GET $path failed: ${e.message}")
        null
    }
}

fun httpPost(path: String, body: String): String? {
    return try {
        val url = URL("http://$HOST:$PORT$path")
        val conn = url.openConnection() as HttpURLConnection
        conn.requestMethod = "POST"
        conn.doOutput = true
        conn.setRequestProperty("Content-Type", "application/json")
        conn.connectTimeout = 10000
        conn.readTimeout = 10000
        conn.outputStream.write(body.toByteArray())
        conn.outputStream.flush()
        val response = if (conn.responseCode < 400) {
            conn.inputStream.bufferedReader().readText()
        } else {
            conn.errorStream?.bufferedReader()?.readText() ?: ""
        }
        log("  POST $path -> ${conn.responseCode}")
        if (conn.responseCode >= 400) {
            log("  Error response: $response")
        }
        conn.disconnect()
        response
    } catch (e: Exception) {
        error("  POST $path failed: ${e.message}")
        null
    }
}

// Get pair challenge
log("Step 3: Getting pair challenge...")
val challengeJson = httpGet("/api/v1/pair/challenge")
if (challengeJson == null) {
    error("Failed to get challenge!")
    System.exit(1)
}
log("  Challenge response: $challengeJson")
println()

// Submit pair code
log("Step 4: Submitting pair code...")
val deviceIdJson = "\"$deviceId\""
val deviceNameJson = "\"$DEVICE_NAME\""
val publicKeyJson = "\"$publicKeyB64\""
val pairRequestJson = """
{
    "code": "$PAIR_CODE",
    "device_id": "$deviceId",
    "device_name": "$DEVICE_NAME",
    "public_key": "$publicKeyB64"
}
""".trimIndent()
log("  Request: $pairRequestJson")
val pairResponseJson = httpPost("/api/v1/pair", pairRequestJson)
if (pairResponseJson == null) {
    error("Failed to submit pair code!")
    System.exit(1)
}
log("  Pair response: $pairResponseJson")
println()

// Parse response
try {
    // Simple JSON parsing without Gson
    val tokenMatch = Regex("""\"token"\s*:\s*"([^"]+)"""").find(pairResponseJson)
    val serverNameMatch = Regex("""\"server_name"\s*:\s*"([^"]+)"""").find(pairResponseJson)
    val expiresInMatch = Regex("""\"expires_in"\s*:\s*(\d+)""").find(pairResponseJson)

    val token = tokenMatch?.groupValues?.get(1)
    val serverName = serverNameMatch?.groupValues?.get(1)
    val expiresIn = expiresInMatch?.groupValues?.get(1)?.toIntOrNull()

    if (token != null) {
        println()
        println("=== PAIRING SUCCESSFUL ===")
        log("  Token: ${token.take(20)}...")
        log("  Server Name: $serverName")
        log("  Expires In: $expiresIn seconds")
    } else {
        println()
        println("=== PAIRING FAILED ===")
        log("  Response: $pairResponseJson")
    }
} catch (e: Exception) {
    error("Failed to parse response: ${e.message}")
}
