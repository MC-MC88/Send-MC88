# send88.py
# Send88 - Offline Local File Transfer (Windows only)
# Copyright (c) 2026 mohamed005cheikh@gmail.com | by MC88
# Bidirectional: phone <-> PC over a local network or hotspot.

import sys
import platform

if platform.system() != "Windows":
    print("=" * 56)
    print(" Send88 only runs on Windows.")
    print(" Your OS was detected as: " + platform.system())
    print("=" * 56)
    sys.exit(1)

import os
import socket
import secrets
import hmac
import logging
from datetime import datetime

try:
    from flask import Flask, request, jsonify, send_from_directory
    from flask_cors import CORS
except ImportError:
    print("Missing dependency. Run:  pip install -r requirements.txt")
    sys.exit(1)

APP_DIR      = os.path.dirname(os.path.abspath(__file__))
RECEIVED_DIR = os.path.join(APP_DIR, "received")
SHARED_DIR   = os.path.join(APP_DIR, "shared")
os.makedirs(RECEIVED_DIR, exist_ok=True)
os.makedirs(SHARED_DIR, exist_ok=True)

app = Flask(__name__)
CORS(app)
app.config["MAX_CONTENT_LENGTH"] = None  # unlimited upload size

SESSION_PIN = f"{secrets.randbelow(9000) + 1000}"


def check_pin():
    """Header-only PIN check (used by JSON endpoints)."""
    supplied = request.headers.get("X-Auth-Pin", "")
    return hmac.compare_digest(supplied, SESSION_PIN)


def pin_from_request():
    """Accept PIN from header (fetch) or query string (download links)."""
    supplied = request.headers.get("X-Auth-Pin") or request.args.get("pin", "")
    return hmac.compare_digest(supplied, SESSION_PIN)


def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("10.255.255.255", 1))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def unique_path(directory, filename):
    base, ext = os.path.splitext(filename)
    candidate = os.path.join(directory, filename)
    counter = 1
    while os.path.exists(candidate):
        candidate = os.path.join(directory, f"{base} ({counter}){ext}")
        counter += 1
    return candidate


def human_size(num_bytes):
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if num_bytes < 1024:
            return f"{num_bytes:.2f} {unit}"
        num_bytes /= 1024.0
    return f"{num_bytes:.2f} PB"


def print_qr(url):
    try:
        import qrcode
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=1,
            border=2,
        )
        qr.add_data(url)
        qr.make(fit=True)
        print("\n=== SCAN TO CONNECT ===")
        qr.print_ascii(invert=True)
        print("=======================\n")
    except ImportError:
        print("(Install 'qrcode' to also get a scannable QR code.)\n")


# ----------------------------------------------------------------------
# Routes
# ----------------------------------------------------------------------

@app.route("/")
def serve_index():
    return send_from_directory(APP_DIR, "index.html")


@app.route("/ping", methods=["GET"])
def ping():
    return jsonify({"status": "active"}), 200


@app.route("/auth", methods=["POST"])
def auth():
    data = request.get_json(silent=True) or {}
    pin = str(data.get("pin", ""))
    if hmac.compare_digest(pin, SESSION_PIN):
        return jsonify({"success": True}), 200
    return jsonify({"success": False, "error": "Wrong PIN"}), 401


@app.route("/upload", methods=["POST"])
def upload():
    """Phone -> PC."""
    if not check_pin():
        return jsonify({"success": False, "error": "Unauthorized"}), 401

    uploaded = request.files.getlist("files")
    if not uploaded:
        return jsonify({"success": False, "error": "No files received"}), 400

    saved = []
    stamp = datetime.now().strftime("%H:%M:%S")

    for f in uploaded:
        if not f or not f.filename:
            continue
        safe_name = os.path.basename(f.filename).replace("\x00", "").strip() or "unnamed"
        target = unique_path(RECEIVED_DIR, safe_name)
        f.save(target)
        size = os.path.getsize(target)
        saved.append({"name": os.path.basename(target), "size": size})
        print(f"  [{stamp}]  [>]  Phone -> PC  ·  {os.path.basename(target):<40} {human_size(size)}")

    if saved:
        print(f"  [{stamp}]  Done. {len(saved)} file(s) received.\n")

    return jsonify({"success": True, "files": saved}), 200


@app.route("/list-shared", methods=["GET"])
def list_shared():
    """Return the list of files the PC offers to the phone."""
    if not check_pin():
        return jsonify({"success": False, "error": "Unauthorized"}), 401

    items = []
    try:
        for name in sorted(os.listdir(SHARED_DIR)):
            p = os.path.join(SHARED_DIR, name)
            if os.path.isfile(p):
                items.append({"name": name, "size": os.path.getsize(p)})
    except OSError:
        pass
    return jsonify({"success": True, "files": items}), 200


@app.route("/download/<path:name>", methods=["GET"])
def download(name):
    """PC -> Phone."""
    if not pin_from_request():
        return jsonify({"success": False, "error": "Unauthorized"}), 401

    safe = os.path.basename(name)
    target = os.path.join(SHARED_DIR, safe)
    if not os.path.isfile(target):
        return jsonify({"success": False, "error": "Not found"}), 404

    stamp = datetime.now().strftime("%H:%M:%S")
    print(f"  [{stamp}]  [<]  PC -> Phone  ·  {safe:<40} {human_size(os.path.getsize(target))}")
    return send_from_directory(SHARED_DIR, safe, as_attachment=True)


# ----------------------------------------------------------------------
# Entry point
# ----------------------------------------------------------------------

if __name__ == "__main__":
    server_ip = get_local_ip()
    port = 8888
    url = f"http://{server_ip}:{port}"

    print("\n" + "+" + "-" * 58 + "+")
    print("|" + "SEND88 - LOCAL FILE TRANSFER".center(58) + "|")
    print("+" + "-" * 58 + "+")
    print("| Open on your phone (same Wi-Fi / hotspot):             |")
    print(f"| {url:<55} |")
    print("+" + "-" * 58 + "+")
    print(f"| PIN: {SESSION_PIN:<51} |")
    print("+" + "-" * 58 + "+")
    print("| Phone  ->  PC    :  ./received/                        |")
    print("| PC     ->  Phone :  ./shared/                          |")
    print("+" + "-" * 58 + "+")
    print("| Tip: drop files into ./shared/ to make them available  |")
    print("|      to your phone. Refresh from the app.              |")
    print("+" + "-" * 58 + "+")

    print_qr(url)

    log = logging.getLogger("werkzeug")
    log.setLevel(logging.ERROR)
    print("Server is running. Press Ctrl+C to stop.\n")
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)