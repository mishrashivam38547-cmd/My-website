# Red Dragon — Wi-Fi Security Toolkit

A Python toolkit for **authorized, non-invasive Wi-Fi diagnostics and offline capture-file analysis**. Designed to install on Kali Linux and Termux without rooting Android.

## Included
- Wi-Fi/environment and adapter capability detection
- Basic network diagnostics (IP, default gateway, DNS, ping)
- Local security checklist and recommendations
- Classic PCAP and basic PCAPNG metadata/packet-block counting
- Exportable TXT/JSON reports
- Terminal menu and optional Tkinter GUI (desktop Linux only)
- Dependency checks, installer scripts and uninstall helper

## Important limitations
- **No root required**, but Android/Termux cannot expose every system feature.
- Nearby Wi-Fi scan results on Termux require the Termux:API Android add-on and the `termux-api` package. Android location/Wi-Fi permissions and location services may also be required. If unavailable, the app reports that instead of pretending to scan.
- On Linux, nearby network discovery depends on `nmcli`/NetworkManager. `iw` detection is informational. Monitor mode, injection and deauthentication are **not implemented**.
- PCAP analysis is offline and read-only. It does not crack passwords, extract credentials, or capture traffic.
- Basic PCAPNG parsing counts blocks; packet interpretation is intentionally minimal.
- Only test networks and captures you own or have explicit permission to assess.

## Quick install

### Kali Linux
```bash
unzip red-dragon-wifi-toolkit.zip
cd red-dragon-wifi-toolkit
chmod +x install-kali.sh
./install-kali.sh
```
The installer creates a virtual environment in this project and a `red-dragon` launcher.

### Termux (no root)
Install Termux from a trusted source, then:
```bash
pkg update
pkg install python unzip
unzip red-dragon-wifi-toolkit.zip
cd red-dragon-wifi-toolkit
chmod +x install-termux.sh
./install-termux.sh
```
Optional nearby scan support:
```bash
pkg install termux-api
```
Also install the **Termux:API** Android app from the same trusted distribution source as Termux, then grant requested permissions. Termux:API cannot guarantee scan access on every Android version/device.

### Run
```bash
./run.sh
```
Terminal menu is the default. GUI:
```bash
./run.sh --gui
```
GUI requires Tkinter and a desktop environment. It is generally unavailable in ordinary Termux sessions.

## Features
- **Scanner:** attempts `nmcli` on Linux or `termux-wifi-scaninfo` on Termux. If unavailable, explains why.
- **Diagnostics:** reads local IP/interface details and gateway/DNS where supported; ping is optional.
- **Audit:** local, non-invasive configuration checklist; it does not remotely probe routers.
- **PCAP:** offline packet count and lengths for classic PCAP; basic PCAPNG block count.
- **Reports:** saves timestamped TXT and JSON reports in `reports/`.
- **Adapter:** detects tools and adapter/monitor-mode capability hints; it does not enable monitor mode.

## Uninstall
Run:
```bash
./uninstall.sh
```
This removes the virtual environment and launcher created by this project. It keeps source files and reports. To remove everything, delete the project folder yourself after backing up reports.

## GitHub upload
1. Create a new GitHub repository named `red-dragon-wifi-toolkit`.
2. From this project directory:
```bash
git init
git add .
git commit -m "Initial Red Dragon toolkit"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/red-dragon-wifi-toolkit.git
git push -u origin main
```
Replace `YOUR-USERNAME` with your GitHub username. Never upload private captures or reports.

## Troubleshooting
- `termux-wifi-scaninfo` missing: install `termux-api` package and Termux:API app.
- Scan empty/denied: check Android Wi-Fi, location services, app permissions, and OS restrictions.
- `nmcli` missing: install NetworkManager on Kali or use the diagnostics/audit features.
- GUI unavailable: use the terminal menu; do not install random X11 packages solely to force it.
- No wireless adapter/monitor mode: hardware/driver/Android restrictions cannot be fixed by this Python program.
