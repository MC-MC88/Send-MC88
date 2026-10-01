# Send88

Offline local file transfer between a phone and a PC — over Wi-Fi or a hotspot.  
No internet. No cable. No cloud. Two-way.

**Copyright (c) 2026 mohamed005cheikh@gmail.com — by MC88**

---

## Requirements

- Windows PC
- Python 3.9+ (with "Add Python to PATH" checked during install)
- A phone connected to the same Wi-Fi network or hotspot as the PC

## How to use

1. Download or clone this repository.
2. Double-click `Start_Send88.bat`.
   - On the very first run, it creates a `.venv` folder and installs the dependencies automatically.
3. A QR code and a 4-digit PIN appear in the console window.
4. Scan the QR code with your phone, or open the printed URL manually.
5. Enter the PIN — the page shows **Connected**.
6. You may now disconnect your phone from the internet. It will keep working over the local network.

### Sending from phone to PC

- Open the **Send** tab.
- Tap the drop zone, pick any files, press **Send**.
- Watch live progress, speed, and estimated time remaining.
- Files land in the `received/` folder next to `send88.py`.

### Receiving from PC to phone

- Drop any file you want to share into the `shared/` folder next to `send88.py`.
- On the phone, open the **Receive** tab and tap the refresh button.
- Tap the download arrow next to any file. It saves to your phone's normal downloads.

## Notes

- The PIN is regenerated every time you start the server.
- The phone remembers the PIN for the current browser session, so you don't retype it every time.
- Files are saved with an automatic `(1)`, `(2)` suffix if a name already exists.
- Bigger files simply take longer — the ETA reflects the real transfer speed.

## Files

```
Start_Send88.bat    Launcher
send88.py           Flask server (Windows-only guard at the top)
requirements.txt    Python dependencies
index.html          Mobile UI (single-file, no build step)
README.md           This file
received/           Created automatically. Phone -> PC files land here.
shared/             Created automatically. Drop files here to serve them to the phone.
```