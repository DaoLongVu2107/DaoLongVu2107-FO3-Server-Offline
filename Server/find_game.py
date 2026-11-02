"""Auto-detect FIFA Online 3 game directory and prepare patch files.

Usage:
    python find_game.py
    Outputs the valid game directory path on stdout, or exits with code 1.
"""
import os
import shutil
import string
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PATCH_DIR = os.path.abspath(os.path.join(HERE, ".."))
SAVED_FILE = os.path.join(PATCH_DIR, "game_path.txt")


def check_dir(d):
    if not d or not os.path.isdir(d):
        return False
    return os.path.isfile(os.path.join(d, "fifazf.exe"))


def detect():
    # 1. Saved path
    if os.path.isfile(SAVED_FILE):
        try:
            with open(SAVED_FILE, "r", encoding="utf-8") as f:
                saved = f.read().strip()
                if check_dir(saved):
                    return saved
        except Exception:
            pass

    # 2. Check candidate folders relative to patch
    for candidate in [
        PATCH_DIR,
        os.path.abspath(os.path.join(PATCH_DIR, "..")),
        os.path.abspath(os.path.join(PATCH_DIR, "..", "..")),
        os.path.abspath(os.path.join(PATCH_DIR, "Game")),
        os.path.abspath(os.path.join(PATCH_DIR, "..", "Game")),
    ]:
        if check_dir(candidate):
            return candidate

    # 3. Common game installation folders
    common = [
        r"E:\FO3TH - Copy",
        r"E:\FO3TH",
        r"D:\FO3TH",
        r"C:\FO3TH",
        r"D:\Games\FO3TH",
        r"D:\GarenaFO3\GameData",
        r"C:\GarenaFO3\GameData",
        r"C:\Program Files (x86)\GarenaFO3\GameData",
        r"D:\Program Files (x86)\GarenaFO3\GameData",
        r"D:\FO3ID\32795",
        r"E:\FO3ID\32795",
        r"C:\FO3ID\32795",
    ]
    for c in common:
        if check_dir(c):
            return c

    # 4. Search all local drives up to 3 levels deep
    drives = [f"{d}:\\" for d in string.ascii_uppercase if os.path.exists(f"{d}:\\")]
    for drv in drives:
        try:
            for root, dirs, files in os.walk(drv):
                if "fifazf.exe" in files:
                    return root
                depth = root.count(os.sep) - drv.count(os.sep)
                if depth >= 3:
                    dirs.clear()
        except Exception:
            pass

    return None


def setup_game(game_dir):
    """Copy launcher and Xigncode bypass stub into game directory if missing or different."""
    try:
        # Save path
        with open(SAVED_FILE, "w", encoding="utf-8") as f:
            f.write(game_dir)

        # 1. fifalauncher_offline.exe
        src_launcher = os.path.join(PATCH_DIR, "fifalauncher_offline.exe")
        if not os.path.isfile(src_launcher):
            src_launcher = os.path.join(PATCH_DIR, "Client_Patch", "fifalauncher_offline.exe")
        dst_launcher = os.path.join(game_dir, "fifalauncher_offline.exe")

        if os.path.isfile(src_launcher) and os.path.abspath(src_launcher) != os.path.abspath(dst_launcher):
            if not os.path.isfile(dst_launcher) or os.path.getsize(dst_launcher) != os.path.getsize(src_launcher):
                try:
                    shutil.copy2(src_launcher, dst_launcher)
                except Exception:
                    pass

        # 2. Xigncode bypass stub
        src_xem = os.path.join(PATCH_DIR, "Xigncode", "xcorona.xem")
        if not os.path.isfile(src_xem):
            src_xem = os.path.join(PATCH_DIR, "Client_Patch", "Xigncode", "xcorona.xem")
        dst_xem_dir = os.path.join(game_dir, "Xigncode")
        dst_xem = os.path.join(dst_xem_dir, "xcorona.xem")

        if os.path.isfile(src_xem) and os.path.abspath(src_xem) != os.path.abspath(dst_xem):
            if not os.path.isfile(dst_xem) or os.path.getsize(dst_xem) != os.path.getsize(src_xem):
                os.makedirs(dst_xem_dir, exist_ok=True)
                try:
                    shutil.copy2(src_xem, dst_xem)
                except Exception:
                    pass

    except Exception:
        pass


def main():
    game = detect()
    if game:
        setup_game(game)
        print(game)
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
