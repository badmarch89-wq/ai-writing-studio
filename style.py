CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Rajdhani:wght@400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Rajdhani', sans-serif;
}

[data-testid="stAppViewContainer"] {
    background:
        linear-gradient(180deg, #ffffff 0%, #f4f7fc 100%),
        repeating-linear-gradient(0deg, rgba(0,150,255,0.05) 0px, rgba(0,150,255,0.05) 1px, transparent 1px, transparent 40px),
        repeating-linear-gradient(90deg, rgba(0,150,255,0.05) 0px, rgba(0,150,255,0.05) 1px, transparent 1px, transparent 40px);
    background-color: #ffffff;
}

[data-testid="stAppViewContainer"] * {
    color: #1c2333;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #ffffff 0%, #eef2fb 100%);
    border-right: 1px solid rgba(0, 150, 255, 0.18);
}

[data-testid="stSidebar"] * {
    color: #1c2333;
}

h1, h2, h3 {
    font-family: 'Orbitron', sans-serif !important;
    letter-spacing: 0.5px;
}

h1 {
    background: linear-gradient(90deg, #0091ff, #8b5cf6 60%, #ec4899);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.stButton > button {
    background: linear-gradient(90deg, rgba(0,145,255,0.08), rgba(139,92,246,0.08));
    border: 1px solid rgba(0, 145, 255, 0.4);
    color: #1c2333;
    border-radius: 10px;
    font-family: 'Rajdhani', sans-serif;
    font-weight: 600;
    letter-spacing: 0.5px;
    transition: all 0.2s ease;
}

.stButton > button:hover {
    border-color: #0091ff;
    box-shadow: 0 4px 18px rgba(0, 145, 255, 0.25);
    transform: translateY(-1px);
    color: #0091ff;
}

.stButton > button[kind="primary"] {
    background: linear-gradient(90deg, #0091ff, #8b5cf6);
    border: none;
    color: #ffffff;
    font-weight: 700;
}

.stButton > button[kind="primary"]:hover {
    box-shadow: 0 6px 22px rgba(139, 92, 246, 0.4);
    color: #ffffff;
}

[data-testid="stVerticalBlockBorderWrapper"] {
    background: #ffffff;
    border: 1px solid rgba(0, 145, 255, 0.15);
    border-radius: 16px;
    box-shadow: 0 2px 10px rgba(28, 35, 51, 0.04);
    transition: all 0.25s ease;
}

[data-testid="stVerticalBlockBorderWrapper"]:hover {
    border-color: rgba(0, 145, 255, 0.5);
    box-shadow: 0 10px 28px rgba(0, 145, 255, 0.14);
    transform: translateY(-3px);
}

.tool-card-icon {
    font-size: 2.2rem;
}

.tool-card-title {
    font-family: 'Orbitron', sans-serif;
    font-size: 1.05rem;
    color: #1c2333;
    margin: 8px 0 4px 0;
}

.tool-card-desc {
    font-size: 0.85rem;
    color: #5b6785;
    min-height: 3.4em;
}

.home-hero {
    text-align: center;
    padding: 10px 0 28px 0;
}

.home-hero-sub {
    color: #5b6785;
    font-size: 1.05rem;
    letter-spacing: 0.5px;
}

hr {
    border-color: rgba(0, 145, 255, 0.18) !important;
}

textarea, input {
    background-color: #ffffff !important;
    color: #1c2333 !important;
    border: 1px solid rgba(0, 145, 255, 0.25) !important;
    border-radius: 8px !important;
}
</style>
"""
