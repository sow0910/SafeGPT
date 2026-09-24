"""
app.py - SafeGPT Application Entrypoint

Usage:
  python app.py              -> Launches the Native Desktop Assistant Window (Default)
  python app.py --web        -> Launches the consumer chat interface in browser
  python app.py --dashboard  -> Launches the researcher / auditor benchmark dashboard
  python app.py --cli        -> Runs the interactive terminal CLI pipeline
"""

import sys
import subprocess
import os


def launch_desktop():
    """Launch the compact, standalone desktop AI assistant application."""
    desktop_script = os.path.join(os.path.dirname(__file__), "desktop_app.py")
    cmd = [sys.executable, desktop_script]
    print(f"🚀 Starting SafeGPT Desktop Assistant Window...")
    subprocess.run(cmd)


def launch_chat():
    """Launch the consumer chat interface in the default browser."""
    chat_path = os.path.join(os.path.dirname(__file__), "ui", "chat_app.py")
    cmd = [sys.executable, "-m", "streamlit", "run", chat_path]
    print(f"🚀 Starting SafeGPT Chatbot in Browser...")
    print(f"Command: {' '.join(cmd)}")
    subprocess.run(cmd)


def launch_admin():
    admin_path = os.path.join(os.path.dirname(__file__), "ui", "admin_dashboard.py")
    cmd = [sys.executable, "-m", "streamlit", "run", admin_path]
    print(f"🛡️ Starting SafeGPT Enterprise Review Console...")
    print(f"Command: {' '.join(cmd)}")
    subprocess.run(cmd)


def launch_dashboard():
    dashboard_path = os.path.join(os.path.dirname(__file__), "ui", "dashboard.py")
    cmd = [sys.executable, "-m", "streamlit", "run", dashboard_path]
    print(f"📊 Starting SafeGPT Auditor & Research Dashboard...")
    print(f"Command: {' '.join(cmd)}")
    subprocess.run(cmd)


def run_cli():
    from pipeline import process_prompt
    print("\n" + "=" * 60)
    print("      🛡️  SafeGPT Interactive Terminal CLI Mode  🛡️      ")
    print("=" * 60)
    user_prompt = input("Enter your prompt: ")
    detections, masked_prompt, response = process_prompt(user_prompt)

    print("\n--- PII DETECTION ---")
    if detections:
        categories = sorted(list(set(item["label"] for item in detections)))
        print(f"Detected PII ({len(detections)} items): {', '.join(categories)}")
    else:
        print("No PII detected.")

    print("\n--- MASKED PROMPT (sent to local Llama 3) ---")
    print(masked_prompt)

    print("\n--- FINAL RESTORED RESPONSE ---")
    print(response)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--cli":
        run_cli()
    elif len(sys.argv) > 1 and sys.argv[1] == "--admin":
        launch_admin()
    elif len(sys.argv) > 1 and sys.argv[1] == "--dashboard":
        launch_dashboard()
    elif len(sys.argv) > 1 and sys.argv[1] == "--web":
        launch_chat()
    else:
        launch_desktop()

