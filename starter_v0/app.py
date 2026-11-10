"""Run with: python -m streamlit run app.py"""

from pathlib import Path

import streamlit as st

from chat import run_model_tool_loop, trim_history
from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools


ROOT = Path(__file__).resolve().parent
st.set_page_config(page_title="Research Agent", page_icon="🔎")
load_lab_env(ROOT)

st.title("🔎 Research Agent")
st.caption("Research the web, explore sources, and ask follow-up questions.")

with st.sidebar:
    st.header("Chat settings")
    st.caption("Provider: OpenRouter")
    model = st.text_input("Model (leave blank for the provider default)").strip()
    if st.button("New conversation", use_container_width=True):
        st.session_state.history = []
        st.session_state.display_messages = []
        st.rerun()
    st.caption("Use chat.py to save the live-chat transcripts required for your report.")

if "history" not in st.session_state:
    st.session_state.history = []
if "display_messages" not in st.session_state:
    st.session_state.display_messages = []
if st.session_state.get("selected_model") != model:
    st.session_state.history = []
    st.session_state.display_messages = []
    st.session_state.selected_model = model


def show_message(message):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("tool_events"):
            with st.expander("Tool calls and results"):
                st.json(message["tool_events"])
        if message.get("status") == "waiting_for_user":
            st.caption("Reply below to continue.")
        elif message.get("status") == "max_tool_rounds":
            st.warning("The tool-round limit was reached. Review the results or narrow your request.")


for message in st.session_state.display_messages:
    show_message(message)

if user_text := st.chat_input("What would you like to research?"):
    if not user_text.strip():
        st.stop()
    user_message = {"role": "user", "content": user_text}
    show_message(user_message)
    try:
        system_prompt = (ROOT / "artifacts" / "system_prompt.md").read_text(encoding="utf-8")
        tools = to_openai_tools(load_tool_declarations(ROOT / "artifacts" / "tools.yaml"))
        provider = make_provider("openrouter")
        messages = [
            {"role": "system", "content": system_prompt},
            *trim_history(st.session_state.history, 5),
            user_message,
        ]
        with st.spinner("Researching…"):
            result = run_model_tool_loop(
                provider=provider,
                messages=messages,
                tools=tools,
                model=model or None,
                max_tool_rounds=4,
            )
    except Exception:
        # Provider exceptions can contain request details; keep them off the public UI.
        st.error("The request could not be completed. Check your local API configuration, model, and connection, then try again.")
    else:
        assistant_message = {
            "role": "assistant",
            "content": result["assistant_text"] or "No answer was returned. Please try a more specific request.",
            "tool_events": result["tool_events"],
            "status": result["status"],
        }
        st.session_state.history.extend([
            user_message,
            {"role": "assistant", "content": assistant_message["content"]},
        ])
        st.session_state.display_messages.extend([user_message, assistant_message])
        show_message(assistant_message)
