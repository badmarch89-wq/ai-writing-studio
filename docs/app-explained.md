# `app.py`解説記事：このアプリはどう動いているのか

`app.py`は、AIライティングツール全体の「司令塔」です。141行というコンパクトさですが、①画面全体の設定、②サイドバー、③ホーム画面とツール画面の切り替え、という3つの役割を担っています。上から順に見ていきます。

## 1. インポート（1〜16行目）

```python
import os
import streamlit as st
from dotenv import load_dotenv

from gemini_client import get_client
from style import CUSTOM_CSS
from tools import (render_blog_writer, render_email_reply, ...)
```

- `streamlit as st` — 画面のUI部品（ボタン、テキスト入力など）を作るライブラリ本体
- `load_dotenv` — `.env`ファイルからAPIキーなどの環境変数を読み込む関数
- `get_client` / `CUSTOM_CSS` / `render_*` — それぞれ`gemini_client.py`・`style.py`・`tools.py`という別ファイルで定義した部品を取り込んでいます

このアプリは「app.py が全部やる」のではなく、**各ファイルが専門分野を持ち、app.pyがそれらを組み合わせて画面にする**という作りになっています。

## 2. 画面の初期設定（18〜21行目）

```python
load_dotenv()
st.set_page_config(page_title="AI Writing Studio", page_icon="✍️", layout="wide")
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
```

- `.env`を読み込む
- ブラウザのタブタイトルやアイコン、レイアウト幅を設定する
- `style.py`で作った白基調＋グラデーションのCSSをページに注入する

`st.markdown(..., unsafe_allow_html=True)`は「本来Streamlitが許さない自由なHTML/CSSを、あえて許可して差し込む」ための書き方です。デザインをカスタムするときの定番テクニックです。

## 3. ツール一覧の定義（23〜59行目）

```python
TOOLS = {
    "📝 ブログ記事作成": {
        "render": render_blog_writer,
        "desc": "テーマとキーワードから...",
    },
    ...
}
```

ここが重要なポイントです。`TOOLS`は**「表示名」→「その画面を描画する関数＋説明文」**の対応表（辞書）になっています。

- `"render": render_blog_writer` の部分に注目してください。Pythonでは関数そのものを値として辞書に入れられます。つまり`TOOLS["📝 ブログ記事作成"]["render"]`と書くと、`render_blog_writer`という関数（の実体）が取り出せます。これを後で`(client, model, temperature)`を渡して**呼び出す**ことで、そのツールの画面が描かれます。

`MODEL_OPTIONS`も同じ発想で、「表示用の日本語ラベル」→「実際にAPIへ渡すモデルID文字列」の対応表です。

## 4. 画面切り替えの仕組み（61〜102行目）

これがこのアプリで一番トリッキーな部分なので、少し丁寧に説明します。

```python
if "page" not in st.session_state:
    st.session_state["page"] = HOME_KEY

def go_to(tool_key: str):
    st.session_state["page"] = tool_key
    st.rerun()
```

**`st.session_state`とは？**
Streamlitはボタンが押されるたびに、実は`app.py`全体を上から下まで**再実行**しています。普通のPython変数はその都度リセットされてしまうので、「今どの画面を表示しているか」のような状態を覚えておくために`st.session_state`という辞書型の"記憶領域"を使います。ブラウザのタブ1つにつき1つの`session_state`が保持されます。

- `st.session_state["page"]`に「今どの画面にいるか」（例: `"🏠 ホーム"`や`"📄 要約"`）を保存
- `go_to(tool_key)`という関数は「`page`を書き換えて`st.rerun()`（強制的に画面を再実行）する」という共通処理をまとめたもの。ホームのカードの「開く →」ボタンや「← ホームに戻る」ボタンから呼ばれます

続いてサイドバー部分です。

```python
with st.sidebar:
    ...
    env_api_key = os.getenv("GEMINI_API_KEY")
    if env_api_key:
        api_key = env_api_key
    else:
        api_key = st.text_input("Gemini API Key", type="password", ...)
```

