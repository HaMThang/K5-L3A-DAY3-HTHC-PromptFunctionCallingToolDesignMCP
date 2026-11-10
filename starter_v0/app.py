"""Run with: python -m streamlit run app.py"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import streamlit as st

from chat import run_model_tool_loop, trim_history
from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import file_hash, short_hash


ROOT = Path(__file__).resolve().parent
PROMPT_PATH = ROOT / "artifacts" / "system_prompt.md"
TOOLS_PATH = ROOT / "artifacts" / "tools.yaml"
POSTER_PATH = ROOT / "artifacts" / "Poster.png"
PROVIDER_NAME = "openrouter"
DEFAULT_MODEL = "openai/gpt-4o-mini"

st.set_page_config(
    page_title="AI & Tech Research Agent",
    page_icon="🔎",
    layout="centered",
    initial_sidebar_state="expanded",
)
load_lab_env(ROOT)

# Friendly labels for tool calls shown in the chat.
TOOL_LABELS: dict[str, tuple[str, str]] = {
    "clarify": ("🙋", "Hỏi lại người dùng"),
    "timeline": ("🐦", "Lấy tweet của một tài khoản"),
    "social_search": ("💬", "Tìm tweet theo chủ đề"),
    "lookup": ("🌐", "Tìm trên web"),
    "fetch": ("🔗", "Đọc nội dung URL"),
    "format": ("📝", "Trình bày bản tin"),
    "send": ("📤", "Gửi lên Telegram"),
    "policy": ("🏢", "Tra quy định nội bộ"),
    "papers": ("📄", "Tìm paper arXiv"),
    "paper_text": ("📑", "Đọc nội dung paper"),
    "cite_sources": ("📌", "Đối chiếu nguồn trích dẫn"),
    "google_maps": ("📍", "Tạo link Google Maps"),
}

EXAMPLES: list[tuple[str, str]] = [
    ("📰", "Tin tức AI hôm nay có gì nổi bật?"),
    ("🐦", "Tweet mới nhất của Sam Altman là gì?"),
    ("💬", "Mọi người đang bàn gì về GPT-5 trên Twitter?"),
    ("📄", "Tìm 3 paper trên arXiv về AI agent evaluation"),
    ("🏢", "Quy định nội bộ có cho dùng tweet làm nguồn chính thức không?"),
    ("📍", "Tạo link Google Maps cho 135 Nam Kỳ Khởi Nghĩa, TP. Hồ Chí Minh"),
]


# ---------------- state ----------------

def reset_conversation() -> None:
    st.session_state.history = []
    st.session_state.display_messages = []


def queue_prompt(text: str) -> None:
    st.session_state.pending_prompt = text


for key, default in (("history", []), ("display_messages", []), ("pending_prompt", None)):
    if key not in st.session_state:
        st.session_state[key] = default


# ---------------- sidebar ----------------

with st.sidebar:
    st.header("🔎 Research Agent")
    st.button("➕ Cuộc trò chuyện mới", on_click=reset_conversation, type="primary", width="stretch")

    if POSTER_PATH.is_file():
        with st.expander("Giới thiệu agent", icon="🖼️"):
            st.image(str(POSTER_PATH), width="stretch")

    with st.expander("Agent làm được gì?", icon="🧰"):
        for name, (icon, label) in TOOL_LABELS.items():
            st.markdown(f"{icon} **{label}** · `{name}`")
        st.caption("Gửi tin lên Telegram luôn cần bạn xác nhận trước.")

    with st.expander("Cài đặt", icon="⚙️"):
        st.caption(f"Provider: **OpenRouter**")
        model = st.text_input("Model", placeholder=DEFAULT_MODEL, help="Để trống để dùng model mặc định.").strip()
        try:
            st.caption(
                f"Prompt `{short_hash(file_hash(PROMPT_PATH))}` · Tools `{short_hash(file_hash(TOOLS_PATH))}`"
            )
        except OSError:
            pass
        st.caption("Transcript cho report: chạy `chat.py`.")

if st.session_state.get("selected_model") != model:
    reset_conversation()
    st.session_state.selected_model = model


# ---------------- rendering helpers ----------------

def summarize_result(result: Any) -> str:
    """One short line describing a tool result, without leaking raw details."""
    if not isinstance(result, dict):
        return "Đã chạy xong."
    if result.get("error"):
        message = str(result.get("message", ""))
        if "env var" in message or "Missing" in message:
            return "⚠️ Công cụ này chưa được cấu hình API key."
        return f"⚠️ Lỗi: {result['error']}"
    if result.get("awaiting_user"):
        return "Đang chờ bạn trả lời."
    if "items" in result:
        return f"{len(result['items'])} kết quả."
    if "results" in result:
        return f"{len(result['results'])} mục phù hợp."
    if result.get("url"):
        return f"[Mở link]({result['url']})"
    if result.get("status"):
        return f"Trạng thái: {result['status']}."
    return "Đã chạy xong."


def show_tool_events(events: list[dict[str, Any]]) -> None:
    visible = [event for event in events if event.get("tool") != "clarify"]
    if not visible:
        return
    names = ", ".join(TOOL_LABELS.get(event["tool"], ("🔧", event["tool"]))[1] for event in visible)
    with st.expander(f"🔧 Đã dùng {len(visible)} công cụ: {names}"):
        for event in visible:
            icon, label = TOOL_LABELS.get(event["tool"], ("🔧", event["tool"]))
            st.markdown(f"**{icon} {label}** · `{event['tool']}`")
            args = {k: v for k, v in (event.get("args") or {}).items() if not str(k).startswith("_")}
            if args:
                st.caption(" · ".join(f"{k} = {v!r}" for k, v in args.items()))
            st.markdown(summarize_result(event.get("result")))
            st.json(event.get("result", {}), expanded=False)


def clarify_request(events: list[dict[str, Any]]) -> dict[str, Any] | None:
    for event in reversed(events or []):
        result = event.get("result")
        if isinstance(result, dict) and result.get("awaiting_user"):
            return result
    return None


def show_quick_replies(message: dict[str, Any], key_prefix: str) -> None:
    request = clarify_request(message.get("tool_events", []))
    if not request:
        return
    if request.get("response_type") == "yes_no":
        options = ["Có, tiếp tục", "Không, huỷ"]
    elif request.get("response_type") == "choice" and request.get("options"):
        options = [str(option) for option in request["options"]]
    else:
        st.caption("✍️ Trả lời ở ô chat bên dưới để agent tiếp tục.")
        return
    columns = st.columns(len(options))
    for index, (column, option) in enumerate(zip(columns, options)):
        column.button(option, key=f"{key_prefix}-reply-{index}", on_click=queue_prompt, args=(option,), width="stretch")


def show_message(message: dict[str, Any], *, key_prefix: str, is_last: bool) -> None:
    avatar = "🧑" if message["role"] == "user" else "🔎"
    with st.chat_message(message["role"], avatar=avatar):
        if message.get("status") == "waiting_for_user":
            st.info(message["content"], icon="🙋")
        elif message.get("status") == "error":
            st.error(message["content"], icon="⚠️")
        else:
            st.markdown(message["content"])
        if message.get("tool_events"):
            show_tool_events(message["tool_events"])
        if message.get("status") == "max_tool_rounds":
            st.warning("Agent đã dùng hết số vòng công cụ cho phép. Hãy hỏi cụ thể hơn.", icon="⏱️")
        if is_last and message.get("status") == "waiting_for_user":
            show_quick_replies(message, key_prefix)


# ---------------- main ----------------

st.title("AI & Tech Research Agent")
st.caption("Tìm tin trên web và Twitter, đọc link, tra paper, rồi tóm tắt bằng tiếng Việt.")

messages_to_show = st.session_state.display_messages
for index, message in enumerate(messages_to_show):
    show_message(message, key_prefix=f"m{index}", is_last=index == len(messages_to_show) - 1)

if not messages_to_show:
    with st.container(border=True):
        st.markdown("#### 👋 Bắt đầu nhanh")
        st.caption("Chọn một câu hỏi mẫu, hoặc gõ câu của bạn ở ô bên dưới.")
        columns = st.columns(2)
        for index, (icon, text) in enumerate(EXAMPLES):
            columns[index % 2].button(
                f"{icon} {text}", key=f"example-{index}", on_click=queue_prompt, args=(text,), width="stretch"
            )

typed = st.chat_input("Bạn muốn tìm hiểu gì?")
user_text = typed or st.session_state.pending_prompt
st.session_state.pending_prompt = None

if user_text and user_text.strip():
    user_message = {"role": "user", "content": user_text.strip()}
    show_message(user_message, key_prefix="new-user", is_last=False)
    try:
        system_prompt = PROMPT_PATH.read_text(encoding="utf-8")
        tools = to_openai_tools(load_tool_declarations(TOOLS_PATH))
        provider = make_provider(PROVIDER_NAME)
        messages = [
            {"role": "system", "content": system_prompt},
            *trim_history(st.session_state.history, 5),
            user_message,
        ]
        with st.spinner("Đang nghiên cứu…"):
            result = run_model_tool_loop(
                provider=provider,
                messages=messages,
                tools=tools,
                model=model or None,
                max_tool_rounds=4,
            )
    except Exception:
        # Provider exceptions can contain request details; keep them off the public UI.
        assistant_message = {
            "role": "assistant",
            "content": "Không gửi được yêu cầu. Kiểm tra API key, model và kết nối mạng rồi thử lại.",
            "status": "error",
        }
        st.session_state.display_messages.extend([user_message, assistant_message])
    else:
        assistant_message = {
            "role": "assistant",
            "content": result["assistant_text"] or "Agent chưa có câu trả lời. Hãy thử hỏi cụ thể hơn.",
            "tool_events": result["tool_events"],
            "status": result["status"],
        }
        st.session_state.history.extend([
            user_message,
            {"role": "assistant", "content": assistant_message["content"]},
        ])
        st.session_state.display_messages.extend([user_message, assistant_message])
    st.rerun()
