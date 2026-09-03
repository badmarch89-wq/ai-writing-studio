import streamlit as st
from google import genai
from google.genai import types


@st.cache_resource(show_spinner=False)
def get_client(api_key: str) -> genai.Client:
    return genai.Client(api_key=api_key)


def generate_text_stream(
    client: genai.Client,
    model: str,
    prompt: str,
    system_instruction: str | None = None,
    temperature: float = 0.7,
):
    config = types.GenerateContentConfig(
        temperature=temperature,
        system_instruction=system_instruction,
    )
    for chunk in client.models.generate_content_stream(
        model=model,
        contents=prompt,
        config=config,
    ):
        if chunk.text:
            yield chunk.text


def run_and_show(
    client: genai.Client,
    model: str,
    temperature: float,
    prompt: str,
    system_instruction: str | None = None,
) -> str:
    placeholder = st.empty()
    full_text = ""
    try:
        with st.spinner("生成中..."):
            for chunk in generate_text_stream(client, model, prompt, system_instruction, temperature):
                full_text += chunk
                placeholder.markdown(full_text)
    except Exception as e:
        st.error(f"エラーが発生しました: {e}")
        return ""

    if full_text:
        with st.expander("📋 コピー用テキスト"):
            st.code(full_text, language=None)
    return full_text
