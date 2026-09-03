import streamlit as st

from gemini_client import run_and_show


def render_blog_writer(client, model, temperature):
    st.subheader("📝 ブログ記事作成（SEO対応）")

    topic = st.text_input("記事のテーマ・タイトル案", placeholder="例: 在宅ワークの生産性を上げる5つの習慣")
    main_keyword = st.text_input(
        "狙う検索キーワード（メインキーワード）",
        placeholder="例: 在宅ワーク 生産性",
        help="この記事で検索上位を狙いたいキーワードを1つ入力してください。タイトル・見出し・冒頭に自然に配置されます。",
    )
    related_keywords = st.text_input("関連キーワード・共起語（任意・カンマ区切り）", placeholder="例: 集中力, タイムマネジメント, 在宅勤務 コツ")
    audience = st.text_input("想定読者（任意）", placeholder="例: フリーランスのエンジニア")

    col1, col2, col3 = st.columns(3)
    with col1:
        search_intent = st.selectbox(
            "検索意図",
            ["情報収集型（〜とは・方法）", "比較検討型（〜おすすめ・比較）", "購入・行動型（〜申込み・始め方）"],
        )
    with col2:
        length = st.select_slider("文章量", options=["短め", "標準", "SEO推奨（長め）"], value="SEO推奨（長め）")
    with col3:
        language = st.selectbox("出力言語", ["日本語", "英語"])

    tone = st.selectbox("トーン", ["フレンドリー", "ビジネスライク", "専門的", "カジュアル"])

    with st.expander("⚙️ 詳細設定"):
        num_headings = st.slider("見出し（H2）の数", 3, 8, 5)
        structure_options = st.multiselect(
            "含める構成要素",
            ["導入文", "目次への言及", "まとめ", "FAQ（よくある質問）", "CTA（行動喚起・締めの一言）"],
            default=["導入文", "目次への言及", "まとめ", "FAQ（よくある質問）"],
        )
        include_meta = st.checkbox("メタタイトル・メタディスクリプションも生成する", value=True)
        suggest_alt_text = st.checkbox("挿入画像のalt属性（代替テキスト）案も提案する")
        internal_link_topics = st.text_area(
            "内部リンクしたい自サイトの関連記事・トピック（任意）",
            height=70,
            placeholder="1行に1つ。例:\nブログの始め方\nSEOライティング入門",
        )
        style_sample = st.text_area(
            "文体の参考サンプル（任意）",
            height=80,
            placeholder="この文体に寄せて書いてほしい文章があれば貼り付けてください",
        )

    length_map = {
        "短め": "800〜1000文字程度",
        "標準": "1500〜2000文字程度",
        "SEO推奨（長め）": "2500〜3500文字程度（検索上位表示を狙える網羅性を意識）",
    }

    if st.button("記事を作成する", type="primary", disabled=not (topic.strip() and main_keyword.strip())):
        structure_lines = [
            f"- 見出し（H2）は{num_headings}個構成にし、それぞれの見出しにメインキーワードまたは関連キーワードを自然に含めてください。",
            "- タイトル（H1相当）にはメインキーワードを含め、32文字前後で検索結果に表示されやすい形にしてください。",
            "- 本文の最初の100〜150文字以内にメインキーワードを自然に配置し、この記事で何が得られるかを明示してください。",
            "- 1段落は3〜4行程度に収め、箇条書きや表を適度に使って読みやすさ（可読性）を高めてください。",
            "- キーワードの詰め込み（不自然な繰り返し）は避け、共起語・関連語を使って自然な文章にしてください。",
        ]
        if "導入文" in structure_options:
            structure_lines.append("- 冒頭に読者の悩みに共感する導入文を入れてください。")
        if "目次への言及" in structure_options:
            structure_lines.append("- 導入文の直後に「この記事でわかること」を箇条書きで3〜4点示してください（目次代わりになるようにする）。")
        if "まとめ" in structure_options:
            structure_lines.append("- 最後に要点をまとめた「まとめ」セクションを入れてください。")
        if "FAQ（よくある質問）" in structure_options:
            structure_lines.append(
                "- 記事の最後にFAQ（よくある質問と回答、3〜5問）セクションを入れてください。質問文には検索されやすい自然な疑問形の表現を使い、"
                "回答は40〜80文字程度で簡潔にまとめてください（検索結果の強調スニペットを狙える形式）。"
            )
        if "CTA（行動喚起・締めの一言）" in structure_options:
            structure_lines.append("- 記事の締めに、読者への行動喚起（CTA）となる一文を入れてください。")
        if include_meta:
            structure_lines.append(
                "- 記事本文の前に、次の2行を追加してください:\n"
                "  「メタタイトル: 」（メインキーワードを含め30〜35文字程度）\n"
                "  「メタディスクリプション: 」（メインキーワードを含め110〜130文字程度で、記事を読むメリットが伝わる内容）"
            )
        if suggest_alt_text:
            structure_lines.append(
                "- 記事内で画像を挿入するとよい箇所に `[画像挿入: 内容の説明]` という形でマーカーを入れ、その直後に「alt属性案: 」として画像の代替テキスト案を1つ添えてください。"
            )
        if internal_link_topics.strip():
            structure_lines.append(
                f"- 本文中の自然な箇所に、以下の自サイト内の関連トピックへのリンクを想定した文言を `[関連: トピック名]` の形式で2〜3箇所差し込んでください:\n{internal_link_topics}"
            )
        if style_sample.strip():
            structure_lines.append(f"- 次の文章と近い文体・語り口で書いてください:\n{style_sample}")

        prompt = f"""以下の条件でSEOを意識したブログ記事を1本、Markdown形式（見出し・箇条書きを適切に使用）で{language}で書いてください。

テーマ: {topic}
メインキーワード（検索上位を狙うキーワード）: {main_keyword}
関連キーワード・共起語: {related_keywords or "特になし"}
検索意図: {search_intent}
想定読者: {audience or "特に指定なし"}
トーン: {tone}
文章量: {length_map[length]}

# SEO・構成の指示
{chr(10).join(structure_lines)}
"""
        run_and_show(
            client, model, temperature, prompt,
            system_instruction=(
                "あなたは検索エンジン最適化（SEO）に精通したプロのWebライターです。"
                "Googleの検索意図・E-E-A-T（経験・専門性・権威性・信頼性）を意識し、"
                "読者の悩みを解決しながら、狙ったキーワードで検索上位を獲得できる記事を書きます。"
                "キーワードの不自然な詰め込みは避け、あくまで読者にとって読みやすく役立つ文章を優先してください。"
            ),
        )


