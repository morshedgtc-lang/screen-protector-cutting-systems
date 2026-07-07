# Screen Protector Cutting Machine — Project Context

## Project Goal
Reverse-engineer the MTB-CUT 180T/M180T screen protector cutting machine's cloud API + PrinterServer protocol to enable **fully local** print/cut control without cloud dependency.

## Target Device
- **Model:** MTB-CUT 180T / M180T (branded Mietubl, manufactured by Huansheng Intelligence, Shenzhen)
- **OS:** Android, kiosk-mode, build `QM1.171019.026.20201202-190618`
- **SoC:** Allwinner/Rockchip
- **Display:** 5.5" touchscreen, WiFi 2.4G
- **IP:** `192.168.0.104` (static)
- **PC IP:** `192.168.0.100`
- **Ports:** Zero open ports (outbound connections only)
- **USB-B:** Enumerates as HID mouse only (VID_18F8/PID_0F97) — no ADB, no serial
- **Kiosk:** No settings, no notification bar, long-press/build-number taps blocked

## Architecture

```
User's Phone/PC Browser
        │
        ▼  (HTTP)
┌──────────────────┐     proxies to      ┌─────────────────────┐
│  PrinterServer   │ ──────────────────►  │ api.hsyunqiemo.com  │
│  (Flask, port 5000)│     (cloud API)    │  (Huansheng Cloud)  │
│  Windows EXE     │                     └─────────────────────┘
└────────┬─────────┘
         │ serial/COM (38400 baud default)
         ▼
┌──────────────────┐
│  Cutting Machine │  (outbound HTTP to cloud or PrinterServer)
│  192.168.0.104   │
└──────────────────┘
```

