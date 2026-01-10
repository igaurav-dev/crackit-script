# 🎯 Crackit - AI-Powered Exam Assistant

> **Capture your screen, get AI-powered answers instantly via Telegram.**

Crackit is a lightweight screen capture tool that streams your display to a backend server, which uses Vision AI to detect questions and deliver solutions directly to your Telegram.

---

## 🚀 One-Line Installation

### Linux / macOS / Raspberry Pi

```bash
curl -fsSL https://raw.githubusercontent.com/igaurav-dev/crackit-script/main/install.sh | bash
```

### Windows (PowerShell)

```powershell
irm https://raw.githubusercontent.com/igaurav-dev/crackit-script/main/install.ps1 | iex
```

This installs Crackit to `~/.crackit` and adds the `crackit` command to your PATH.

---

## 📖 How It Works

```
┌─────────────────────────────────────────────────────────────────────┐
│                           YOUR DEVICE (Pi/Mac/Linux/Windows)        │
│  ┌─────────────┐    ┌──────────────┐    ┌──────────────────────┐   │
│  │   Screen    │───▶│  Capture &   │───▶│  HTTP POST to Server │   │
│  │  (Exam UI)  │    │  Compress    │    │  (WebP Image)        │   │
│  └─────────────┘    └──────────────┘    └──────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                           SOCKET SERVER (Cloud)                      │
│  ┌─────────────┐    ┌──────────────┐    ┌──────────────────────┐   │
│  │  Receive    │───▶│  Vision AI   │───▶│ Telegram Bot         │   │
│  │  Image      │    │  Solve Q     │    │ Sends Answer         │   │
│  └─────────────┘    └──────────────┘    └──────────────────────┘   │
│         │                                                            │
│         ▼                                                            │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

### Key Features

| Feature | Description |
|---------|-------------|
| **2-Second Capture** | Ultra-fast screen capture every 2 seconds |
| **WebP Compression** | Optimized image format for fast uploads |
| **Vision AI** | Gemini 1.5 Flash extracts and solves questions |
| **RAG Caching** | Duplicate questions answered instantly (0.99 similarity) |
| **Telegram Delivery** | Solutions sent directly to your phone |
| **Image Deduplication** | Same screen = No AI call = Saves quota |

---

## 📦 Manual Installation

If you prefer manual setup:

```bash
# Clone the repository
git clone https://github.com/igaurav-dev/crackit-script.git
cd crackit-script

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

## ⚙️ Configuration

### 1. Get Your API Token

Visit the **Crackit Dashboard** to create your token:

🌐 **[https://crackit-dashboard.netlify.app/](https://crackit-dashboard.netlify.app/)**

1. Sign up or log in
2. Create a new token
3. Copy your token

### 2. Setup Your Script

```bash
crackit setup
```

You'll be prompted for:
- **API Token**: Paste the token from the dashboard
- **API Endpoint**: Press Enter to use default (`https://crackit.igaurav.dev`)

### 3. Link Telegram (Optional)

1. Get the Telegram bot link from your dashboard
2. Click the link to start your bot
3. Send `/start` to activate

---

## 🎮 Usage

### Start the Service

**Linux / macOS / Raspberry Pi:**
```bash
crackit start  # Runs in background, terminal stays free
```

**Windows:**
```powershell
# Option 1: Foreground mode (simple, but terminal must stay open)
crackit start -f

# Option 2: Background mode (survives terminal close)
Start-Process -WindowStyle Hidden powershell -ArgumentList "-Command", "crackit start -f"
```

> **Windows Note:** Option 2 runs the script in a hidden window that will keep running even if you close PowerShell or if exam software closes your terminal.

### Stop the Service

```bash
crackit stop
```

### Check Status

```bash
crackit status
```

### View Logs

```bash
crackit logs
```

### Uninstall

```bash
crackit uninstall
```

This removes all Crackit files and configurations.

---

## 🖥️ Supported Platforms

| Platform | Status | Capture Method |
|----------|--------|----------------|
| **Linux (Raspberry Pi)** | ✅ Fully Supported | `scrot` / `grim` |
| **macOS** | ✅ Fully Supported | Native `mss` |
| **Windows** | ✅ Fully Supported | Native `mss` |

### Linux/Raspberry Pi Prerequisites

```bash
sudo apt install scrot   # For X11
sudo apt install grim    # For Wayland
```

---

## 🔐 Environment Variables

You can also configure via environment variables:

```bash
export API_ENDPOINT="http://your-server:8000"
export API_TOKEN="your-token-here"
```

---

## 📁 File Structure

```
~/.crackit/
├── sync_service.py      # Main CLI entry point
├── config.py            # Configuration settings
├── core/
│   ├── capture.py       # Screen capture logic
│   ├── uploader.py      # HTTP upload to server
│   └── storage.py       # Local config storage
├── venv/                # Python virtual environment
└── crackit              # Launcher script
```

---

## 🛠️ Troubleshooting

### "Connection Refused" Error

Your device can't reach the server. Check:
1. Server is running: `python main.py` on the server
2. Correct IP in config: `crackit setup` and enter the server's LAN IP
3. Firewall: Ensure port 8000 is open

### "scrot failed" on Raspberry Pi

```bash
# Ensure you have a display
export DISPLAY=:0

# Install scrot
sudo apt install scrot

# Test manually
scrot test.png && echo "Works!"
```

### High CPU Usage

This is rare with the new lightweight script. If it happens:
1. Increase capture interval in `config.py`
2. Reduce `IMAGE_MAX_WIDTH` to 800

---

## 📜 License

MIT License - Use responsibly.

---

## 🤝 Contributing

Pull requests welcome! For major changes, please open an issue first.

---

**Made with ❤️ for exam warriors everywhere.**
