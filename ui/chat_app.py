"""
chat_app.py - Consumer Chatbot Interface for SafeGPT
A modern, minimalist, ChatGPT-like conversational AI assistant.
"""

import os
import sys
import time
from typing import Generator
import streamlit as st

# SafeGPT Core Backend Modules
from pii_detector import detect_pii
from masker import mask_pii, create_pii_mapping
from demasker import restore_pii
from storage.encrypted_store import generate_key, encrypt_data, decrypt_data
from llm.llm_connector import ask_llm

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# -----------------------------------------------------------------------------
# PAGE CONFIGURATION & MINIMALIST DESKTOP STYLING
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="SafeGPT — Private AI Assistant",
    page_icon="🛡️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
    /* Dark Theme & Typography */
    .stApp {
        background-color: #0F172A;
        color: #F8FAFC;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Center the container like desktop assistant */
    .block-container {
        max-width: 680px;
        padding-top: 0.5rem;
        padding-bottom: 5.5rem;
    }
    
    /* Top Header Bar */
    .app-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 12px 6px 14px 6px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 24px;
    }
    .app-header-title {
        display: flex;
        align-items: center;
        gap: 10px;
        font-size: 1.15rem;
        font-weight: 600;
        color: #F8FAFC;
        letter-spacing: -0.01em;
    }

    /* Hero / Empty State */
    .hero-container {
        text-align: center;
        padding: 40px 10px 24px 10px;
    }
    .hero-icon {
        font-size: 3.2rem;
        margin-bottom: 14px;
        display: inline-block;
        filter: drop-shadow(0 0 16px rgba(56, 189, 248, 0.35));
    }
    .hero-title {
        font-size: 1.6rem;
        font-weight: 600;
        color: #F8FAFC;
        margin-bottom: 8px;
        letter-spacing: -0.02em;
    }
    .hero-subtitle {
        font-size: 0.88rem;
        color: #94A3B8;
        margin-bottom: 24px;
    }

    /* Subtle Privacy Notification Card below Assistant Message */
    .privacy-box {
        margin-top: 6px;
        margin-bottom: 12px;
        padding: 8px 14px;
        background: rgba(30, 41, 59, 0.55);
        border: 1px solid rgba(56, 189, 248, 0.2);
        border-radius: 10px;
        display: inline-block;
    }
    .privacy-box-title {
        font-size: 0.82rem;
        font-weight: 600;
        color: #38BDF8;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .privacy-box-sub {
        font-size: 0.75rem;
        color: #94A3B8;
        margin-top: 2px;
        margin-left: 20px;
    }
    
    .privacy-clean-badge {
        font-size: 0.78rem;
        color: #64748B;
        margin-top: 4px;
        margin-bottom: 8px;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }

    /* Chat message styling */
    .stChatMessage {
        border-radius: 12px;
        padding: 10px 14px;
        margin-bottom: 12px;
    }

    /* Bottom input area border divider */
    div[data-testid="stChatInput"] {
        border-top: 1px solid rgba(255, 255, 255, 0.1) !important;
        padding-top: 10px !important;
        background-color: #0F172A !important;
    }

    /* Clean Streamlit elements for pure native desktop look */
    header {visibility: hidden; height: 0px !important;}
    #MainMenu {visibility: hidden; display: none !important;}
    footer {visibility: hidden; height: 0px !important;}
    div[data-testid="stDecoration"] {display: none !important;}
    div[data-testid="stStatusWidget"] {display: none !important;}
    .stDeployButton {display: none !important;}
    [data-testid="stToolbar"] {visibility: hidden; height: 0px !important;}
    [data-testid="stHeader"] {display: none !important;}
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# SESSION STATE INITIALIZATION
# -----------------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "privacy_meta" not in st.session_state:
    st.session_state.privacy_meta = {}

if "preset_prompt" not in st.session_state:
    st.session_state.preset_prompt = None


def new_chat():
    st.session_state.messages = []
    st.session_state.privacy_meta = {}
    st.session_state.preset_prompt = None


# -----------------------------------------------------------------------------
# TOP APP BAR (┌─────────────────────────────────────┐)
# -----------------------------------------------------------------------------
col_title, col_tools = st.columns([5, 1])

with col_title:
    st.markdown("""
    <div class="app-header-title">
        <span>🛡️</span> SafeGPT — Private AI Assistant
    </div>
    """, unsafe_allow_html=True)

with col_tools:
    with st.popover("⚙", use_container_width=True):
        st.markdown("**🛡️ SafeGPT**")
        st.caption("Private AI Assistant • Local Processing")
        if st.button("➕ New Chat", use_container_width=True):
            new_chat()
            st.rerun()
        st.markdown("---")
        st.markdown("""
        **Privacy Engine Status**
        - 🟢 Hybrid PII Protection: Active
        - 🟢 Local AI (Llama 3): Connected
        - 🟢 Storage: AES-256-GCM
        """)

