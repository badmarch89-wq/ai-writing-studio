# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## これは何か

Streamlit と Gemini API で作られた、個人利用のAIライティングアシスタントです。データベースも認証もなく、アプリ全体がローカルのStreamlitプロセスで、APIキーは `.env` かサイドバーのテキスト入力から読み込みます。

## コマンド

```bash
# セットアップ（.venv は作成済み）
source .venv/bin/activate
pip install -r requirements.txt

# 起動
streamlit run app.py

# 構文・importの健全性チェック（テストスイートは存在しない）
python -m py_compile app.py gemini_client.py tools.py style.py
```

lint・formatter・テストスイートは設定されていません。`GEMINI_API_KEY` は `.env` に置きます（`.env.example` 参照）。未設定の場合、実行時にサイドバーで入力を求められ、値は `st.session_state` にのみ保持されます。

`.streamlit/config.toml`（テーマ設定）の変更はホットリロードされないため、変更後は `streamlit run` プロセスを再起動してください。それ以外（`app.py`、`tools.py`、`style.py`、`gemini_client.py`）はブラウザ側で自動リロードされます。

## アーキテクチャ

4つのファイルにそれぞれ1つの役割があります。

- **`app.py`** — ページ設定、`style.py` のCSS読み込み、ナビゲーション状態の管理を担当し、Geminiクライアントの生成とサイドバー（APIキー、モデル選択、temperatureスライダー）を扱う唯一の場所です。ナビゲーションは `st.session_state["nav"]` という単一のキーで管理されます。値が `"🏠 ホーム"` ならカード形式のツール一覧（`TOOLS` 辞書から構築）を表示し、それ以外なら `TOOLS[key]["render"]` を呼び出します。カードのボタンと「ホームに戻る」ボタンはどちらも `st.session_state["nav"]` を書き換えてから `st.rerun()` を呼ぶパターンです。ナビゲーションの導線を追加する際もこのパターンに従ってください。
- **`tools.py`** — ツールごとに1つの `render_*(client, model, temperature)` 関数（ブログ記事作成、メール返信、要約、校正、トーン変換、タイトル提案、翻訳）を持ちます。各関数は完結しており、自身のUI（基本項目はそのまま、副次的な項目は `st.expander("⚙️ 詳細設定")` 内）を描画し、ボタン押下時にフォームの状態からプロンプト文字列を組み立て、`run_and_show(...)` で実行します。新しいツールを追加する場合は、同じ形の `render_*` 関数を書き、`app.py` の `TOOLS` 辞書に表示名・説明文とともに登録してください。
- **`gemini_client.py`** — `google-genai` SDK を扱う唯一のモジュールです。`get_client` はAPIキーごとに `st.cache_resource` でキャッシュされます。`generate_text_stream` は `client.models.generate_content_stream` のラッパーです。`run_and_show` は各ツールのボタン処理から呼ばれる共通の実行ヘルパーで、レスポンスをストリーミングしながら `st.markdown` のプレースホルダーに逐次表示し、完了後は全文をコピーしやすい `st.code` ブロックとして折りたたみ式のexpander内に表示します。`tools.py` から直接Gemini APIを呼ばず、必ず `run_and_show` を再利用してください。
- **`style.py`** — `CUSTOM_CSS` という1つの文字列をエクスポートし、`app.py` 内で `st.markdown(..., unsafe_allow_html=True)` により注入されます（ライトテーマ、Orbitron/Rajdhaniフォント、シアン/パープル/ピンクのグラデーションアクセント）。構造的な要素にはカスタムクラスではなくStreamlit内部の `data-testid` セレクタ（`stAppViewContainer`、`stSidebar`、`stVerticalBlockBorderWrapper`、`stButton` など）を対象にしており、ホーム画面のマークアップ（`app.py` 内）でのみ使うカスタムクラス（`tool-card-*`、`home-hero*`）が一部あります。全体的な見た目を変更する場合は、`app.py`/`tools.py` にインラインスタイルを追加するのではなく、ここを編集してください。基本テーマの配色は `.streamlit/config.toml` にも反映されています。これは、一部のウィジェット内部のUI（ドロップダウンのポップアップなど）が注入したCSSではなくStreamlitのテーマ設定に従うためです。

## モデル

Gemini のモデルIDは `app.py` の `MODEL_OPTIONS` 辞書にハードコードされています（現在は `gemini-2.5-flash` と `gemini-2.5-pro` をサイドバーで選択）。モデルの選択肢を追加・削除する場合はこの辞書を更新してください。

## プロンプト構築の規約

`tools.py` の各 `render_*` 関数は、ボタン押下時に同じ形でプロンプトを組み立てています。

1. 「⚙️ 詳細設定」を含む各UI項目から、日本語の指示文を `instructions`（または個別の変数）としてリストに集める。
2. `chr(10).join(f"- {i}" for i in instructions)` で箇条書きにし、`# 条件` セクションとしてプロンプトに埋め込む。
3. ユーザー入力本文は `---` で挟んで別セクションとして渡す。

新しいツールや設定項目を追加するときは、この「UIの選択肢 → 条件の箇条書き → プロンプトテンプレートに埋め込む」という流れに合わせてください。バラバラな組み立て方をするとツール間で挙動やメンテナンス性が揃わなくなります。

## その他の注意点

- このディレクトリは Git 管理下にありません（`.git` なし）。バージョン管理を始める場合は `git init` から必要です。
- `requirements.txt` はバージョン固定していません。`google-genai` はSDKの変更が比較的早いパッケージなので、依存関係を更新した際は `gemini_client.py` の呼び出し（`client.models.generate_content_stream` の引数・戻り値の形など）が変わっていないか確認してください。
- `GEMINI_API_KEY` を環境変数で設定している場合、サイドバーの入力欄は表示されず変更もできません（`app.py` の `env_api_key` 分岐）。動作確認時にキーを差し替えたい場合は `.env` 側を編集してください。