def render_email_reply(client, model, temperature):
    st.subheader("✉️ メール返信文作成")

    original = st.text_area("受信したメール本文", height=200, placeholder="返信したいメールの本文を貼り付けてください")
    intent = st.text_area("伝えたい内容・返信の要点", height=100, placeholder="例: 来週の打ち合わせは参加できるが、時間を14時に変更してほしい")

    col1, col2, col3 = st.columns(3)
    with col1:
        purpose = st.selectbox("目的", ["一般的な返信", "お礼", "謝罪", "日程調整", "依頼・お願い", "断り・辞退", "催促・リマインド"])
    with col2:
        tone = st.selectbox("トーン", ["丁寧・ビジネス", "フォーマル", "カジュアル・親しみやすい"])
    with col3:
        length = st.select_slider("長さ", options=["簡潔", "普通", "丁寧に詳しく"], value="普通")

    with st.expander("⚙️ 詳細設定"):
        relationship = st.selectbox(
            "相手との関係性",
            ["社外・取引先（目上）", "社内・上司", "社内・同僚", "友人・親しい間柄"],
        )
        sender_name = st.text_input("署名に使う名前（任意）", placeholder="例: 山田太郎")
        language = st.selectbox("出力言語", ["日本語", "英語"])
        include_subject = st.checkbox("件名（Re:）も提案する")

    if st.button("返信文を作成する", type="primary", disabled=not intent.strip()):
        instructions = [
            f"目的: {purpose}",
            f"相手との関係性: {relationship}",
            f"トーン: {tone}",
            f"長さ: {length}",
            f"出力言語: {language}",
        ]
        if sender_name.strip():
            instructions.append(f"末尾の署名には「{sender_name}」を使ってください。")
        if include_subject:
            instructions.append("メール本文の前に、適切な件名を「件名: 」として1行追加してください。")

        prompt = f"""以下の受信メールへの返信メールを1通作成してください。そのまま送れる完成形の文面にしてください。

# 受信メール
{original or "(元メールの提示なし。伝えたい内容のみから返信文を作成してください)"}

# 伝えたい内容・要点
{intent}

# 条件
{chr(10).join(f"- {i}" for i in instructions)}
"""
        run_and_show(
            client, model, temperature, prompt,
            system_instruction="あなたはビジネスメールに精通したアシスタントです。相手に失礼のない、自然な文面のメールを作成します。",
        )


