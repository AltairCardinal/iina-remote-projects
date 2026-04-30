# System Architecture

## Overview

The IINA Remote system is a three-layer architecture enabling remote control of the IINA media player from Android devices.

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Android App                                   │
│                    (IINA Remote Client)                              │
└─────────────────────────────────────────────────────────────────────┘
                               │
                               │ HTTP / Bonjour Discovery
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        macOS App                                     │
│              (Menu Bar App + Go Server Host)                         │
│                                                                      │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────────┐ │
│  │ HTTPServer  │    │   IINA      │    │   PairingManager         │ │
│  │ Manager     │    │ Lifecycle   │    │   (DeviceTokenStore)     │ │
│  └─────────────┘    │ Manager     │    └─────────────────────────┘ │
│                      └─────────────┘                                 │
└─────────────────────────────────────────────────────────────────────┘
                               │
                               │ IPC Socket (/tmp/iina.sock)
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        IINA Player                                   │
│                    (mpv-based media player)                          │
└─────────────────────────────────────────────────────────────────────┘
```

## Three-Layer Architecture

### Layer 1: Android App (Client)

The Android application serves as the remote control interface. It discovers available servers via Bonjour/mDNS, handles device pairing, and sends playback control commands.

**Key Components:**
- `IinaRepository` - State management via StateFlows, API communication
- `PairingViewModel` - Handles device pairing flow and pair code display
- `MainScreen` - Primary UI composable with playback controls
- `BonjourDiscovery` - Network service discovery for finding servers

### Layer 2: macOS App + Go Server (Bridge)

The macOS application hosts the Go server and manages IINA lifecycle. It acts as a bridge between Android clients and the local IINA instance.

**Key Components:**

| Component | Responsibility |
|-----------|----------------|
| `StatusBarController` | Menu bar UI, server status display |
| `HTTPServerManager` | Manages Go server process lifecycle |
| `IINALifecycleManager` | Launches and monitors IINA player |
| `PairingManager` | Device authentication, JWT token management |
| `DeviceTokenStore` | Persistent storage for paired device credentials |

### Layer 3: IINA Player (Execution)

IINA is the actual media player that receives commands via IPC socket and executes playback operations.

**Interface:** `/tmp/iina.sock` (Unix domain socket)

## Communication Flows

### Pairing Flow

```
Android                          macOS/Go Server                       IINA
  │                                    │                                  │
  │──── Bonjour Discovery ────────────▶│                                  │
  │◀──── Server Info (port, name) ─────│                                  │
  │                                    │                                  │
  │──── Request Pair Code ─────────────▶│                                  │
  │◀──── Pair Code Display ────────────│                                  │
  │                                    │                                  │
  │  [User enters code on macOS]        │                                  │
  │                                    │                                  │
  │──── Validate Pairing ──────────────▶│──── IPC: verify ───────────────▶│
  │                                    │◀─── Response ────────────────────│
  │◀──── JWT Token ─────────────────────│                                  │
  │                                    │                                  │
```

**Steps:**
1. Android scans for server via Bonjour ( `_iinarc._tcp` )
2. Server generates time-limited pair code
3. Android displays pair code to user
4. User enters code on macOS menu bar app
5. Server validates code via IINA IPC
6. Server issues JWT token to Android
7. All subsequent requests include JWT for authentication

### Playback Control Flow

```
Android          Go Server           IINA
   │                │                 │
   │── HTTP POST ───▶│                 │
   │   (with JWT)    │                 │
   │                │── IPC Command ─▶│
   │                │◀── Response ─────│
   │◀── HTTP OK ────│                 │
   │                │                 │
```

**Steps:**
1. Android sends HTTP request with JWT authorization header
2. Go server validates JWT token
3. Go server sends IPC command to IINA via `/tmp/iina.sock`
4. IINA executes command and responds via IPC
5. Go server formats response and returns to Android
6. Android updates UI via StateFlow

## Data Flow

### Authentication Data

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Android    │────▶│   Go Server  │────▶│ DeviceToken  │
│   Client     │     │   (JWT)      │     │   Store      │
└──────────────┘     └──────────────┘     └──────────────┘
     │                      │
     │  JWT Token           │  bcrypt hash
     │  (in Authorization  │  (stored securely
     │   header)           │   in Keychain)
     ▼                      ▼
```

### Playback State

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   IINA       │────▶│   Go Server  │────▶│   Android    │
│   (mpv)      │     │   (state     │     │   (StateFlow │
│              │     │    mirror)   │     │    update)   │
└──────────────┘     └──────────────┘     └──────────────┘
     │                      │
     │  IPC observe         │  Polling
     │  (property change)   │  (1s interval)
     ▼                      ▼
```

## Network Architecture

### Ports

| Service | Port | Protocol | Purpose |
|---------|------|----------|---------|
| HTTP Server | 7192 | TCP | Main API endpoint |
| Pair Code | 7193 | TCP | Internal pairing verification |
| Bonjour | 7192 | mDNS | Service discovery |

### Security

- **JWT Authentication**: All API requests (except pairing) require valid JWT
- **Pair Code**: Time-limited (60 seconds), single-use
- **Device Tokens**: Stored in macOS Keychain, never transmitted in plain text
- **Local Only**: Server binds to `127.0.0.1` (not exposed to network)

## Component Interactions

### State Synchronization

The Go server maintains an in-memory mirror of IINA's playback state, updated via:

1. **IPC Observation** - Subscribe to property changes on IINA socket
2. **Polling** - Periodic `get_property` calls for critical state
3. **Event Push** - IINA notifies on certain state changes

### Error Handling

| Error Type | Handling |
|------------|----------|
| IINA not running | Auto-launch via `IINALifecycleManager` |
| IPC socket missing | Retry with exponential backoff |
| JWT expired | Return 401, Android re-pairs |
| Network timeout | Android retries with backoff |

## Platform-Specific Details

### macOS
- Menu bar app (LSUIElement, no Dock icon)
- Go server runs as child process
- IINA managed via LaunchAgent pattern
- Keychain for secure token storage

### Android
- Jetpack Compose UI
- Hilt for dependency injection
- StateFlow for reactive state
- Retrofit for HTTP communication
