# 🎯 Crackit - AI-Powered Exam Assistant

> **Capture your screen, get AI-powered answers instantly via Telegram.**

Crackit is a lightweight screen capture tool that streams your display to a backend server, which uses Vision AI to detect questions and deliver solutions directly to your Telegram.

---

## 🚀 One-Line Installation

```bash
curl -fsSL https://raw.githubusercontent.com/igaurav-dev/crackit-script/main/install.sh | bash
```

This installs Crackit to `~/.crackit` and adds the `crackit` command to your PATH.

---

## 📖 How It Works

```
┌─────────────────────────────────────────────────────────────────────┐
│                           YOUR DEVICE (Pi/Mac/Linux)                │
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
│  │    WebSocket Broadcast to React Dashboard (Live View)       │   │
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

### 1. Setup Your Token

```bash
crackit setup
```

You'll be prompted for:
- **API Token**: Get this from the Crackit dashboard
- **API Endpoint**: Your server URL (e.g., `http://192.168.1.34:8000`)

### 2. Link Telegram (Optional but Recommended)

1. Open Telegram and search for your Crackit Bot
2. Click the deep link from your dashboard
3. The bot will confirm when linked

---

## 🎮 Usage

### Start the Service

```bash
crackit start
```

This starts background screen capture. Your screen is now streaming to the server.

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

---

## 🖥️ Supported Platforms

| Platform | Status | Notes |
|----------|--------|-------|
| **Linux (Raspberry Pi)** | ✅ Fully Supported | Uses `scrot` for capture |
| **macOS** | ✅ Fully Supported | Uses native `mss` |
| **Windows** | ⚠️ Experimental | Requires manual start |

### Linux/Raspberry Pi Prerequisites

```bash
# Install screen capture tool
sudo apt install scrot

# For Wayland (newer Raspberry Pi OS)
sudo apt install grim
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
