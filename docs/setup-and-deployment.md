# 生成AIアプリ開発ガイド：環境準備・設定・豆知識・注意事項

このドキュメントは、本プロジェクト（AI Writing Studio / Streamlit + Gemini API）を実際に構築・運用する過程で得られた知見をまとめたものです。今後の生成AIアプリ開発でも再利用できるよう、一般化しつつ随時更新していきます。

- 最終更新: 2026-09-04
- 対象アプリ: `python ai application`（Streamlit + Google Gemini API、DB・認証なしの個人用ツール）
- 本番URL: https://7uygefsvdfkzcrxxjtbwqt.streamlit.app/（Streamlit Community Cloud、Privateリポジトリ連携）

---

## 1. 環境準備

### 1.1 技術スタック（今回の選定）

- **言語 / フレームワーク**: Python + Streamlit（UIをHTML/CSS/JSなしで素早く組める）
- **LLM**: Google Gemini API（`google-genai` SDK）
- **設定管理**: `python-dotenv`（`.env`から環境変数読み込み）
- **バージョン管理**: Git + GitHub（GitHub CLI `gh` で認証・操作）

### 1.2 セットアップ手順

```bash
# 仮想環境の作成・有効化
python3 -m venv .venv
source .venv/bin/activate

# 依存パッケージのインストール
pip install -r requirements.txt
# 中身の例: streamlit / google-genai / python-dotenv

# 起動
streamlit run app.py
```

- デフォルトでは `http://localhost:8501` で起動。ポートが使用中の場合は `8502` など自動で繰り上がる。
- バックグラウンドで起動して並行作業したい場合:
  ```bash
  nohup streamlit run app.py > streamlit.log 2>&1 &
  open http://localhost:8501
  ```

### 1.3 GitHub CLI（`gh`）の認証

```bash
gh auth status          # 現在の認証状態を確認
gh auth login --web     # 未認証、または別アカウントに切り替えたい場合
```

- 既に同じアカウントで認証済みの場合、再認証してもアクセスできるリポジトリ・権限（スコープ）は変わらない。トークンが再発行されるだけ。
- 別アカウントでログインし直した場合のみ、アクセス範囲が切り替わる。

### 1.4 リポジトリの状態確認（連携前に必ず確認）

```bash
git status
git remote -v
git log --oneline
gh repo view <owner>/<repo> --json name,url,visibility,pushedAt
```

すでに `git init` 済み・GitHubにプッシュ済みのプロジェクトを誤って作り直さないよう、まず現状把握してから作業する。

---

## 2. 設定

### 2.1 APIキーの管理（`.env`）

```bash
cp .env.example .env
# GEMINI_API_KEY=your_api_key_here を実際のキーに書き換える
```