def render_summarizer(client, model, temperature):
    st.subheader("📄 要約")

    text = st.text_area("要約したい文章", height=280, placeholder="要約したい文章を貼り付けてください")

    col1, col2, col3 = st.columns(3)
    with col1:
        length = st.select_slider("要約の長さ", options=["短め", "普通", "長め"], value="普通")
    with col2:
        style = st.radio("形式", ["箇条書き", "文章"], horizontal=True)
    with col3:
        language = st.selectbox("出力言語", ["日本語", "英語", "原文と同じ言語"])

    with st.expander("⚙️ 詳細設定"):
        focus = st.text_input("特に重視したい観点（任意）", placeholder="例: コストへの影響, 今後のアクション")
        add_tldr = st.checkbox("冒頭に一言まとめ（TL;DR）を追加する")
        preserve_numbers = st.checkbox("数値・固有名詞・日付は省略せず保持する", value=True)

    length_map = {
        "短め": "2〜3文（または3項目）程度に短く",
        "普通": "5〜6文（または5項目）程度で",
        "長め": "重要なポイントを漏らさず、10文（または項目）程度で",
    }
    style_map = {"箇条書き": "箇条書き形式で", "文章": "自然な文章形式で"}
    language_map = {
        "日本語": "日本語で出力してください。",
        "英語": "英語で出力してください。",
        "原文と同じ言語": "原文と同じ言語で出力してください。",
    }

    if st.button("要約する", type="primary", disabled=not text.strip()):
        extra = []
        if focus.strip():
            extra.append(f"特に「{focus}」の観点を重視して要約してください。")
        if add_tldr:
            extra.append("冒頭に「TL;DR: 」として一言まとめを1文追加してください。")
        if preserve_numbers:
            extra.append("数値・固有名詞・日付などの具体的な情報は省略せず保持してください。")

        prompt = f"""以下の文章を{style_map[style]}{length_map[length]}要約してください。{language_map[language]}
{chr(10).join(extra)}

---
{text}
---
"""
        run_and_show(client, model, temperature, prompt)


def render_proofreader(client, model, temperature):
    st.subheader("✅ 校正・誤字脱字チェック")

    text = st.text_area("校正したい文章", height=280, placeholder="誤字脱字や言い回しをチェックしたい文章を貼り付けてください")

    col1, col2 = st.columns(2)
    with col1:
        strictness = st.select_slider("校正の強さ", options=["軽め（誤字脱字のみ）", "標準", "厳しめ（文章全体を推敲）"], value="標準")
    with col2:
        style_guide = st.selectbox("文体の基準", ["ビジネス文書", "カジュアル・日常文", "学術・論文調", "指定なし"])

    with st.expander("⚙️ 詳細設定"):
        show_explanation = st.checkbox("修正点の説明も表示する", value=True)
        unify_expression = st.checkbox("表記ゆれ（漢字/かな、送り仮名など）を統一する", value=True)
        show_diff = st.checkbox("修正箇所を ~~取り消し線~~ と **太字** で分かるように示す")

    if st.button("校正する", type="primary", disabled=not text.strip()):
        instructions = [f"校正の強さ: {strictness}"]
        if style_guide != "指定なし":
            instructions.append(f"「{style_guide}」の文体基準に合わせて整えてください。")
        if unify_expression:
            instructions.append("表記ゆれ（漢字/ひらがな、送り仮名、カタカナ表記など）を文章全体で統一してください。")
        if show_diff:
            instructions.append(
                "修正後の文章では、削除した部分を ~~取り消し線~~ で、追加・変更した部分を **太字** で示し、変更箇所が視覚的にわかるようにしてください。"
            )
        else:
            instructions.append("修正後の文章はそのまま自然に読める形で出力してください（記号での差分表示は不要です）。")

        if show_explanation:
            instructions.append("修正後の文章の後に、区切り線を引いて「## 主な修正点」として変更箇所と理由を簡潔な箇条書きで説明してください。")
        else:
            instructions.append("修正後の文章のみを出力し、説明は不要です。")

        prompt = f"""以下の文章の誤字脱字・文法・不自然な言い回しを修正してください。意味や書き手のニュアンスはできるだけ変えないでください。

# 条件
{chr(10).join(f"- {i}" for i in instructions)}

---
{text}
---
"""
        run_and_show(client, model, temperature, prompt)