# Top border divider (├─────────────────────────────────────┤)
st.markdown("<div style='border-bottom: 1px solid rgba(255, 255, 255, 0.1); margin-top: 4px; margin-bottom: 18px;'></div>", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# STREAMING GENERATOR FOR SMOOTH CHATGPT-LIKE TYPING
# -----------------------------------------------------------------------------
def stream_words(text: str) -> Generator[str, None, None]:
    """Stream response word-by-word smoothly."""
    words = text.split(" ")
    for i, word in enumerate(words):
        yield word + (" " if i < len(words) - 1 else "")
        time.sleep(0.015)


# -----------------------------------------------------------------------------
# HERO EMPTY STATE (WHEN CHAT IS EMPTY)
# -----------------------------------------------------------------------------
if len(st.session_state.messages) == 0:
    st.markdown("""
    <div class="hero-container">
        <div class="hero-icon">🛡️</div>
        <div class="hero-title">How can I help you today?</div>
        <div class="hero-subtitle">Chat naturally. SafeGPT automatically protects sensitive information before AI processing.</div>
    </div>
    """, unsafe_allow_html=True)

    # Clean starter suggestions [ Try something... ]
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🪪 Try: Ask about Aadhaar status", use_container_width=True):
            st.session_state.preset_prompt = "My name is Ananya Iyer and my Aadhaar is 2222 3333 4444. What is Aadhaar used for?"
            st.rerun()
        if st.button("💳 Try: Verify PAN card format", use_container_width=True):
            st.session_state.preset_prompt = "My name is Arjun Menon and my PAN is ABCDE1234F. Is this valid?"
            st.rerun()
    with col2:
        if st.button("📧 Try: Contact query with email & phone", use_container_width=True):
            st.session_state.preset_prompt = "My email is user@example.com and phone is +91-98765-43210. How can I reach support?"
            st.rerun()
        if st.button("💡 Try: Explain Machine Learning", use_container_width=True):
            st.session_state.preset_prompt = "What is machine learning in simple terms?"
            st.rerun()


# -----------------------------------------------------------------------------
# CONVERSATION STREAM
# -----------------------------------------------------------------------------
for idx, message in enumerate(st.session_state.messages):
    role = message["role"]
    content = message["content"]

    if role == "user":
        with st.chat_message("user", avatar="👤"):
            st.markdown(content)
    else:
        with st.chat_message("assistant", avatar="🛡️"):
            st.markdown(content)

            # Subtle privacy notification matching wireframe
            meta = st.session_state.privacy_meta.get(idx)
            if meta:
                if meta["has_pii"]:
                    st.markdown("""
                    <div class="privacy-box">
                        <div class="privacy-box-title">🔒 Sensitive information</div>
                        <div class="privacy-box-sub">protected before AI processing</div>
                    </div>
                    """, unsafe_allow_html=True)
                    with st.expander("Details", expanded=False):
                        st.markdown("""
                        - ✓ Sensitive information detected
                        - ✓ Sensitive information masked
                        - ✓ Protected before AI processing
                        - ✓ Local AI processing enabled
                        """)
                else:
                    st.markdown('<div class="privacy-clean-badge">🛡️ Privacy Protected</div>', unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# INPUT BOX (FIXED AT BOTTOM: Message SafeGPT... ↑)
# -----------------------------------------------------------------------------
active_input = st.session_state.preset_prompt
if active_input:
    st.session_state.preset_prompt = None
    user_input = active_input
else:
    user_input = st.chat_input("Message SafeGPT...")

if user_input:
    # 1. Render and record User Message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)

    # 2. Run through SafeGPT Privacy Pipeline
    with st.chat_message("assistant", avatar="🛡️"):
        with st.spinner("SafeGPT is thinking..."):
            # Step A: Hybrid PII Detection
            detections = detect_pii(user_input)

            # Step B: Masking & Encrypted Mapping
            if detections:
                masked_prompt = mask_pii(user_input, detections)
                mapping = create_pii_mapping(detections)
                key = generate_key()
                encrypted_payload = encrypt_data(mapping, key)
            else:
                masked_prompt = user_input
                mapping = None
                key = None
                encrypted_payload = None

            # Step C: Local Llama 3 Inference
            try:
                raw_response = ask_llm(masked_prompt)
            except Exception as exc:
                raw_response = f"I'm sorry, I could not connect to local Llama 3 ({exc}). Please ensure Ollama is running."

            # Step D: Controlled De-masking / Restoration
            if detections and mapping and key:
                decrypted_mapping = decrypt_data(encrypted_payload, key)
                final_response = restore_pii(raw_response, decrypted_mapping)
            else:
                final_response = raw_response

        # Step E: Stream Final Restored Response
        st.write_stream(stream_words(final_response))

        # Record message and metadata
        assistant_idx = len(st.session_state.messages)
        st.session_state.messages.append({"role": "assistant", "content": final_response})
        st.session_state.privacy_meta[assistant_idx] = {
            "has_pii": bool(detections),
            "pii_count": len(detections) if detections else 0,
        }

        # Subtle Privacy Notification matching wireframe
        if detections:
            st.markdown("""
            <div class="privacy-box">
                <div class="privacy-box-title">🔒 Sensitive information</div>
                <div class="privacy-box-sub">protected before AI processing</div>
            </div>
            """, unsafe_allow_html=True)
            with st.expander("Details", expanded=False):
                st.markdown("""
                - ✓ Sensitive information detected
                - ✓ Sensitive information masked
                - ✓ Protected before AI processing
                - ✓ Local AI processing enabled
                """)
        else:
            st.markdown('<div class="privacy-clean-badge">🛡️ Privacy Protected</div>', unsafe_allow_html=True)