- キーは [Google AI Studio](https://aistudio.google.com/apikey) で発行。
- `.gitignore` に `.env` を必ず含める（本プロジェクトでは最初から設定済み）。
- **方式の変遷**: 当初は「環境変数優先、未設定ならサイドバーで手入力」の二段構えにしていたが、利用者本人が費用発生タイミングを把握・管理しやすいよう、**常にサイドバーで手入力する方式に変更**した（`.env`・環境変数からの自動読み込みは廃止）。入力されたキーは `st.session_state` にのみ保持し、ファイルには書き出さない。
- この方式ならデプロイ先（Streamlit Community Cloud）の Secrets にキーを登録する必要がなく、Privateリポジトリと組み合わせても鍵の管理箇所が「自分の頭の中」だけで完結する。

### 2.2 Streamlitのテーマ設定（`.streamlit/config.toml`）

- 配色などの見た目は `.streamlit/config.toml`（テーマ）と、`st.markdown(..., unsafe_allow_html=True)` で注入するカスタムCSS（本プロジェクトでは `style.py`）の二箇所で管理される。
- ドロップダウンのポップアップなど、CSS注入が効かない一部のウィジェット内部UIは `config.toml` のテーマ設定に従うため、両方を揃えておく必要がある。

### 2.3 モデルIDの管理

- Gemini のモデルIDはハードコードせず、辞書などで一箇所にまとめておく（本プロジェクトでは `app.py` の `MODEL_OPTIONS`）。
- Gemini側でモデルが廃止・置き換えになることがあるため、定期的に有効なモデルIDか確認が必要（詳細は「4. 注意事項」参照）。
- 現在の選択肢（2026-09-04時点）: `gemini-3.6-flash`（速い・普段使い）／ `gemini-3.1-pro-preview`（高精度）。旧 `gemini-2.5-flash` / `gemini-2.5-pro` は新規ユーザー向けに廃止済みで置き換えた。

### 2.4 Streamlit Community Cloud へのデプロイ

無料でアプリを公開URL化できるサービス。GitHubリポジトリと連携するだけでデプロイできる。

1. https://share.streamlit.io にGitHubアカウントでログイン
2. 「Create app」→「Deploy a public app from GitHub」
3. Repository / Branch / Main file path（`app.py`）を指定してデプロイ

**得られたURL（本プロジェクト）**: https://7uygefsvdfkzcrxxjtbwqt.streamlit.app/

**注意点:**

- リポジトリが Private でも Streamlit Cloud（無料枠）はGitHub連携で読み取れるが、**デプロイされたアプリ自体は誰でもアクセスできる公開URL**になる。他人に使われたくない場合はパスワード保護や有料プランでのプライベート化を検討する。
- コードをGitHubにプッシュすると自動的に再デプロイされるが、反映が遅れる／効かないことがあるため、確実に最新化したい場合は管理画面から手動で **「Reboot app」** を実行する。
- APIキーを毎回手入力する方式にしているため、Secrets（環境変数）欄には何も設定していない。

---

## 3. 豆知識（開発中に得た知見）

### 3.1 `.streamlit/config.toml` はホットリロードされない

`app.py` や `tools.py` などのPythonコードはブラウザ側で自動リロードされるが、`.streamlit/config.toml`（テーマ設定）を変更した場合は反映されない。**`streamlit run` プロセスを再起動する必要がある。**

### 3.2 `st.session_state` は「ウィジェット生成後」に書き換えるとエラーになる

実際に遭遇したエラー:

```
streamlit.errors.StreamlitWidgetAlreadyInstantiatedError:
`st.session_state.nav` cannot be modified after the widget with key `nav` is instantiated.
```

ナビゲーション用の `st.session_state["nav"]` を、同じ `key="nav"` を持つウィジェットが既に描画された後のスクリプト内で書き換えようとすると発生する。**ボタン押下時の処理でセッションステートを更新する場合は、ウィジェットの再描画（`st.rerun()`）を挟むパターンに統一する**（本プロジェクトの `app.py` で採用している方式）。

### 3.3 `google-genai` SDKはAPIの変更が比較的早い

`requirements.txt` でバージョン固定していないため、`pip install --upgrade` 等でSDKが上がると `client.models.generate_content_stream` の引数・戻り値の形が変わっている可能性がある。依存関係を更新したら、Gemini呼び出し箇所の動作確認を必ず行う。

### 3.4 プロンプト組み立ての型を統一しておくと保守しやすい

複数のAIツール（ブログ執筆・メール返信・要約など）を1アプリにまとめる場合、各機能でプロンプトの組み立て方がバラバラだと保守性が落ちる。本プロジェクトでは以下の型に統一している。

1. UIの各項目から日本語の指示文をリストに集める
2. 箇条書き（`- ...`）にして `# 条件` セクションとしてプロンプトに埋め込む
3. ユーザー入力本文は `---` で区切って別セクションとして渡す

### 3.5 Gemini APIの費用感

- Gemini APIは**トークン数に応じた従量課金**。Google AI Studio経由でクレジットカードなしで使える無料枠があり、Flash系モデルなら1日あたり1000リクエスト超まで無料。
- **Proモデルは2026年4月以降、無料枠の対象外**になっており、使うと課金が発生する。
- 課金を有効にすると無料枠が上乗せされるのではなく、**無料枠自体がなくなり全て有料になる**仕様のため、有効化前に使い方を確認しておく。
- 無料枠のデータはGoogle側のモデル学習に使われる点にも留意する。
- 費用を抑えたい場合は普段はFlashを選び、高精度が必要な時だけProに切り替える運用が現実的。

### 3.6 Next.js / Drizzle ORM との使い分け（Streamlitの限界を知る）

- **Streamlit**: 個人・社内向けの「動くツール」を最速で作る用途に向く。Pythonのみで完結する代わりに、デザインの自由度・複数ユーザー対応・SEOには弱い。
- **Next.js**: 不特定多数に公開する製品として育てたい場合に向く。認証・DB連携・SEO・デザインの自由度は高いが、フロントエンド実装のコストがかかる。バックエンドはPython（FastAPIなど）を別途用意してAPI経由で繋ぐ構成が一般的。
- DBを使う機能（生成履歴の保存など）を追加する場合、Next.js側では **Drizzle ORM**（SQLに近い書き味・型安全・軽量でサーバーレスと相性が良いTypeScript向けORM）などが選択肢になる。本プロジェクトは現状DBを持たないため未使用。
- 目安: 「自分や身内が使えればいい・検証段階」→ Streamlit、「他人に配布・公開する製品にしたい」→ Next.js。まずStreamlitでプロトタイプを検証し、必要になったらNext.js化する進め方もよくある。

### 3.7 Netlifyなど静的ホスティングはStreamlitアプリにはそのまま使えない

Streamlitは常駐するPythonプロセスとして動くため、静的サイトホスティングであるNetlifyでは通常動作しない。本番公開する場合は **Streamlit Community Cloud**（本プロジェクトで採用、2.4節参照）か、**コンテナ実行環境（Cloud Run など）** を使う方式を検討する。

---

## 4. 注意事項

### 4.1 APIキー漏洩リスクの確認ポイント

- `git ls-files | grep .env` で、`.env` がコミット対象に入っていないか都度確認する。
- `.gitignore` の誤編集や `git add -f` での強制追加に注意。
- コード側でエラーメッセージにAPIキーそのものを含めて出力しない（本プロジェクトの `gemini_client.py` は例外メッセージのみを表示し、キーは出力しない設計）。
- 念のため、Google AI Studio側でAPIキーの使用量に上限を設定しておくと、万一漏れた場合の被害を抑えられる。
- スクリーンショットや画面共有でエディタ上のキーが映り込まないよう注意する。

### 4.2 Geminiモデルの廃止・仕様変更

実際に遭遇したエラー例:

```
404 NOT_FOUND: This model models/gemini-2.5-flash is no longer available to new users.
Please update your code to use models/gemini-3.6-flash for the latest features and improvements.
```

```
エラーが発生しました: 400 INVALID_ARGUMENT. API key not valid.
```

- モデルIDは予告なく非推奨・廃止になることがあるため、`MODEL_OPTIONS` のような一箇所管理にしておき、エラー時にすぐ差し替えられるようにしておく。
- 「APIキーが無効」というエラーは、キー自体のタイプミスだけでなく、キーに紐づくプロジェクトでそのモデルへのアクセス権がない場合にも出ることがあるため、両方を切り分けて確認する。

### 4.3 セキュリティレビューを組み込む

本プロジェクトでは `/streamlit-llm-security-check` スキルを作成し、以下の観点を都度チェックできるようにしている。

- APIキー・シークレットの漏洩
- プロンプト組み立て方法に起因するプロンプトインジェクションのリスク
- `unsafe_allow_html` を使ったXSS注入箇所
- 依存関係やその他一般的な脆弱性

LLM APIをラップするアプリはDBも認証もないことが多く、典型的なWebアプリ脆弱性（SQLインジェクション、CSRF、セッション固定攻撃など）がそのまま当てはまらないケースが多い点に注意。該当しない指摘でレポートを水増しすると、本当に重要な指摘が埋もれる。

### 4.4 ドキュメントは実施内容だけを書く

「〇〇と連携した」と書く前に、実際に設定ファイルや接続が存在するか確認してから記載する（例: 本プロジェクトではNetlify連携について聞かれた際、実際には未設定だったため「未連携」と明記した）。憶測でデプロイ済みと書かない。

---

## 更新履歴

- 2026-09-04: 初版作成（GitHub連携・ローカル実行手順）→ 全セッションを踏まえ、環境準備・設定・豆知識・注意事項を含む包括的なガイドに再構成
- 2026-09-04: APIキーを常にサイドバー手入力する方式に変更（環境変数からの自動読み込みを廃止）／Streamlit Community Cloudへデプロイし本番URLを発行／Gemini APIの費用感、Next.js・Drizzle ORMとの使い分けを追記
