"""Launcher checks before the servers start (called by 2_Choi_Game_Offline.bat).

    python Server/career/preflight.py

Prints [OK] / [CANH BAO] / [LOI] lines (ASCII only: the Windows console code page cannot show
Vietnamese diacritics). Exit code 2 = a problem that stops the launch (port 443 taken), 0 otherwise.
Stand-alone on purpose: standard library only, no imports from the server.
"""
import errno
import os
import socket
import struct
import subprocess
import sys

PORTS = ((443, "server game (https://APSEODESK172)", True), (8088, "trang admin", False),
         (28002, "messenger", False))


def check_python():
    out = []
    v = sys.version_info
    out.append(("OK", f"Python {v.major}.{v.minor}.{v.micro}"))
    if (v.major, v.minor) < (3, 8):
        out.append(("LOI", "Can Python 3.8 tro len. Tai tai https://www.python.org/downloads/"))
    elif (v.major, v.minor) >= (3, 13):
        out.append(("CANH BAO", "Python 3.13+ : goi cai offline (Server/wheels) chi ho tro toi 3.12. "
                                "Lan dau can co mang de tu tai 'cryptography'. Khuyen dung Python 3.12."))
    if struct.calcsize("P") * 8 != 64:
        out.append(("CANH BAO", "Python 32-bit: goi cai offline chi co ban 64-bit. Nen cai Python 64-bit."))
    return out


def port_owner(port):
    """'name (PID n)' of the Windows process listening on port, or '' if unknown."""
    if os.name != "nt":
        return ""
    try:
        lines = subprocess.run(["netstat", "-ano", "-p", "TCP"], capture_output=True, text=True,
                               timeout=15).stdout.splitlines()
        lines += subprocess.run(["netstat", "-ano", "-p", "TCPv6"], capture_output=True, text=True,
                                timeout=15).stdout.splitlines()
    except (OSError, subprocess.SubprocessError):
        return ""
    for ln in lines:
        parts = ln.split()
        # TCP  0.0.0.0:443  0.0.0.0:0  LISTENING  1234   (the state word is localized: skip it)
        if len(parts) >= 5 and parts[0].upper().startswith("TCP") and parts[1].endswith(f":{port}") \
                and parts[2].endswith((":0", ":*")) and parts[-1].isdigit():
            pid = parts[-1]
            try:
                row = subprocess.run(["tasklist", "/fi", f"PID eq {pid}", "/fo", "csv", "/nh"],
                                     capture_output=True, text=True, timeout=15).stdout.strip()
                name = row.split(",")[0].strip('"') if row.startswith('"') else "?"
            except (OSError, subprocess.SubprocessError):
                name = "?"
            return f"{name} (PID {pid})"
    return ""


def port_free(port):
    """True / False (in use) / None (cannot tell, e.g. no permission)."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        if hasattr(socket, "SO_EXCLUSIVEADDRUSE"):
            s.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        s.bind(("0.0.0.0", port))
        return True
    except OSError as e:
        if e.errno in (errno.EADDRINUSE, getattr(errno, "WSAEADDRINUSE", -1), 10048):
            return False
        if e.errno in (errno.EACCES, 10013):
            return None if os.name != "nt" else False  # Windows 10013 = taken exclusively
        return None
    finally:
        s.close()


def check_ports():
    out = []
    for port, what, required in PORTS:
        free = port_free(port)
        if free:
            out.append(("OK", f"Cong {port} trong ({what})"))
        elif free is None:
            out.append(("CANH BAO", f"Khong kiem tra duoc cong {port} ({what})"))
        else:
            owner = port_owner(port) or "mot chuong trinh khac"
            msg = f"Cong {port} ({what}) dang bi chiem boi {owner}."
            if port == 443:
                msg += " Hay tat chuong trinh do (thuong la IIS, VMware, Skype, XAMPP/Apache) roi chay lai."
            out.append(("LOI" if required else "CANH BAO", msg))
    return out


def main():
    results = check_python() + check_ports()
    if os.environ.get("FO3_DEV") == "1":
        results.append(("CANH BAO", "CHE DO DEV dang bat: cong cu cheat tren trang admin hoat dong."))
    for level, msg in results:
        print(f"[{level}] {msg}", flush=True)
    return 2 if any(level == "LOI" for level, _ in results) else 0


if __name__ == "__main__":
    sys.exit(main())
