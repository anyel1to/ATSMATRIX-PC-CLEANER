# ATS Matrix PC Cleaner

**Professional Windows PC optimization & junk file removal tool**

[![License: MIT](https://img.shields.io/badge/License-MIT-cyan.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows-0078D6.svg)](https://www.microsoft.com/windows)
[![ATS Matrix](https://img.shields.io/badge/ATS%20Matrix-AI%20Tools-00E5FF.svg)](https://github.com/atsmatrix)

---

A clean, fast, and **transparent** desktop utility that helps you reclaim disk space by safely removing temporary files, browser caches, Windows junk, and more — without bloat, ads, or shady behavior.

Built with a modern dark UI (CustomTkinter) matching the ATS Matrix aesthetic.

![ATS Matrix](https://img.shields.io/badge/Made%20by-ATS%20Matrix-00E5FF?style=for-the-badge)

## ✨ Features

- **Multi-threaded scanning** – analyzes multiple locations in parallel
- **Smart categories** with risk levels (Low / Medium)
  - Temporary Files (User + System)
  - Prefetch Data
  - Thumbnail Cache
  - Windows Update Cache
  - Recent Files shortcuts
  - Browser Caches (Chrome, Edge, Firefox)
  - Recycle Bin
- **Selective cleaning** – choose exactly what to remove
- **Real-time progress & activity log**
- **Safe by design** – skips locked/permission-denied files, never touches your documents or installed programs
- **Disk usage overview** at a glance
- **One-click Clean Selected** with confirmation
- **Zero telemetry / zero ads / open source**

## 🖥️ Screenshots

> Dark professional interface with cyan accents, live size counters, and detailed activity log.

*(Run the app to see the full UI)*

## 🚀 Quick Start

### Prerequisites

- Windows 10 / 11
- Python 3.9 or newer

### Installation

```bash
# Clone the repository
git clone https://github.com/anyel1to/ATSMATRIX-PC-CLEANER.git
cd ATSMATRIX-PC-CLEANER

# Create virtual environment (recommended)
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Run

```bash
python main.py
```

## 📦 Building a Standalone EXE (optional)

```bash
pip install pyinstaller
pyinstaller --noconfirm --onefile --windowed --name "ATS-Matrix-PC-Cleaner" main.py
```

The executable will appear in the `dist/` folder.

## 🛡️ Safety Notes

- The cleaner **never** deletes files from your Documents, Desktop, Downloads, or program installation folders.
- Prefetch cleaning is marked **Medium** risk because it can slightly increase the next boot time (Windows rebuilds it automatically).
- Locked files (in use by another process) are automatically skipped.
- Always review the total size before confirming a clean.

## 📁 Project Structure

```
ATSMATRIX-PC-CLEANER/
├── main.py                 # Entry point
├── requirements.txt
├── LICENSE
├── README.md
├── .gitignore
└── cleaner/
    ├── __init__.py
    ├── core.py             # Scanning & cleaning engine
    ├── ui.py               # CustomTkinter modern GUI
    └── utils.py            # Path helpers & safe delete utilities
```

## 🛠️ Tech Stack

| Component          | Technology              |
|--------------------|-------------------------|
| Language           | Python 3.9+             |
| GUI                | CustomTkinter           |
| System Info        | psutil                  |
| Safe Delete        | Native OS APIs + careful error handling |
| Packaging          | PyInstaller (optional)  |

## 📄 License

This project is licensed under the **MIT License** – see the [LICENSE](LICENSE) file for details.

## 🔗 Links & Related Projects

- **ATS Matrix** – Premium AI agent tools, automation & high-performance visualizations  
  [GitHub Organization / Profile](https://github.com/atsmatrix)
- Other public demos from the same ecosystem:
  - ATSMATRIX-HORIZON (market radar + whale tracking)
  - Multi-agent collision engines & real-time graph visualizers
  - ALPR / security camera tools (RAVEN, Flock-style)

## 🤝 Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

---

**Made with ❤️ by ATS Matrix**  
*Helping people keep their machines clean, fast, and under control.*
