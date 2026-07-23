# Download & Install

Complete installation guide for davici-resolve on any system.

---

## Option 1: One-Click Install (Windows)

### Prerequisites
- Windows 10 or later
- Internet connection (for first-time setup)

### Steps

1. **Download** the project:
   ```
   git clone https://github.com/sulmanfarooqq/davici-resolve.git
   ```
   Or click **Code > Download ZIP** on GitHub and extract it.

2. **Double-click** `setup.bat` in the project root.

3. **Wait** for the installer to:
   - Create a virtual environment (first time only)
   - Install PySide6, NumPy, OpenCV, Pillow
   - Run 242 tests
   - Launch the application

4. **Done!** The app opens maximized.

### What setup.bat Does

```
[1/4] Creating virtual environment...
[2/4] Installing dependencies (this may take a few minutes)...
[3/4] Running tests...
[4/4] Launching davici-resolve...
```

---

## Option 2: Manual Install (Windows, macOS, Linux)

### Prerequisites

| Requirement | How to Check |
|-------------|--------------|
| **Python 3.10+** | `python --version` or `python3 --version` |
| **pip** | `pip --version` |
| **Git** (optional) | `git --version` |

### Step 1: Install Python

**Windows:**
1. Go to https://www.python.org/downloads/
2. Download Python 3.12 (recommended)
3. Run the installer
4. **CHECK** "Add Python to PATH" during installation
5. Click "Install Now"

**macOS:**
```bash
# Using Homebrew
brew install python@3.12

# Or download from https://www.python.org/downloads/
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3.12 python3.12-venv python3-pip
```

**Linux (Fedora):**
```bash
sudo dnf install python3.12 python3.12-pip
```

### Step 2: Clone or Download

```bash
git clone https://github.com/sulmanfarooqq/davici-resolve.git
cd davici-resolve
```

Or download the ZIP from GitHub and extract it.

### Step 3: Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

If PySide6 fails to install (slow network, firewall), try a mirror:

```bash
# Aliyun mirror (fast in Asia)
pip install PySide6 numpy opencv-python Pillow -i https://mirrors.aliyun.com/pypi/simple/

# Tsinghua mirror
pip install PySide6 numpy opencv-python Pillow -i https://pypi.tuna.tsinghua.edu.cn/simple/

# PyPI official
pip install PySide6 numpy opencv-python Pillow --default-timeout=300
```

### Step 5: Run Tests

```bash
python -m pytest software/tests/ -v
```

Expected: `242 passed`

### Step 6: Launch

```bash
python software/main.py
```

---

## Option 3: Install Python 3.12 Alongside Existing Python

If you have Python 3.13+ or 3.14 (PySide6 may not support it):

### Download Python 3.12.9

1. Go to: https://www.python.org/downloads/release/python-3129/
2. Download **Windows installer (64-bit)**
3. Run the installer
4. **CHECK** "Add Python 3.12 to PATH"
5. Choose "Install Now"

### Use Python 3.12 Specifically

```bash
# Windows - use py launcher
py -3.12 -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python software/main.py

# Or use full path
C:\Python312\python.exe -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python software/main.py
```

---

## Standalone .exe Build (Windows)

See [BUILD_EXE.md](BUILD_EXE.md) for creating a single-file Windows executable.

---

## Verify Installation

After installation, run this to verify everything works:

```bash
python -c "
import PySide6; print(f'PySide6: {PySide6.__version__}')
import numpy; print(f'NumPy: {numpy.__version__}')
import cv2; print(f'OpenCV: {cv2.__version__}')
import PIL; print(f'Pillow: {PIL.__version__}')
from core.color_math import colorbalance_lgg; print('Color math: OK')
from nodes import NODE_CLASSES; print(f'Nodes: {len(NODE_CLASSES)} registered')
print('All systems go!')
"
```

Expected output:
```
PySide6: 6.11.1
NumPy: 2.x.x
OpenCV: 4.x.x
Pillow: 11.x.x
Color math: OK
Nodes: 25 registered
All systems go!
```

---

## Next Steps

- [User Guide](USER_GUIDE.md) — Learn how to use the application
- [Keyboard Shortcuts](KEYBOARD_SHORTCUTS.md) — Speed up your workflow
- [Node Reference](NODE_REFERENCE.md) — All 25 node types explained