def render_tone_converter(client, model, temperature):
    st.subheader("🎭 トーン変換")

    text = st.text_area("変換したい文章", height=250, placeholder="トーンを変えたい文章を貼り付けてください")

    col1, col2 = st.columns(2)
    with col1:
        target_tone = st.selectbox(
            "変換先のトーン",
            ["丁寧語・ビジネス", "フォーマル", "カジュアル", "フレンドリー", "謙譲語多め（かしこまった敬語）", "簡潔・端的"],
        )
    with col2:
        strength = st.select_slider("変換の強さ", options=["少しだけ", "標準", "しっかり変換"], value="標準")

    with st.expander("⚙️ 詳細設定"):
        audience = st.text_input("読み手・想定シーン（任意）", placeholder="例: 初めて取引する社外の相手, 親しい同僚")
        preserve_length = st.checkbox("元の文章とほぼ同じ長さに保つ")

    if st.button("変換する", type="primary", disabled=not text.strip()):
        instructions = [
            f"トーン: 「{target_tone}」に書き換えてください。",
            f"変換の強さ: {strength}",
        ]
        if audience.strip():
            instructions.append(f"読み手・シーン: {audience} を意識してください。")
        if preserve_length:
            instructions.append("文章の長さは元の文章とほぼ同じになるようにしてください。")

        prompt = f"""以下の文章を、意味内容を変えずにトーンだけ書き換えてください。

# 条件
{chr(10).join(f"- {i}" for i in instructions)}

---
{text}
---
"""
        run_and_show(client, model, temperature, prompt)


def render_title_generator(client, model, temperature):
    st.subheader("💡 タイトル・見出し提案")

    content = st.text_area(
        "記事の内容・テーマ（本文の一部や要約でも可）",
        height=200,
        placeholder="タイトルを考えたい記事の内容やテーマを入力してください",
    )
    col1, col2, col3 = st.columns(3)
    with col1:
        platform = st.selectbox("用途", ["ブログ記事", "YouTube動画", "X（Twitter）投稿", "note記事", "メールマガジン件名"])
    with col2:
        style = st.selectbox("スタイル", ["SEOを意識した検索されやすいタイトル", "キャッチーで目を引くタイトル", "シンプルで分かりやすいタイトル", "煽り・驚き重視"])
    with col3:
        count = st.slider("候補数", 3, 10, 5)

    with st.expander("⚙️ 詳細設定"):
        max_length = st.number_input("文字数の上限（任意・0で指定なし）", min_value=0, max_value=200, value=0, step=5)
        include_numbers = st.checkbox("「◯つの」のような数字を含める", value=True)
        include_emoji = st.checkbox("絵文字を含める")

    if st.button("タイトルを生成する", type="primary", disabled=not content.strip()):
        instructions = [f"用途: {platform}", f"スタイル: {style}", f"{count}個、番号付きの箇条書きで提案してください。"]
        if max_length > 0:
            instructions.append(f"各タイトルは{max_length}文字以内に収めてください。")
        if include_numbers:
            instructions.append("可能であれば「5つの」「3ステップで」のような具体的な数字を含めてください。")
        if include_emoji:
            instructions.append("各タイトルの先頭か末尾に、内容に合った絵文字を1つ入れてください。")
        else:
            instructions.append("絵文字は使わないでください。")

        prompt = f"""以下の内容に基づいて、タイトル案を提案してください。

# 条件
{chr(10).join(f"- {i}" for i in instructions)}

---
{content}
---
"""
        run_and_show(client, model, temperature, prompt)


def render_translator(client, model, temperature):
    st.subheader("🌐 翻訳")

    text = st.text_area("翻訳したい文章", height=250, placeholder="翻訳したい文章を貼り付けてください")
    col1, col2 = st.columns(2)
    with col1:
        target_lang = st.selectbox("翻訳先の言語", ["英語", "日本語", "中国語（簡体字）", "韓国語", "スペイン語", "フランス語"])
    with col2:
        formality = st.radio("文体", ["フォーマル", "カジュアル"], horizontal=True)

    with st.expander("⚙️ 詳細設定"):
        glossary = st.text_area(
            "専門用語・固有名詞の対訳（任意）",
            height=80,
            placeholder="1行に1つ、「原語=訳語」の形式で入力してください\n例: 御社=your company",
        )
        keep_formatting = st.checkbox("元の改行・箇条書きなどのレイアウトを保持する", value=True)
        add_notes = st.checkbox("訳注（意訳した箇所やニュアンスの補足）を追加する")

    if st.button("翻訳する", type="primary", disabled=not text.strip()):
        instructions = [
            f"翻訳先の言語: {target_lang}",
            f"文体: {formality}",
            "不自然な直訳ではなく、その言語のネイティブが読んで自然な表現にしてください。",
        ]
        if glossary.strip():
            instructions.append(f"次の対訳表に従って用語を訳してください:\n{glossary}")
        if keep_formatting:
            instructions.append("元の文章の改行・箇条書き・段落構成をできるだけ保持してください。")
        if add_notes:
            instructions.append("翻訳の後に区切り線を引き、「## 訳注」として意訳した箇所やニュアンスの補足を簡潔に記載してください。")

        prompt = f"""以下の文章を翻訳してください。

# 条件
{chr(10).join(f"- {i}" for i in instructions)}

---
{text}
---
"""
        run_and_show(client, model, temperature, prompt)
