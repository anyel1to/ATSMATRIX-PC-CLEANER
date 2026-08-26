"""
Utility helpers for ATS Matrix PC Cleaner.
"""

import os
import sys
import platform
from pathlib import Path
from typing import Optional, List, Tuple

def format_size(size_bytes: int) -> str:
    """Convert bytes to human readable string."""
    if size_bytes < 0:
        return "0 B"
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"


def get_windows_temp_paths() -> List[Path]:
    """Return common Windows temporary directories."""
    paths = []
    # User TEMP
    temp = os.environ.get("TEMP") or os.environ.get("TMP")
    if temp:
        paths.append(Path(temp))
    # System TEMP
    windir = os.environ.get("WINDIR", r"C:\Windows")
    paths.append(Path(windir) / "Temp")
    # LocalAppData Temp
    local = os.environ.get("LOCALAPPDATA")
    if local:
        paths.append(Path(local) / "Temp")
    return [p for p in paths if p.exists()]


def get_prefetch_path() -> Optional[Path]:
    windir = os.environ.get("WINDIR", r"C:\Windows")
    p = Path(windir) / "Prefetch"
    return p if p.exists() else None


def get_recycle_bin_path() -> Optional[Path]:
    # Not a real path for listing easily; handled specially
    return None


def get_browser_cache_paths() -> dict:
    """Return dict of browser name -> list of cache Paths."""
    caches = {}
    local = os.environ.get("LOCALAPPDATA")
    roaming = os.environ.get("APPDATA")

    if local:
        # Chrome
        chrome_base = Path(local) / "Google" / "Chrome" / "User Data"
        if chrome_base.exists():
            chrome_caches = []
            for profile in chrome_base.iterdir():
                if profile.is_dir():
                    for cache_name in ["Cache", "Code Cache", "GPUCache", "Media Cache"]:
                        c = profile / cache_name
                        if c.exists():
                            chrome_caches.append(c)
            if chrome_caches:
                caches["Google Chrome"] = chrome_caches

        # Edge
        edge_base = Path(local) / "Microsoft" / "Edge" / "User Data"
        if edge_base.exists():
            edge_caches = []
            for profile in edge_base.iterdir():
                if profile.is_dir():
                    for cache_name in ["Cache", "Code Cache", "GPUCache"]:
                        c = profile / cache_name
                        if c.exists():
                            edge_caches.append(c)
            if edge_caches:
                caches["Microsoft Edge"] = edge_caches

    if roaming:
        # Firefox
        ff_base = Path(roaming) / "Mozilla" / "Firefox" / "Profiles"
        if ff_base.exists():
            ff_caches = []
            for profile in ff_base.iterdir():
                if profile.is_dir():
                    for cache_name in ["cache2", "startupCache"]:
                        c = profile / cache_name
                        if c.exists():
                            ff_caches.append(c)
            if ff_caches:
                caches["Mozilla Firefox"] = ff_caches

    return caches


def get_thumbnail_cache() -> Optional[Path]:
    local = os.environ.get("LOCALAPPDATA")
    if local:
        p = Path(local) / "Microsoft" / "Windows" / "Explorer"
        return p if p.exists() else None
    return None


def get_windows_update_cache() -> Optional[Path]:
    windir = os.environ.get("WINDIR", r"C:\Windows")
    p = Path(windir) / "SoftwareDistribution" / "Download"
    return p if p.exists() else None


def get_recent_files() -> Optional[Path]:
    roaming = os.environ.get("APPDATA")
    if roaming:
        p = Path(roaming) / "Microsoft" / "Windows" / "Recent"
        return p if p.exists() else None
    return None


def is_windows() -> bool:
    return platform.system() == "Windows"


def safe_delete_file(path: Path) -> Tuple[bool, str]:
    """Try to delete a single file. Returns (success, message)."""
    try:
        if path.is_file() or path.is_symlink():
            path.unlink(missing_ok=True)
            return True, "deleted"
        return False, "not a file"
    except PermissionError:
        return False, "permission denied / locked"
    except OSError as e:
        return False, str(e)


def safe_delete_dir_contents(path: Path, max_depth: int = 3) -> Tuple[int, int, int]:
    """
    Recursively delete contents of a directory (not the dir itself).
    Returns (files_deleted, bytes_freed, errors)
    """
    files_deleted = 0
    bytes_freed = 0
    errors = 0

    if not path.exists() or not path.is_dir():
        return 0, 0, 0

    try:
        for root, dirs, files in os.walk(path, topdown=False):
            for name in files:
                fpath = Path(root) / name
                try:
                    size = fpath.stat().st_size
                    fpath.unlink(missing_ok=True)
                    files_deleted += 1
                    bytes_freed += size
                except (PermissionError, OSError):
                    errors += 1
            for name in dirs:
                dpath = Path(root) / name
                try:
                    dpath.rmdir()  # only if empty
                except OSError:
                    pass  # still has files or permission
    except Exception:
        errors += 1

    return files_deleted, bytes_freed, errors


def get_folder_size(path: Path) -> int:
    """Calculate total size of a folder (files only)."""
    total = 0
    try:
        for root, _, files in os.walk(path):
            for f in files:
                try:
                    fp = Path(root) / f
                    total += fp.stat().st_size
                except (OSError, PermissionError):
                    pass
    except Exception:
        pass
    return total
