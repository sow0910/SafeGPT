"""
desktop_app.py - Native Desktop AI Assistant Window for SafeGPT
Packages the user-facing SafeGPT chatbot as a compact, standalone desktop window
(like ChatGPT Desktop or Claude Desktop), with no browser URL bar or tabs.
"""

import os
import sys
import time
import socket
import signal
import atexit
import subprocess
import requests

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
VENV_PYTHON = os.path.join(PROJECT_DIR, "venv", "bin", "python")
CHAT_SCRIPT = os.path.join(PROJECT_DIR, "ui", "chat_app.py")
DESKTOP_PORT = 8502  # Use 8502 by default so 8501 remains free for researcher dashboard


def is_port_in_use(port: int) -> bool:
    """Check if a network port is already open."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", port)) == 0


def is_service_ready(url: str, timeout: float = 0.5) -> bool:
    """Check if the web server is answering HTTP requests."""
    try:
        r = requests.get(url, timeout=timeout)
        return r.status_code == 200
    except Exception:
        return False


def start_backend_server(port: int) -> subprocess.Popen:
    """Start Streamlit in headless background mode."""
    cmd = [
        VENV_PYTHON,
        "-m",
        "streamlit",
        "run",
        CHAT_SCRIPT,
        "--server.port",
        str(port),
        "--server.headless",
        "true",
        "--browser.gatherUsageStats",
        "false",
        "--server.address",
        "127.0.0.1",
    ]
    env = os.environ.copy()
    env["PYTHONPATH"] = PROJECT_DIR

    process = subprocess.Popen(
        cmd,
        cwd=PROJECT_DIR,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return process


def launch_native_window(target_url: str):
    """Launch a native desktop Cocoa WebKit window using pywebview."""
    import webview

    # Create compact, standalone desktop assistant window
    window = webview.create_window(
        title="SafeGPT — Private AI Assistant",
        url=target_url,
        width=540,
        height=820,
        resizable=True,
        min_size=(420, 600),
    )
    webview.start()


def launch_fallback_app_mode(target_url: str):
    """Fallback: open standalone window in Chrome app mode without browser URL or tabs."""
    chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    if os.path.exists(chrome_path):
        subprocess.run([
            chrome_path,
            f"--app={target_url}",
            "--window-size=540,820"
        ])
    else:
        # Default open
        subprocess.run(["open", target_url])


def main():
    target_port = DESKTOP_PORT
    server_process = None

    # Check if target port is already running our chat app
    target_url = f"http://localhost:{target_port}"
    if not is_service_ready(target_url):
        # If port 8502 is busy with something else, find next available port
        if is_port_in_use(target_port):
            for p in range(8503, 8520):
                if not is_port_in_use(p):
                    target_port = p
                    target_url = f"http://localhost:{target_port}"
                    break

        print(f"🚀 Starting SafeGPT Chatbot backend on port {target_port}...")
        server_process = start_backend_server(target_port)

        # Cleanup on exit
        def cleanup():
            if server_process and server_process.poll() is None:
                try:
                    server_process.terminate()
                    server_process.wait(timeout=2)
                except Exception:
                    server_process.kill()

        atexit.register(cleanup)

        # Wait for server to be responsive
        max_retries = 30
        for _ in range(max_retries):
            if is_service_ready(target_url):
                break
            time.sleep(0.2)

    print(f"🖥️  Opening SafeGPT Desktop Assistant Window...")
    try:
        launch_native_window(target_url)
    except Exception as exc:
        print(f"Native window engine notice ({exc}). Launching standalone desktop mode...")
        launch_fallback_app_mode(target_url)

    if server_process and server_process.poll() is None:
        server_process.terminate()


if __name__ == "__main__":
    main()
