"""
Core scanning and cleaning engine for ATS Matrix PC Cleaner.
Thread-safe design with progress callbacks.
"""

from __future__ import annotations

import os
import shutil
import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import ctypes

from .utils import (
    format_size,
    get_windows_temp_paths,
    get_prefetch_path,
    get_browser_cache_paths,
    get_thumbnail_cache,
    get_windows_update_cache,
    get_recent_files,
    is_windows,
    safe_delete_dir_contents,
    get_folder_size,
)


@dataclass
class CleanTarget:
    """Represents a cleanable location or category."""
    id: str
    name: str
    description: str
    paths: List[Path] = field(default_factory=list)
    size_bytes: int = 0
    file_count: int = 0
    selected: bool = True
    special: Optional[str] = None  # e.g. "recycle", "prefetch"
    risk: str = "low"  # low / medium / high


class CleanerEngine:
    """Main engine that discovers targets, scans sizes, and performs cleaning."""

    def __init__(self):
        self.targets: Dict[str, CleanTarget] = {}
        self._lock = threading.Lock()
        self._cancel = False

    def cancel(self):
        self._cancel = True

    def reset_cancel(self):
        self._cancel = False

    def discover_targets(self) -> List[CleanTarget]:
        """Build the list of available clean targets based on OS."""
        self.targets.clear()

        if not is_windows():
            # Minimal support for non-Windows (temp only)
            import tempfile
            t = CleanTarget(
                id="temp",
                name="Temporary Files",
                description="System and user temporary files",
                paths=[Path(tempfile.gettempdir())],
                risk="low",
            )
            self.targets[t.id] = t
            return list(self.targets.values())

        # === Windows targets ===

        # 1. User + System Temp
        temp_paths = get_windows_temp_paths()
        if temp_paths:
            t = CleanTarget(
                id="temp",
                name="Temporary Files",
                description="User TEMP, Windows\\Temp and LocalAppData\\Temp",
                paths=temp_paths,
                risk="low",
            )
            self.targets[t.id] = t

        # 2. Prefetch
        prefetch = get_prefetch_path()
        if prefetch:
            t = CleanTarget(
                id="prefetch",
                name="Prefetch Data",
                description="Windows Prefetch files (can free space, may slightly affect next boot)",
                paths=[prefetch],
                risk="medium",
                special="prefetch",
            )
            self.targets[t.id] = t

        # 3. Thumbnail Cache
        thumbs = get_thumbnail_cache()
        if thumbs:
            t = CleanTarget(
                id="thumbnails",
                name="Thumbnail Cache",
                description="Windows Explorer thumbnail database",
                paths=[thumbs],
                risk="low",
            )
            self.targets[t.id] = t

        # 4. Windows Update Download Cache
        wu = get_windows_update_cache()
        if wu:
            t = CleanTarget(
                id="wu_cache",
                name="Windows Update Cache",
                description="Downloaded update packages that are no longer needed",
                paths=[wu],
                risk="low",
            )
            self.targets[t.id] = t

        # 5. Recent Files shortcuts
        recent = get_recent_files()
        if recent:
            t = CleanTarget(
                id="recent",
                name="Recent Files",
                description="Shortcuts to recently opened documents",
                paths=[recent],
                risk="low",
            )
            self.targets[t.id] = t

        # 6. Browser Caches
        browser_caches = get_browser_cache_paths()
        for browser, paths in browser_caches.items():
            tid = f"browser_{browser.lower().replace(' ', '_')}"
            t = CleanTarget(
                id=tid,
                name=f"{browser} Cache",
                description=f"Temporary internet files and cache for {browser}",
                paths=paths,
                risk="low",
            )
            self.targets[t.id] = t

        # 7. Recycle Bin (special handling)
        t = CleanTarget(
            id="recycle",
            name="Recycle Bin",
            description="Empty the Windows Recycle Bin",
            paths=[],
            risk="low",
            special="recycle",
        )
        self.targets[t.id] = t

        return list(self.targets.values())

    def scan_target(self, target: CleanTarget) -> CleanTarget:
        """Calculate size and approximate file count for one target."""
        if self._cancel:
            return target

        total_size = 0
        total_files = 0

        if target.special == "recycle":
            # Approximate via shell or skip detailed
            target.size_bytes = 0
            target.file_count = 0
            return target

        for path in target.paths:
            if self._cancel:
                break
            if not path.exists():
                continue
            try:
                if path.is_file():
                    total_size += path.stat().st_size
                    total_files += 1
                else:
                    size = get_folder_size(path)
                    # rough file count
                    file_count = 0
                    for root, _, files in os.walk(path):
                        file_count += len(files)
                        if self._cancel:
                            break
                    total_size += size
                    total_files += file_count
            except Exception:
                pass

        target.size_bytes = total_size
        target.file_count = total_files
        return target

    def scan_all(
        self,
        progress_callback: Optional[Callable[[str, int, int], None]] = None,
        max_workers: int = 4,
    ) -> List[CleanTarget]:
        """Scan all discovered targets in parallel."""
        self.reset_cancel()
        targets = list(self.targets.values())
        total = len(targets)
        completed = 0

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(self.scan_target, t): t for t in targets}
            for future in as_completed(futures):
                if self._cancel:
                    break
                completed += 1
                target = future.result()
                if progress_callback:
                    progress_callback(target.name, completed, total)

        return list(self.targets.values())

    def clean_target(
        self,
        target: CleanTarget,
        progress_callback: Optional[Callable[[str, int], None]] = None,
    ) -> Tuple[int, int, int]:
        """
        Clean one target.
        Returns (files_deleted, bytes_freed, errors)
        """
        if not target.selected:
            return 0, 0, 0

        files = 0
        bytes_freed = 0
        errors = 0

        if target.special == "recycle":
            return self._empty_recycle_bin()

        for path in target.paths:
            if self._cancel:
                break
            if not path.exists():
                continue

            if path.is_file():
                try:
                    size = path.stat().st_size
                    path.unlink(missing_ok=True)
                    files += 1
                    bytes_freed += size
                except Exception:
                    errors += 1
            else:
                f, b, e = safe_delete_dir_contents(path)
                files += f
                bytes_freed += b
                errors += e

            if progress_callback:
                progress_callback(target.name, bytes_freed)

        return files, bytes_freed, errors

    def clean_selected(
        self,
        progress_callback: Optional[Callable[[str, int, int], None]] = None,
    ) -> Dict[str, Tuple[int, int, int]]:
        """Clean all selected targets. Returns dict id -> (files, bytes, errors)."""
        self.reset_cancel()
        results = {}
        selected = [t for t in self.targets.values() if t.selected]
        total = len(selected)
        done = 0

        for target in selected:
            if self._cancel:
                break
            res = self.clean_target(target)
            results[target.id] = res
            done += 1
            if progress_callback:
                progress_callback(target.name, done, total)

        return results

    def _empty_recycle_bin(self) -> Tuple[int, int, int]:
        """Empty Windows Recycle Bin using shell API."""
        if not is_windows():
            return 0, 0, 1
        try:
            # SHEmptyRecycleBinW
            # Flags: SHERB_NOCONFIRMATION | SHERB_NOPROGRESSUI | SHERB_NOSOUND
            SHERB_NOCONFIRMATION = 0x00000001
            SHERB_NOPROGRESSUI = 0x00000002
            SHERB_NOSOUND = 0x00000004
            flags = SHERB_NOCONFIRMATION | SHERB_NOPROGRESSUI | SHERB_NOSOUND

            shell32 = ctypes.windll.shell32  # type: ignore
            result = shell32.SHEmptyRecycleBinW(None, None, flags)
            if result == 0:
                return 1, 0, 0  # success (size unknown easily)
            else:
                return 0, 0, 1
        except Exception:
            # Fallback attempt with send2trash not applicable for whole bin
            return 0, 0, 1
