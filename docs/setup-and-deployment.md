# セットアップ・連携の記録：GitHub 連携とローカル実行

このドキュメントは、本プロジェクト（AI Writing Studio）をどのように GitHub と連携し、ローカルで動かせる状態にしたかをまとめたものです。

## 前提

- リポジトリは `git init` 済み、GitHub 上に `badmarch89-wq/ai-writing-studio`（Private）としてリモート `origin` が設定済みの状態からスタートしています。
- 認証には GitHub CLI（`gh`）を使用しています。

## 1. GitHub CLI の認証確認

```bash
gh auth status
```

すでにアカウント `badmarch89-wq` で認証済み（トークンスコープ: `gist`, `read:org`, `repo`, `workflow`）であることを確認しました。認証をやり直しても、同じアカウントであればアクセスできるリポジトリや権限は変わりません（トークンが再発行されるだけです）。別アカウントでログインし直す場合のみ、アクセス範囲が切り替わります。

## 2. リポジトリの状態確認

```bash
git status
git remote -v
git log --oneline
```

- `origin` は `https://github.com/badmarch89-wq/ai-writing-studio.git` を指しており、`main` ブランチが `origin/main` と同期済みでした。
- `gh repo view badmarch89-wq/ai-writing-studio` でリモート側の存在と可視性（Private）も確認しました。

## 3. 環境変数（APIキー）の設定

Gemini API キーは `.env` に置く方式です。リポジトリには実際のキーを含めず、テンプレートとして `.env.example` のみを管理しています。

```bash
cp .env.example .env
```

作成した `.env` の `GEMINI_API_KEY=your_api_key_here` の部分を、実際に [Google AI Studio](https://aistudio.google.com/apikey) で発行したキーに書き換えます。

### 漏洩リスクの確認

- `.gitignore` に `.env` を登録済みのため、`git ls-files` で確認しても `.env` はコミット対象に含まれておらず、GitHub にはアップロードされません。
- 残るリスクは主にローカル環境側（PC自体の侵害、スクリーンショットや画面共有への写り込み、`.gitignore` の誤編集や `git add -f` での強制追加など）であり、コード側でキーをログ出力する実装にはなっていません。
- 念のため、Google AI Studio 側でそのキーの使用量に上限を設定しておくと、万一漏れた場合の被害を抑えられます。

## 4. ローカルでの起動

```bash
source .venv/bin/activate
streamlit run app.py
```

- デフォルトでは `http://localhost:8501`（ポート使用中の場合は `8502` など自動で繰り上がり）で起動します。
- `.env` に `GEMINI_API_KEY` を設定していれば、サイドバーへのキー入力は不要でそのまま各ツールが使えます。未設定の場合はサイドバーにキー入力欄が表示され、入力したキーは `st.session_state` にのみ保持されます（永続化はされません）。

## 現時点でのデプロイ状況

- **GitHub**: 連携済み・プッシュ済み（`origin/main`）。
- **Netlify などの本番ホスティング**: 未設定。Streamlit アプリは Python の常駐プロセスとして動くため、静的サイトホスティングである Netlify では通常そのまま動作しません。本番公開する場合は Streamlit Community Cloud や、コンテナ実行環境（Cloud Run など）を使う方式の検討が別途必要です。
