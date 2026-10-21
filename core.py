import os, sys, json, socket, shutil, subprocess, platform, struct, datetime, ipaddress
from pathlib import Path

APP_NAME = "Red Dragon"
ROOT = Path(__file__).resolve().parent.parent
REPORT_DIR = ROOT / "reports"

def run_cmd(args, timeout=8):
    try:
        p = subprocess.run(args, capture_output=True, text=True, timeout=timeout, check=False)
        return p.returncode, (p.stdout or "").strip(), (p.stderr or "").strip()
    except FileNotFoundError:
        return 127, "", f"Command not found: {args[0]}"
    except subprocess.TimeoutExpired:
        return 124, "", "Command timed out"
    except Exception as e:
        return 1, "", str(e)

def is_termux():
    return "com.termux" in os.environ.get("PREFIX", "") or bool(os.environ.get("TERMUX_VERSION"))

def environment():
    return {
        "tool": APP_NAME,
        "version": "1.0.0",
        "platform": platform.platform(),
        "python": sys.version.split()[0],
        "termux": is_termux(),
        "root_required": False,
        "gui_available": bool(shutil.which("wish")) and not is_termux(),
    }

def adapter_report():
    out = ["Wireless adapter capability check", "-" * 34]
    for cmd in ("iw", "iwconfig", "nmcli", "ip", "termux-wifi-scaninfo", "termux-wifi-connectioninfo"):
        out.append(f"{cmd}: {'available' if shutil.which(cmd) else 'not found'}")
    if is_termux():
        out.append("Platform: Termux/Android; ordinary apps cannot enable monitor mode or packet injection.")
        if shutil.which("termux-wifi-scaninfo"):
            rc, stdout, stderr = run_cmd(["termux-wifi-connectioninfo"])
            out.append("Termux:API connection info: " + (stdout if rc == 0 and stdout else (stderr or "not available")))
    else:
        if shutil.which("iw"):
            rc, stdout, stderr = run_cmd(["iw", "dev"])
            out.append("iw dev output:\n" + (stdout or stderr or "(no wireless interfaces reported)"))
        if shutil.which("nmcli"):
            rc, stdout, stderr = run_cmd(["nmcli", "-t", "-f", "DEVICE,TYPE,STATE", "device"])
            out.append("NetworkManager devices:\n" + (stdout or stderr or "(none)"))
    out.append("Monitor mode / injection: not activated or tested by this tool.")
    return "\n".join(out)

def wifi_scan():
    if is_termux():
        if not shutil.which("termux-wifi-scaninfo"):
            return ("Nearby Wi-Fi scan unavailable.\nInstall the termux-api package and Termux:API Android app, grant permissions, and retry. Android may still restrict scans.", [])
        rc, stdout, stderr = run_cmd(["termux-wifi-scaninfo"], timeout=15)
        if rc != 0:
            return ("Wi-Fi scan failed or permission was denied:\n" + (stderr or stdout or "Unknown error"), [])
        try:
            data = json.loads(stdout)
            lines = ["Nearby Wi-Fi scan results (as provided by Android):"]
            rows = []
            for item in data if isinstance(data, list) else []:
                row = {k: item.get(k) for k in ("SSID", "BSSID", "frequency", "level", "capabilities")}
                rows.append(row)
                lines.append(" | ".join(f"{k}={v}" for k,v in row.items() if v is not None))
            if not rows: lines.append("No results returned. Check Wi-Fi/location permissions and Android restrictions.")
            return "\n".join(lines), rows
        except Exception:
            return "Scan output could not be parsed:\n" + stdout[:4000], []
    if shutil.which("nmcli"):
        rc, stdout, stderr = run_cmd(["nmcli", "-t", "-f", "IN-USE,SSID,BSSID,CHAN,RATE,SIGNAL,SECURITY", "device", "wifi", "list"], timeout=15)
        if rc == 0:
            return ("Nearby Wi-Fi networks from NetworkManager:\n" + (stdout or "(no networks returned)"), [{"raw": x} for x in stdout.splitlines()])
        return ("nmcli scan failed:\n" + (stderr or stdout), [])
    return ("Nearby Wi-Fi scan unavailable: install/use NetworkManager (nmcli) on Linux. Termux requires Termux:API and Android permissions.", [])

