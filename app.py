import os

import streamlit as st
from dotenv import load_dotenv

from gemini_client import get_client
from style import CUSTOM_CSS
from tools import (
    render_blog_writer,
    render_email_reply,
    render_proofreader,
    render_summarizer,
    render_title_generator,
    render_tone_converter,
    render_translator,
)

load_dotenv()

st.set_page_config(page_title="AI Writing Studio", page_icon="✍️", layout="wide")
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

HOME_KEY = "🏠 ホーム"

TOOLS = {
    "📝 ブログ記事作成": {
        "render": render_blog_writer,
        "desc": "テーマとキーワードから、構成の整ったブログ記事を自動生成します。",
    },
    "✉️ メール返信文作成": {
        "render": render_email_reply,
        "desc": "受信メールと伝えたい要点から、そのまま送れる返信文を作成します。",
    },
    "📄 要約": {
        "render": render_summarizer,
        "desc": "長い文章を、箇条書きや任意の長さで簡潔に要約します。",
    },
    "✅ 校正・誤字脱字チェック": {
        "render": render_proofreader,
        "desc": "誤字脱字や不自然な言い回しを検出し、修正案を提示します。",
    },
    "🎭 トーン変換": {
        "render": render_tone_converter,
        "desc": "同じ内容のまま、丁寧語・カジュアルなど文体を変換します。",
    },
    "💡 タイトル・見出し提案": {
        "render": render_title_generator,
        "desc": "記事内容から、目を引くタイトル候補を複数提案します。",
    },
    "🌐 翻訳": {
        "render": render_translator,
        "desc": "多言語への翻訳を、フォーマル/カジュアルの文体指定つきで行います。",
    },
}

MODEL_OPTIONS = {
    "Gemini 3.6 Flash（速い・普段使い）": "gemini-3.6-flash",
    "Gemini 3.1 Pro（高精度・じっくり）": "gemini-3.1-pro-preview",
}

if "page" not in st.session_state:
    st.session_state["page"] = HOME_KEY


def go_to(tool_key: str):
    st.session_state["page"] = tool_key
    st.rerun()


with st.sidebar:
    st.markdown("## ✍️ AI Writing Studio")

    env_api_key = os.getenv("GEMINI_API_KEY")
    if env_api_key:
        api_key = env_api_key
        st.caption("API Key: 環境変数から読み込み済み")
    else:
        api_key = st.text_input(
            "Gemini API Key",
            type="password",
            value=st.session_state.get("api_key", ""),
            help="環境変数 GEMINI_API_KEY が設定されていないため、ここに入力してください。",
        )
        st.session_state["api_key"] = api_key

    st.divider()
    nav_options = [HOME_KEY] + list(TOOLS.keys())
    selected_nav = st.radio(
        "ナビゲーション",
        nav_options,
        index=nav_options.index(st.session_state["page"]),
    )
    if selected_nav != st.session_state["page"]:
        st.session_state["page"] = selected_nav
        st.rerun()

    st.divider()
    model_label = st.selectbox("モデル", list(MODEL_OPTIONS.keys()))
    model = MODEL_OPTIONS[model_label]
    temperature = st.slider("創造性（temperature）", 0.0, 1.5, 0.7, 0.1)

current = st.session_state["page"]

if current == HOME_KEY:
    st.markdown(
        """
        <div class="home-hero">
            <h1>✍️ AI Writing Studio</h1>
            <div class="home-hero-sub">Gemini 搭載・オールインワン ライティングアシスタント</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tool_keys = list(TOOLS.keys())
    cols_per_row = 3
    for i in range(0, len(tool_keys), cols_per_row):
        row_keys = tool_keys[i : i + cols_per_row]
        cols = st.columns(cols_per_row)
        for col, key in zip(cols, row_keys):
            info = TOOLS[key]
            icon, title = key.split(" ", 1)
            with col:
                with st.container(border=True):
                    st.markdown(
                        f"""
                        <div style="text-align:center;">
                            <div class="tool-card-icon">{icon}</div>
                            <div class="tool-card-title">{title}</div>
                            <div class="tool-card-desc">{info['desc']}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    if st.button("開く →", key=f"open_{key}", use_container_width=True):
                        go_to(key)
else:
    if st.button("← ホームに戻る"):
        go_to(HOME_KEY)

    st.title(current)

    if not api_key:
        st.warning("サイドバーに Gemini API Key を入力してください。")
        st.stop()

    client = get_client(api_key)
    TOOLS[current]["render"](client, model, temperature)
