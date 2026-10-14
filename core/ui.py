import streamlit as st

PREMIUM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

.stApp {
    background:
        radial-gradient(ellipse at 50% 0%, #19264a 0%, transparent 48%),
        #080d18;
    color: #eef3ff;
    font-family: 'Inter', sans-serif;
}
[data-testid="stSidebar"] {
    background: #0a1120;
    border-right: 1px solid #22314d;
}
h1, h2, h3 { color: #f3f6ff; letter-spacing: -0.5px; }
[data-testid="stChatMessage"] {
    background: rgba(18, 29, 51, 0.82);
    border: 1px solid #22314d;
    border-radius: 18px;
    padding: 16px;
    margin-bottom: 12px;
}
[data-testid="stChatInput"] {
    border: 1px solid #5843a8;
    border-radius: 18px;
    background: #111b30;
    box-shadow: 0 0 24px rgba(112, 71, 255, 0.10);
}
.stButton > button {
    background: linear-gradient(115deg, #5937e8, #236fe9);
    color: white;
    border: 1px solid #7259ff;
    border-radius: 12px;
    padding: 0.6rem 1rem;
    font-weight: 600;
}
.stButton > button:hover {
    border-color: #7bdcff;
    box-shadow: 0 0 18px rgba(88, 111, 255, 0.3);
}
[data-testid="stFileUploader"] {
    background: rgba(16, 24, 42, 0.7);
    border: 1px dashed #4e5f91;
    border-radius: 16px;
    padding: 12px;
}
hr { border-color: #22314d; }
.hero {
    padding: 26px 16px;
    text-align: center;
    border: 1px solid #26365a;
    border-radius: 24px;
    margin-bottom: 22px;
    background: linear-gradient(140deg,
        rgba(93, 65, 190, .18),
        rgba(23, 122, 215, .08),
        rgba(12, 20, 38, .55));
}
.hero-title {
    font-size: 38px;
    font-weight: 800;
    background: linear-gradient(90deg, #c7b6ff, #7a8cff, #50d9ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.muted { color: #91a5c8; }
.card {
    padding: 18px;
    border-radius: 18px;
    border: 1px solid #26365a;
    background: rgba(18, 29, 51, 0.6);
    margin-bottom: 14px;
}
@media (max-width: 768px) {
    .block-container { padding-left: 1rem; padding-right: 1rem; }
    .hero-title { font-size: 28px; }
}
</style>
"""


def inject_css():
    st.markdown(PREMIUM_CSS, unsafe_allow_html=True)


def hero(title, subtitle, icon="✦"):
    st.markdown(f"""
    <div class="hero">
        <div style="font-size:42px;">{icon}</div>
        <div class="hero-title">{title}</div>
        <p class="muted">{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)