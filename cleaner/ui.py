"""
Modern CustomTkinter GUI for ATS Matrix PC Cleaner.
Dark theme, professional layout, real-time feedback.
"""

from __future__ import annotations

import threading
import customtkinter as ctk
from tkinter import messagebox
from typing import Optional, List
import psutil

from .core import CleanerEngine, CleanTarget
from .utils import format_size, is_windows
from . import __version__


# ATS Matrix brand colors
ACCENT = "#00E5FF"       # Cyan
ACCENT_HOVER = "#00B8D4"
BG_DARK = "#0D1117"
BG_CARD = "#161B22"
BG_SIDE = "#0D1117"
TEXT = "#E6EDF3"
TEXT_MUTED = "#8B949E"
SUCCESS = "#3FB950"
WARNING = "#D29922"
DANGER = "#F85149"


class MatrixCleanerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title(f"ATS Matrix PC Cleaner  v{__version__}")
        self.geometry("1100x720")
        self.minsize(960, 640)

        # Appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        self.configure(fg_color=BG_DARK)

        self.engine = CleanerEngine()
        self.targets: List[CleanTarget] = []
        self.is_scanning = False
        self.is_cleaning = False

        self._build_ui()
        self._update_disk_info()
        self.after(100, self._initial_discover)

    # ------------------------------------------------------------------ UI
    def _build_ui(self):
        # ===== Header =====
        header = ctk.CTkFrame(self, fg_color=BG_CARD, height=70, corner_radius=0)
        header.pack(fill="x")
        header.pack_propagate(False)

        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.pack(side="left", padx=24, pady=12)

        ctk.CTkLabel(
            title_frame,
            text="ATS MATRIX",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=ACCENT,
        ).pack(anchor="w")

        ctk.CTkLabel(
            title_frame,
            text="PC CLEANER",
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
            text_color=TEXT,
        ).pack(anchor="w")

        # Disk info on right of header
        self.disk_label = ctk.CTkLabel(
            header,
            text="Disk: calculating...",
            font=ctk.CTkFont(size=13),
            text_color=TEXT_MUTED,
        )
        self.disk_label.pack(side="right", padx=24)

        # ===== Main body =====
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=16, pady=12)

        # Left panel – targets list
        left = ctk.CTkFrame(body, fg_color=BG_CARD, width=320, corner_radius=12)
        left.pack(side="left", fill="y", padx=(0, 12))
        left.pack_propagate(False)

        ctk.CTkLabel(
            left,
            text="CLEAN TARGETS",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=TEXT_MUTED,
        ).pack(anchor="w", padx=16, pady=(16, 8))

        self.targets_frame = ctk.CTkScrollableFrame(
            left, fg_color="transparent", corner_radius=0
        )
        self.targets_frame.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        # Buttons under list
        btn_frame = ctk.CTkFrame(left, fg_color="transparent")
        btn_frame.pack(fill="x", padx=12, pady=12)

        self.scan_btn = ctk.CTkButton(
            btn_frame,
            text="SCAN SYSTEM",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=ACCENT,
            hover_color=ACCENT_HOVER,
            text_color="#000000",
            height=40,
            command=self.start_scan,
        )
        self.scan_btn.pack(fill="x", pady=(0, 8))

        self.clean_btn = ctk.CTkButton(
            btn_frame,
            text="CLEAN SELECTED",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=SUCCESS,
            hover_color="#2EA043",
            text_color="#000000",
            height=40,
            state="disabled",
            command=self.start_clean,
        )
        self.clean_btn.pack(fill="x")

        # Right panel – results + log
        right = ctk.CTkFrame(body, fg_color="transparent")
        right.pack(side="left", fill="both", expand=True)

        # Summary cards
        summary = ctk.CTkFrame(right, fg_color=BG_CARD, height=90, corner_radius=12)
        summary.pack(fill="x", pady=(0, 12))
        summary.pack_propagate(False)

        self.total_size_label = ctk.CTkLabel(
            summary,
            text="0 B",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=ACCENT,
        )
        self.total_size_label.pack(side="left", padx=24, pady=16)

        ctk.CTkLabel(
            summary,
            text="potential space to free",
            font=ctk.CTkFont(size=13),
            text_color=TEXT_MUTED,
        ).pack(side="left", pady=16)

        self.status_label = ctk.CTkLabel(
            summary,
            text="Ready",
            font=ctk.CTkFont(size=13),
            text_color=TEXT_MUTED,
        )
        self.status_label.pack(side="right", padx=24)

        # Progress
        self.progress = ctk.CTkProgressBar(
            right, height=6, progress_color=ACCENT, fg_color="#21262D"
        )
        self.progress.pack(fill="x", pady=(0, 12))
        self.progress.set(0)

        # Log area
        log_card = ctk.CTkFrame(right, fg_color=BG_CARD, corner_radius=12)
        log_card.pack(fill="both", expand=True)

        ctk.CTkLabel(
            log_card,
            text="ACTIVITY LOG",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=TEXT_MUTED,
        ).pack(anchor="w", padx=16, pady=(12, 4))

        self.log_box = ctk.CTkTextbox(
            log_card,
            font=ctk.CTkFont(family="Consolas", size=12),
            fg_color="#0D1117",
            text_color=TEXT,
            corner_radius=8,
            wrap="word",
        )
        self.log_box.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        self.log_box.configure(state="disabled")

        # Footer
        footer = ctk.CTkFrame(self, fg_color=BG_CARD, height=36, corner_radius=0)
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)

        ctk.CTkLabel(
            footer,
            text=f"ATS Matrix  •  v{__version__}  •  MIT License  •  Safe & Transparent",
            font=ctk.CTkFont(size=11),
            text_color=TEXT_MUTED,
        ).pack(side="left", padx=16)

        ctk.CTkLabel(
            footer,
            text="Made for the community",
            font=ctk.CTkFont(size=11),
            text_color=TEXT_MUTED,
        ).pack(side="right", padx=16)

    # ------------------------------------------------------------------ Helpers
    def log(self, message: str, level: str = "info"):
        self.log_box.configure(state="normal")
        prefix = {
            "info": "• ",
            "success": "✓ ",
            "warning": "⚠ ",
            "error": "✗ ",
        }.get(level, "• ")
        self.log_box.insert("end", f"{prefix}{message}\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def _update_disk_info(self):
        try:
            usage = psutil.disk_usage("C:\\" if is_windows() else "/")
            free = format_size(usage.free)
            total = format_size(usage.total)
            percent = usage.percent
            self.disk_label.configure(
                text=f"C:  {free} free of {total}  ({percent}% used)"
            )
        except Exception:
            self.disk_label.configure(text="Disk info unavailable")

    def _initial_discover(self):
        self.log("Discovering cleanable locations...")
        self.targets = self.engine.discover_targets()
        self._render_targets()
        self.log(f"Found {len(self.targets)} categories. Click SCAN SYSTEM to analyze.", "success")

    def _render_targets(self):
        for widget in self.targets_frame.winfo_children():
            widget.destroy()

        for target in self.targets:
            row = ctk.CTkFrame(self.targets_frame, fg_color="transparent")
            row.pack(fill="x", pady=3)

            var = ctk.BooleanVar(value=target.selected)

            def make_toggle(t=target, v=var):
                def toggle():
                    t.selected = v.get()
                    self._update_total()
                return toggle

            cb = ctk.CTkCheckBox(
                row,
                text="",
                variable=var,
                width=24,
                command=make_toggle(),
                fg_color=ACCENT,
                hover_color=ACCENT_HOVER,
            )
            cb.pack(side="left", padx=(4, 8))

            info = ctk.CTkFrame(row, fg_color="transparent")
            info.pack(side="left", fill="x", expand=True)

            name_row = ctk.CTkFrame(info, fg_color="transparent")
            name_row.pack(fill="x")

            ctk.CTkLabel(
                name_row,
                text=target.name,
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=TEXT,
                anchor="w",
            ).pack(side="left")

            size_lbl = ctk.CTkLabel(
                name_row,
                text=format_size(target.size_bytes) if target.size_bytes else "—",
                font=ctk.CTkFont(size=12),
                text_color=ACCENT if target.size_bytes else TEXT_MUTED,
            )
            size_lbl.pack(side="right")
            target._size_label = size_lbl  # type: ignore

            ctk.CTkLabel(
                info,
                text=target.description,
                font=ctk.CTkFont(size=11),
                text_color=TEXT_MUTED,
                anchor="w",
                wraplength=240,
            ).pack(fill="x")

            # risk badge
            risk_color = {"low": SUCCESS, "medium": WARNING, "high": DANGER}.get(
                target.risk, TEXT_MUTED
            )
            ctk.CTkLabel(
                info,
                text=target.risk.upper(),
                font=ctk.CTkFont(size=9, weight="bold"),
                text_color=risk_color,
            ).pack(anchor="w")

    def _update_total(self):
        total = sum(t.size_bytes for t in self.targets if t.selected)
        self.total_size_label.configure(text=format_size(total))

    # ------------------------------------------------------------------ Actions
    def start_scan(self):
        if self.is_scanning or self.is_cleaning:
            return
        self.is_scanning = True
        self.scan_btn.configure(state="disabled", text="SCANNING...")
        self.clean_btn.configure(state="disabled")
        self.progress.set(0)
        self.status_label.configure(text="Scanning...")
        self.log("Starting full system scan...")

        def worker():
            def progress(name, done, total):
                self.after(0, lambda: self._on_scan_progress(name, done, total))

            self.engine.scan_all(progress_callback=progress)
            self.after(0, self._on_scan_finished)

        threading.Thread(target=worker, daemon=True).start()

    def _on_scan_progress(self, name: str, done: int, total: int):
        self.progress.set(done / max(total, 1))
        self.status_label.configure(text=f"Scanning {name} ({done}/{total})")
        self.log(f"Analyzed: {name}")

    def _on_scan_finished(self):
        self.is_scanning = False
        self.scan_btn.configure(state="normal", text="SCAN SYSTEM")
        self.clean_btn.configure(state="normal")
        self.progress.set(1)
        self.status_label.configure(text="Scan complete")

        # Refresh size labels
        for t in self.targets:
            if hasattr(t, "_size_label"):
                t._size_label.configure(
                    text=format_size(t.size_bytes),
                    text_color=ACCENT if t.size_bytes > 0 else TEXT_MUTED,
                )

        self._update_total()
        total = sum(t.size_bytes for t in self.targets)
        self.log(f"Scan finished. Total junk found: {format_size(total)}", "success")
        self._update_disk_info()

    def start_clean(self):
        selected = [t for t in self.targets if t.selected]
        if not selected:
            messagebox.showinfo("Nothing selected", "Select at least one category to clean.")
            return

        total = sum(t.size_bytes for t in selected)
        confirm = messagebox.askyesno(
            "Confirm Clean",
            f"You are about to permanently delete approximately {format_size(total)} of junk files.\n\n"
            "This action cannot be undone.\n\nContinue?",
        )
        if not confirm:
            return

        self.is_cleaning = True
        self.scan_btn.configure(state="disabled")
        self.clean_btn.configure(state="disabled", text="CLEANING...")
        self.progress.set(0)
        self.status_label.configure(text="Cleaning...")
        self.log("Starting cleanup of selected targets...")

        def worker():
            def progress(name, done, total):
                self.after(0, lambda: self._on_clean_progress(name, done, total))

            results = self.engine.clean_selected(progress_callback=progress)
            self.after(0, lambda: self._on_clean_finished(results))

        threading.Thread(target=worker, daemon=True).start()

    def _on_clean_progress(self, name: str, done: int, total: int):
        self.progress.set(done / max(total, 1))
        self.status_label.configure(text=f"Cleaning {name} ({done}/{total})")
        self.log(f"Cleaned: {name}")

    def _on_clean_finished(self, results: dict):
        self.is_cleaning = False
        self.scan_btn.configure(state="normal")
        self.clean_btn.configure(state="normal", text="CLEAN SELECTED")
        self.progress.set(1)
        self.status_label.configure(text="Cleanup complete")

        total_files = 0
        total_bytes = 0
        total_errors = 0
        for tid, (f, b, e) in results.items():
            total_files += f
            total_bytes += b
            total_errors += e

        self.log(
            f"Done! Removed {total_files} files • Freed {format_size(total_bytes)}"
            + (f" • {total_errors} items skipped (locked/permission)" if total_errors else ""),
            "success",
        )

        # Reset sizes for cleaned items
        for t in self.targets:
            if t.selected:
                t.size_bytes = 0
                t.file_count = 0
                if hasattr(t, "_size_label"):
                    t._size_label.configure(text="0 B", text_color=TEXT_MUTED)

        self._update_total()
        self._update_disk_info()
        messagebox.showinfo(
            "Cleanup Finished",
            f"Successfully cleaned!\n\nFiles removed: {total_files}\nSpace freed: {format_size(total_bytes)}",
        )


def run_app():
    app = MatrixCleanerApp()
    app.mainloop()