def diagnostics():
    lines = ["Basic network diagnostics", "-" * 26]
    lines += [f"Hostname: {socket.gethostname()}", f"Platform: {platform.platform()}"]
    try:
        infos = socket.getaddrinfo(socket.gethostname(), None)
        ips = sorted({x[4][0] for x in infos if x[4] and not x[4][0].startswith("127.")})
        lines.append("Local IPs: " + (", ".join(ips) if ips else "not detected"))
    except Exception as e:
        lines.append("Local IP detection: " + str(e))
    if shutil.which("ip"):
        rc, stdout, stderr = run_cmd(["ip", "route", "show", "default"])
        lines.append("Default route: " + (stdout or stderr or "not detected"))
        rc, stdout, stderr = run_cmd(["ip", "-brief", "address"])
        lines.append("Interfaces:\n" + (stdout or stderr or "not available"))
    elif is_termux():
        lines.append("Interface/gateway details: Android restricts some system network details without elevated access.")
    if shutil.which("getprop"):
        rc, stdout, stderr = run_cmd(["getprop", "net.dns1"])
        if stdout: lines.append("Android DNS (net.dns1): " + stdout)
    try:
        lines.append("DNS lookup example.com: " + socket.gethostbyname("example.com"))
    except Exception as e:
        lines.append("DNS lookup failed: " + str(e))
    ping = shutil.which("ping")
    if ping:
        args = [ping, "-c", "1", "-W", "2", "1.1.1.1"]
        rc, stdout, stderr = run_cmd(args, timeout=4)
        lines.append("Ping 1.1.1.1: " + ("success" if rc == 0 else "failed / blocked"))
    else:
        lines.append("Ping: ping command not installed; skipped.")
    return "\n".join(lines)

def audit():
    checks = [
        ("Router admin password", "Use a unique password; never keep the vendor default."),
        ("Wi-Fi encryption", "Prefer WPA3-Personal, or WPA2-AES if WPA3 is unavailable; avoid WEP/open networks."),
        ("WPS", "Disable WPS if it is not needed."),
        ("Firmware", "Install router firmware updates from the vendor's official source."),
        ("Guest network", "Use a separate guest network for visitors and untrusted IoT devices."),
        ("Remote administration", "Disable WAN-side router administration unless there is a clear need."),
        ("UPnP / port forwarding", "Disable unused UPnP and remove unnecessary port-forwarding rules."),
        ("Connected devices", "Review the router's own connected-device list and remove unknown devices after verifying them."),
        ("DNS and HTTPS", "Use a trusted DNS provider if desired and keep HTTPS certificate warnings enabled."),
        ("Capture privacy", "Do not share packet captures publicly; they may contain private metadata."),
    ]
    lines = ["Local Wi-Fi security checklist", "-" * 31, "This is a checklist, not a remote router scan."]
    for i, (name, advice) in enumerate(checks, 1):
        lines.append(f"{i}. {name}: {advice}")
    return "\n".join(lines)