`.env`に`GEMINI_API_KEY`が設定してあればそれを使い、なければ入力欄を表示して手入力してもらう、という分岐です。`type="password"`は入力文字を`•••`のように隠す指定です。

```python
    nav_options = [HOME_KEY] + list(TOOLS.keys())
    selected_nav = st.radio("ナビゲーション", nav_options, index=nav_options.index(st.session_state["page"]))
    if selected_nav != st.session_state["page"]:
        st.session_state["page"] = selected_nav
        st.rerun()
```

ここは以前バグ修正した箇所です。最初は`st.radio(..., key="page")`と書いて、ラジオボタンと`session_state["page"]`を直接結びつけようとしていました。しかしStreamlitには「ウィジェットに紐づけたキーは、そのウィジェットが表示された後の同じ処理の中で他の場所（例: ホーム画面のボタン）から書き換えてはいけない」というルールがあり、それに違反してエラーになっていました。

そこで今の形に変更しています。

- ラジオボタン自体には`key`を持たせず、ただの戻り値`selected_nav`として受け取る
- その値が今の`page`と違っていたら（＝ユーザーがラジオボタンをクリックして選択を変えたら）、そこで初めて`page`を書き換えて`rerun`する

これなら「ラジオボタンから」も「ホームのカードボタンから」も、両方安全に`page`を更新できます。

## 5. ホーム画面 vs ツール画面の出し分け（104〜148行目）

```python
current = st.session_state["page"]

if current == HOME_KEY:
    # ホーム画面：カードを並べる
    ...
else:
    # ツール画面：選ばれたツールを描画する
    ...
```

### ホーム画面（104〜136行目）

```python
tool_keys = list(TOOLS.keys())
cols_per_row = 3
for i in range(0, len(tool_keys), cols_per_row):
    row_keys = tool_keys[i : i + cols_per_row]
    cols = st.columns(cols_per_row)
    for col, key in zip(cols, row_keys):
        ...
```

7つのツールを3列ずつ横に並べるための二重ループです。`range(0, 7, 3)`は`0, 3, 6`を生成するので、「0〜2番目」「3〜5番目」「6番目のみ」の3行に分かれてカードが並びます。`st.columns(3)`で横3分割のレイアウト枠を作り、`zip`でその枠とツール名を1対1で対応づけながらカードを描画しています。

各カードでは`st.container(border=True)`（枠線付きの箱）の中にHTML（アイコン・タイトル・説明文）と、最後に「開く →」ボタンを置いています。ボタンが押されると`go_to(key)`が呼ばれ、画面がそのツールに切り替わります。

### ツール画面（137〜148行目）

```python
else:
    if st.button("← ホームに戻る"):
        go_to(HOME_KEY)

    st.title(current)

    if not api_key:
        st.warning("サイドバーに Gemini API Key を入力してください。")
        st.stop()

    client = get_client(api_key)
    TOOLS[current]["render"](client, model, temperature)
```

最後の1行が全ての締めくくりです。`TOOLS[current]["render"]`で、今選ばれているツールの描画関数（例: `render_summarizer`）を取り出し、`(client, model, temperature)`を渡して実行しています。この関数の中身（入力フォームやAI呼び出し）は`tools.py`側に書かれています。`st.stop()`はAPIキーが無ければそこでスクリプトの実行を止める、という安全弁です。

## まとめ：全体の流れ

1. ページ設定・CSS読み込みで見た目を整える
2. `TOOLS`辞書で「どんなツールがあるか」を一元管理する
3. `session_state["page"]`という"今どの画面か"の記憶を使って画面を切り替える
4. `page`が`"🏠 ホーム"`ならカード一覧、それ以外なら`TOOLS[page]["render"](...)`で該当ツールの中身を呼び出す

`app.py`自体はGemini APIを直接呼んでおらず、「どのツールをいつ表示するか」の交通整理役に徹しているのがポイントです。実際のプロンプト作成やAI呼び出しのロジックは`tools.py`・`gemini_client.py`にあります。