## PrinterServer (`CutterPrinter_V1.6\PrinterServer.exe`)
- **Location:** `D:\workspase\screen-protector cutting systems\PrinterServer\CutterPrinter_V1.6\`
- **Compiled Python Flask app** (source `.pyc`/extracted)
- **Web UI Endpoints:**
  - `/login` — admin panel (credentials: admin / 123456)
  - `/photo/phone` — phone model selection & print design (canvas editor with rotate/zoom/text)
  - `/photo/print_page` — custom image print design (upload image or pick from online gallery)
  - `/manage` — job management, print mode selector (Auto/Manual), password change
  - `/plt/upload` — direct PLT file upload to machine via serial/COM
  - `/photo/print` (POST) — submit print job (base64 PNG)
  - `/api/phone/*` — proxy endpoints to cloud API
- **Cloud API proxied:** `https://api.hsyunqiemo.com` (classifylist, brandlist, modellist, pltfile)
- **PLT file storage:** `https://cloudcutter.oss-accelerate.aliyuncs.com` (Alibaba Cloud OSS)
- **PLT encryption:** DES-CBC-PKCS7 (key unknown)
- **Database:** `db\printer.db` (SQLite)
  - `tab_user` — admin/123456
  - `tab_plt` — print jobs (base64 PNG images)
  - `tab_phone` — phone model catalog (synced from cloud)
  - `tab_mode` — print mode (1=Auto)
  - `tab_config` — language (1=English)
  - `activate` — registration status (1=activated)
- **Serial/COM:** COM1, baud 38400 (configurable 9600–115200)

## Key Findings
1. Machine initiates **all** connections — no open ports, can't connect TO it
2. PrinterServer is already **activated** and was **previously used** (historical print jobs in DB)
3. Machine app has a **Server IP setting** — user entered `192.168.0.104` (machine's own IP), should be `192.168.0.100` to use local PrinterServer
4. Standard workflow: Customer scans QR → opens web design page → designs screen protector → submits → PrinterServer cuts via serial

## Critical Next Step
Find and change the **Server IP / DIY Mode** setting in the machine's Android app to point to `192.168.0.100:5000` instead of the cloud API. Look in:
- App settings / configuration menu
- Network / server configuration
- Any "DIY", "Local", or "Server" mode option
- Hidden menus (long-press, multi-tap, gesture patterns)

## Bypass Stack (built)

The cloud is no longer needed. A complete local impersonation stack runs on the PC:

```
Machine (192.168.0.104)
  │  DNS query for api.hsyunqiemo.com
  │  or cloudcutter.oss-accelerate.aliyuncs.com
  ▼
┌──────────────────────┐  (or ARP-spoofed traffic)
│  dns_hijack.py       │  UDP/53 — intercepts both cloud domains,
│  (run as ADMIN)      │  answers with 192.168.0.100
└──────┬───────────────┘
       │  HTTPS GET/POST to api.hsyunqiemo.com
       ▼
┌──────────────────────┐
│  fakeapi.py          │  Flask HTTPS — serves all cloud API
│  (Flask, port 5000)  │  endpoints + PLT files via DES-CBC.
│                      │  Returns "never-expired" user record.
│  Routes:             │
│  /api/datalist/user  │  ← user/expiration (key endpoint)
│  /api/datalist/cat.. │  ← category list
│  /api/datalist/brand │  ← brand list
│  /api/datalist/series│  ← series list
│  /api/datalist/model │  ← model list (with PLT filename)
│  /api/phone/*        │  ← PrinterServer API compat
│  /api/phone/pltfile  │  ← PLT download URL
│  /model/<filename>   │  ← DES-encrypted PLT file
│  /api/cutterMacTest  │  ← machine MAC test endpoint
└──────────────────────┘

Optional: arp_spoof.py — tells the machine we're the gateway,
routes all traffic through our NIC for interception.
```

### How to run the bypass stack

```bash
# Terminal 1 — HTTPS fake API (port 5000)
C:\Python314\python.exe fakeapi.py
# Or with logging: run_fakeapi_logged.bat

# Terminal 2 — DNS hijack (ADMIN, UDP/53)
C:\Python314\python.exe dns_hijack.py
# Or: run_dns.bat

# One-command orchestration:
C:\Python314\python.exe orchestrator.py
# With ARP:  python orchestrator.py --arp
```

### What needs to happen for the machine to connect

The machine must talk to our PC instead of the cloud. Three approaches:

1. **Change machine's Server IP** (best) — physically access the Android app
   settings and set Server IP to `192.168.0.100:5000`. This is the `Critical
   Next Step` above.

2. **DNS on router** — set the router's static DNS entries for both cloud
   domains to point to 192.168.0.100. No machine config changes needed.

3. **ARP spoofing** — `arp_spoof.py` tells the machine that this PC is the
   gateway (192.168.0.1). All machine traffic flows through us. Combined
   with DNS hijack, every cloud request gets answered locally.

### Testing status (as of 2026-07-07)

- `fakeapi.py` — tested on localhost ✅ (all endpoints respond correctly)
- `dns_hijack.py` — tested on localhost ✅ (intercepts and returns LOCAL)
- `arp_spoof.py` — written ✅ (fixed variable scoping)
- Machine (192.168.0.104) — **not yet connected** (no entries in DNS or access logs)
- Real PLT files — placeholder only (generic rectangle outline)
- `test_integration.py` — 37 API endpoint tests ✅ all pass (2026-07-07)

## APK Build Pipeline

The machine's Chrome browser works and can download/install APKs from `https://satelecom.up.railway.app/`.

APK variants available at `/downloads` on the CutOS frontend:
| APK | Target | Use case |
|-----|--------|----------|
| `CutOS-Terminal-Cloud.apk` | `https://satelecom.up.railway.app/` | Machine can reach internet, talks to Railway server |
| `CutOS-Terminal-Local.apk` | `http://192.168.0.100:8000/` | Fully offline, talks to local FastAPI CutOS stack |
| `launcher.apk` | — | Custom launcher to break out of kiosk mode |
| `filemanager.apk` | — | File manager for browsing machine filesystem |

**Build pipeline:** `patched_apk/extract_apk.py` → `patch_dex.py [cloud|local]` → `sign_apk.py <dex_dir> <out_name>`
- `original.apk` — stock OEM app
- `patched.apk` — cloud variant (Railway)
- `CutOS-Terminal-Local.apk` — local variant (192.168.0.100:8000)
- Pure Python signing (no JDK/Android SDK needed) via `cryptography` library
- Replaces cloud URLs in DEX strings: `https://app.mietubl.com/api/` → local/cloud base URL

## PWA (Progressive Web App)
Frontend (`D:\workspase\frontend\`) has PWA support:
- `public/manifest.json` — PWA manifest with SVG icons
- `public/sw.js` — service worker (caches static assets)
- `public/icons/icon-192.svg`, `icon-512.svg` — app icons
- `/terminal` route at `src/pages/MachineTerminal.tsx` — touch-optimized machine control interface (public, no auth)

## Files & Paths
### Bypass stack
- `fakeapi.py` — Flask HTTPS impersonation of cloud API (port 5000)
- `dns_hijack.py` — DNS server on UDP/53, intercepts cloud domains
- `arp_spoof.py` — ARP spoofing (Npcap/scapy required)
- `orchestrator.py` — launches fakeapi + DNS hijack in one command
- `make_cert.py` — generates self-signed TLS cert for fakeapi
- `listener.py` — simple HTTP debug listener
- `run_fakeapi.bat` / `run_fakeapi_logged.bat` — launch scripts
- `run_dns.bat` — DNS launch script
- `plt_cache/iphone15pro.plt` — placeholder DES-encrypted PLT
- `test_dl.plt` — test download PLT
- `fakeapi_access.log` — access log from test runs
- `fakeapi.out.log` / `fakeapi.err.log` — stdout/stderr from logged runs
- `dns_hijack.log` — DNS hijack activity log
### PrinterServer
- `PrinterServer\CutterPrinter_V1.6\` — PrinterServer root
- `PrinterServer\CutterPrinter_V1.6\PrinterServer.exe` — main server
- `PrinterServer\CutterPrinter_V1.6\db\printer.db` — database
- `PrinterServer\CutterPrinter_V1.6\templates\` — HTML templates
- `PrinterServer\CutterPrinter_V1.6\logs\log` — server log
### Research tools
- `probe_hid.py` — enumerate HID devices
- `read_hid.py` — read from vendor-defined HID interface
- `read_db.py` — inspect SQLite printer.db
- `extract_printer.py` — extract PrinterServer.rar (WIP)
- `plt_cache/` — DES-encrypted PLT files for machine to download
- `C:\Program Files (x86)\Nmap\nmap.exe` — network scanner
### CutOS stack
- `backend/app/main.py` — FastAPI entry (auth, admin, printing, machine endpoints)
- `backend/app/api/v1/*` — REST endpoints (users, machines, brands, jobs, etc.)
- `backend/app/api/legacy/cloud_api.py` — Legacy cloud API proxy
- `backend/app/api/v1/ws.py` — WebSocket endpoint for machine status
- `backend/app/api/v1/print.py` — Print job submission/confirm/progress
- `frontend/` — React 19 + Vite + Tailwind v4 PWA dashboard
- `frontend/src/pages/MachineTerminal.tsx` — Touch-optimized terminal for 5.5" screen
- `frontend/src/pages/DownloadsPage.tsx` — APK download page
- `drivers/` — Pluggable driver architecture (M180T, generic HPGL serial)
- `deployment/` — Docker compose + nginx + scripts