def analyze_capture(path_text):
    path = Path(path_text).expanduser()
    if not path.is_file():
        return f"File not found: {path}", {}
    try:
        size = path.stat().st_size
        with path.open("rb") as f:
            header = f.read(64)
        result = {"file": str(path), "size_bytes": size, "format": "unknown", "packets_or_blocks": 0, "note": ""}
        lines = [f"Capture file: {path}", f"Size: {size} bytes"]
        if len(header) >= 24 and header[:4] in (b"\xd4\xc3\xb2\xa1", b"\xa1\xb2\xc3\xd4", b"\x4d\x3c\xb2\xa1", b"\xa1\xb2\x3c\x4d"):
            result["format"] = "classic PCAP"
            endian = "<" if header[:4] in (b"\xd4\xc3\xb2\xa1", b"\x4d\x3c\xb2\xa1") else ">"
            try:
                major, minor = struct.unpack(endian + "HH", header[4:8])
                snaplen, network = struct.unpack(endian + "II", header[16:24])
                result.update({"pcap_version": f"{major}.{minor}", "snaplen": snaplen, "linktype": network})
                count, total_captured, offset = 0, 0, 24
                with path.open("rb") as f:
                    f.seek(24)
                    while True:
                        ph = f.read(16)
                        if not ph: break
                        if len(ph) < 16: result["note"] = "Truncated packet header at end of file."; break
                        sec, usec, incl, orig = struct.unpack(endian + "IIII", ph)
                        if incl > size or offset + 16 + incl > size:
                            result["note"] = "Invalid/truncated packet data; stopped safely."
                            break
                        f.seek(incl, 1)
                        offset += 16 + incl
                        count += 1
                        total_captured += incl
                        if count > 5_000_000:
                            result["note"] = "Safety limit of 5,000,000 packets reached."
                            break
                result.update({"packets_or_blocks": count, "captured_packet_bytes": total_captured})
                lines += [f"Format: classic PCAP v{major}.{minor}", f"Link type: {network}", f"Snapshot length: {snaplen}", f"Packets counted: {count}", f"Captured packet bytes: {total_captured}"]
            except Exception as e:
                result["note"] = str(e); lines.append("Could not parse PCAP: " + str(e))
        elif len(header) >= 12 and header[:4] == b"\x0a\x0d\x0d\x0a":
            result["format"] = "PCAPNG"
            # Basic block walk: detect byte order from section header byte-order magic.
            count, offset, note = 0, 0, ""
            with path.open("rb") as f:
                while offset + 12 <= size:
                    f.seek(offset); bh = f.read(12)
                    if len(bh) < 12: break
                    if bh[:4] == b"\x0a\x0d\x0d\x0a":
                        bom = bh[8:12]
                        endian = "<" if bom == b"\x4d\x3c\x2b\x1a" else ">"
                    try:
                        blen = struct.unpack(endian + "I", bh[4:8])[0]
                    except Exception:
                        note = "Could not determine PCAPNG byte order."; break
                    if blen < 12 or blen % 4 or offset + blen > size:
                        note = "Invalid/truncated PCAPNG block; stopped safely."; break
                    count += 1
                    offset += blen
                    if count > 5_000_000:
                        note = "Safety limit of 5,000,000 blocks reached."; break
            result.update({"packets_or_blocks": count, "note": note or "Counts PCAPNG blocks only; packet payloads are not decoded."})
            lines += ["Format: PCAPNG", f"Blocks counted: {count}", result["note"]]
        else:
            lines.append("Unrecognized file header. Supported: classic PCAP and PCAPNG.")
            result["note"] = "Unrecognized file format."
        lines.append("Privacy: this tool does not extract credentials or decode packet contents.")
        return "\n".join(lines), result
    except PermissionError:
        return "Permission denied while reading capture file.", {}
    except Exception as e:
        return "Capture analysis failed safely: " + str(e), {}

def save_report(title, body, extra=None):
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    safe = "".join(c.lower() if c.isalnum() else "-" for c in title).strip("-")[:32] or "report"
    txt = REPORT_DIR / f"{stamp}-{safe}.txt"
    js = REPORT_DIR / f"{stamp}-{safe}.json"
    txt.write_text(f"{APP_NAME} Report\nGenerated: {datetime.datetime.now().isoformat()}\n\n{body}\n", encoding="utf-8")
    data = {"tool": APP_NAME, "generated_at": datetime.datetime.now().isoformat(), "title": title, "body": body, "details": extra or {}}
    js.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return str(txt), str(js)
