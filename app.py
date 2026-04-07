
import streamlit as st
import base64
from pathlib import Path
from diff_engine import compare_files, format_output

st.set_page_config(
    page_title="Labcorp | Text Diff Analyzer",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------- LOAD LOGO ----------
def get_logo_base64(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

# Try to load logo; fall back gracefully
try:
    logo_b64 = get_logo_base64("labcorp_logo.png")
    logo_html = f'<img src="data:image/png;base64,{logo_b64}" class="nav-logo" alt="Labcorp"/>'
except Exception:
    logo_html = '<span class="nav-logo-text">labcorp</span>'

# ---------- GLOBAL STYLES ----------
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

/* ── Reset & base ── */
*, *::before, *::after {{ box-sizing: border-box; }}

html, body, [class*="css"] {{
    font-family: 'DM Sans', sans-serif;
    color: #1a2332 !important;
}}

/* ── App background ── */
.stApp {{
    background: #f0f4f9;
    min-height: 100vh;
}}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header {{ visibility: hidden; }}
.block-container {{
    padding-top: 0 !important;
    padding-bottom: 2rem !important;
    max-width: 1200px;
}}

/* ══════════════════════════════════════
   NAVBAR
══════════════════════════════════════ */
.labcorp-nav {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: #ffffff;
    border-bottom: 1px solid #dce4ef;
    padding: 0 2.5rem;
    height: 68px;
    position: sticky;
    top: 0;
    z-index: 999;
    box-shadow: 0 2px 12px rgba(0,0,0,.06);
    margin-bottom: 0;
}}

.nav-logo {{
    height: 36px;
    width: auto;
    object-fit: contain;
}}

.nav-logo-text {{
    font-size: 1.6rem;
    font-weight: 700;
    color: #1a2332;
    letter-spacing: -0.02em;
}}

.nav-badge {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: #e8f4ff;
    color: #0077cc;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    padding: 5px 12px;
    border-radius: 20px;
    border: 1px solid #b3d9f5;
}}

.nav-dot {{
    width: 6px;
    height: 6px;
    background: #00aaff;
    border-radius: 50%;
    animation: pulse 2s ease-in-out infinite;
}}

@keyframes pulse {{
    0%, 100% {{ opacity: 1; transform: scale(1); }}
    50%       {{ opacity: .5; transform: scale(1.3); }}
}}

/* ══════════════════════════════════════
   HERO HEADER
══════════════════════════════════════ */
.hero {{
    background: linear-gradient(135deg, #0059b3 0%, #0099e6 60%, #00bfff 100%);
    padding: 3.5rem 2.5rem 3rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}}

.hero::before {{
    content: '';
    position: absolute;
    inset: 0;
    background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.04'%3E%3Ccircle cx='30' cy='30' r='28'/%3E%3Ccircle cx='30' cy='30' r='18'/%3E%3Ccircle cx='30' cy='30' r='8'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E") repeat;
    pointer-events: none;
}}

.hero-title {{
    font-size: 2.2rem;
    font-weight: 700;
    color: #ffffff;
    margin: 0 0 .6rem 0;
    letter-spacing: -0.03em;
    position: relative;
}}

.hero-sub {{
    font-size: 1rem;
    color: rgba(255,255,255,.82);
    font-weight: 400;
    margin: 0;
    position: relative;
}}

.hero-stats {{
    display: flex;
    gap: 2rem;
    margin-top: 1.8rem;
    position: relative;
}}

.hero-stat {{
    text-align: center;
}}

.hero-stat-num {{
    display: block;
    font-size: 1.6rem;
    font-weight: 700;
    color: #ffffff;
    line-height: 1;
}}

.hero-stat-lbl {{
    display: block;
    font-size: 0.7rem;
    color: rgba(255,255,255,.7);
    text-transform: uppercase;
    letter-spacing: .08em;
    margin-top: 3px;
}}

/* ══════════════════════════════════════
   CARD
══════════════════════════════════════ */
.card {{
    background: #ffffff;
    border-radius: 14px;
    border: 1px solid #dce4ef;
    padding: 1.6rem 1.8rem;
    margin-bottom: 1.25rem;
    box-shadow: 0 1px 6px rgba(0,0,0,.04);
}}

.card-title {{
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: .1em;
    color: #0077cc;
    margin: 0 0 1.1rem 0;
}}

/* ══════════════════════════════════════
   SECTION LABELS
══════════════════════════════════════ */
.section-label {{
    font-size: 0.65rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: .12em;
    color: #8899aa;
    margin-bottom: .45rem;
    display: block;
}}

/* ══════════════════════════════════════
   RESULT PILLS
══════════════════════════════════════ */
.result-pill {{
    display: flex;
    align-items: flex-start;
    gap: 10px;
    padding: 10px 14px;
    border-radius: 10px;
    margin-bottom: 8px;
    font-family: 'DM Mono', monospace;
    font-size: 0.8rem;
    line-height: 1.5;
}}

.pill-added {{
    background: #e8faf0;
    border: 1px solid #a8e6c3;
    color: #1a6b3a;
}}

.pill-removed {{
    background: #fef0f0;
    border: 1px solid #f5b8b8;
    color: #8b2020;
}}

.pill-modified {{
    background: #fffbea;
    border: 1px solid #f0d87a;
    color: #7a5500;
}}

.pill-icon {{
    font-size: 1rem;
    line-height: 1.4;
    flex-shrink: 0;
}}

.pill-line {{
    font-size: 0.68rem;
    font-weight: 600;
    opacity: .65;
    margin-right: 6px;
}}

/* ══════════════════════════════════════
   STAT SUMMARY BOXES
══════════════════════════════════════ */
.stat-box {{
    border-radius: 12px;
    padding: 1.2rem;
    text-align: center;
}}

.stat-box-added   {{ background: #e8faf0; border: 1px solid #a8e6c3; }}
.stat-box-removed {{ background: #fef0f0; border: 1px solid #f5b8b8; }}
.stat-box-modified{{ background: #fffbea; border: 1px solid #f0d87a; }}

.stat-box-num {{
    font-size: 2rem;
    font-weight: 700;
    line-height: 1;
    display: block;
}}

.stat-box-added   .stat-box-num {{ color: #1a6b3a; }}
.stat-box-removed .stat-box-num {{ color: #8b2020; }}
.stat-box-modified .stat-box-num {{ color: #7a5500; }}

.stat-box-label {{
    font-size: 0.68rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: .09em;
    opacity: .7;
    margin-top: 4px;
    display: block;
}}

/* ══════════════════════════════════════
   Streamlit widget overrides
══════════════════════════════════════ */
/* Radio */
.stRadio > label {{
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: .08em !important;
    color: #0077cc !important;
}}

/* File uploader */
[data-testid="stFileUploader"] {{
    background: #f7faff !important;
    border: 2px dashed #b3d9f5 !important;
    border-radius: 10px !important;
}}

/* Text area */
.stTextArea textarea {{
    background: #f7faff !important;
    border: 1.5px solid #b3d9f5 !important;
    border-radius: 10px !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.82rem !important;
}}

.stTextArea textarea:focus {{
    border-color: #0099e6 !important;
    box-shadow: 0 0 0 3px rgba(0,153,230,.15) !important;
}}

/* Primary button */
.stButton > button {{
    background: linear-gradient(135deg, #0059b3, #0099e6) !important;
    color: #fff !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    letter-spacing: .03em !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.65rem 1.5rem !important;
    transition: all .2s ease !important;
    box-shadow: 0 4px 14px rgba(0,89,179,.25) !important;
}}

.stButton > button:hover {{
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 20px rgba(0,89,179,.35) !important;
}}

/* Download button */
.stDownloadButton > button {{
    background: linear-gradient(135deg, #00873e, #00b356) !important;
    color: #fff !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    border: none !important;
    border-radius: 10px !important;
    box-shadow: 0 4px 14px rgba(0,135,62,.25) !important;
}}

/* Divider */
hr {{ border-color: #dce4ef !important; }}

/* Subheader */
h3 {{
    font-size: 0.95rem !important;
    font-weight: 600 !important;
    color: #1a2332 !important;
    margin-bottom: .5rem !important;
}}
</style>

<!-- ══ NAVBAR ══ -->
<div class="labcorp-nav">
    {logo_html}
    <div class="nav-badge">
        <span class="nav-dot"></span>
        Text Diff Analyzer
    </div>
</div>

<!-- ══ HERO ══ -->
<div class="hero">
    <p class="hero-title">Text Difference Analyzer</p>
    <p class="hero-sub">Compare two text sources and instantly detect added, removed, and modified lines with precision.</p>
    <div class="hero-stats">
        <div class="hero-stat">
            <span class="hero-stat-num">3</span>
            <span class="hero-stat-lbl">Change Types</span>
        </div>
        <div class="hero-stat">
            <span class="hero-stat-num">TXT</span>
            <span class="hero-stat-lbl">File Support</span>
        </div>
        <div class="hero-stat">
            <span class="hero-stat-num">↓</span>
            <span class="hero-stat-lbl">Exportable</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------- INPUT MODE ----------
st.markdown('<div class="card"><p class="card-title">Input Configuration</p>', unsafe_allow_html=True)

input_option = st.radio(
    "Choose Input Method",
    ["📂  Upload TXT Files", "✏️  Enter Text Manually"],
    horizontal=True,
    key="input_option",
    label_visibility="collapsed"
)

st.markdown('</div>', unsafe_allow_html=True)

old_text = ""
new_text = ""

# ---------- FILE UPLOAD ----------
if "Upload" in input_option:
    st.markdown('<div class="card"><p class="card-title">File Upload</p>', unsafe_allow_html=True)
    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown('<span class="section-label">Original / Old File</span>', unsafe_allow_html=True)
        old_file = st.file_uploader("Old File", type=["txt"], key="old_file", label_visibility="collapsed")

    with col2:
        st.markdown('<span class="section-label">Revised / New File</span>', unsafe_allow_html=True)
        new_file = st.file_uploader("New File", type=["txt"], key="new_file", label_visibility="collapsed")

    if old_file and new_file:
        old_text = old_file.read().decode("utf-8")
        new_text = new_file.read().decode("utf-8")

    st.markdown('</div>', unsafe_allow_html=True)

# ---------- MANUAL INPUT ----------
else:
    st.markdown('<div class="card"><p class="card-title">Manual Text Entry</p>', unsafe_allow_html=True)
    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown('<span class="section-label">Original / Old Text</span>', unsafe_allow_html=True)
        old_text = st.text_area("Old Text", height=260, key="old_text", label_visibility="collapsed",
                                placeholder="Paste your original text here…")

    with col2:
        st.markdown('<span class="section-label">Revised / New Text</span>', unsafe_allow_html=True)
        new_text = st.text_area("New Text", height=260, key="new_text", label_visibility="collapsed",
                                placeholder="Paste your revised text here…")

    st.markdown('</div>', unsafe_allow_html=True)

# ---------- RUN DIFF ----------
st.markdown("")
run = st.button("⟳  Run Text Diff", use_container_width=True, key="run_diff")

if run:
    if old_text and new_text:

        old_lines = old_text.splitlines()
        new_lines = new_text.splitlines()

        added, removed, modified = compare_files(old_lines, new_lines)

        # ── Summary row ──
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="card"><p class="card-title">Summary</p>', unsafe_allow_html=True)
        sA, sB, sC = st.columns(3, gap="large")

        with sA:
            st.markdown(f"""
            <div class="stat-box stat-box-added">
                <span class="stat-box-num">{len(added)}</span>
                <span class="stat-box-label">Lines Added</span>
            </div>""", unsafe_allow_html=True)

        with sB:
            st.markdown(f"""
            <div class="stat-box stat-box-removed">
                <span class="stat-box-num">{len(removed)}</span>
                <span class="stat-box-label">Lines Removed</span>
            </div>""", unsafe_allow_html=True)

        with sC:
            st.markdown(f"""
            <div class="stat-box stat-box-modified">
                <span class="stat-box-num">{len(modified)}</span>
                <span class="stat-box-label">Lines Modified</span>
            </div>""", unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        # ── Detailed results ──
        st.markdown('<div class="card"><p class="card-title">Detailed Changes</p>', unsafe_allow_html=True)
        colA, colB, colC = st.columns(3, gap="large")

        with colA:
            st.markdown('<span class="section-label">➕ Added</span>', unsafe_allow_html=True)
            if added:
                for line_no, text in added:
                    st.markdown(
                        f'<div class="result-pill pill-added">'
                        f'<span class="pill-icon">＋</span>'
                        f'<span><span class="pill-line">L{line_no}</span>{text}</span>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
            else:
                st.markdown("<small style='color:#8899aa'>No lines added.</small>", unsafe_allow_html=True)

        with colB:
            st.markdown('<span class="section-label">➖ Removed</span>', unsafe_allow_html=True)
            if removed:
                for line_no, text in removed:
                    st.markdown(
                        f'<div class="result-pill pill-removed">'
                        f'<span class="pill-icon">－</span>'
                        f'<span><span class="pill-line">L{line_no}</span>{text}</span>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
            else:
                st.markdown("<small style='color:#8899aa'>No lines removed.</small>", unsafe_allow_html=True)

        with colC:
            st.markdown('<span class="section-label">✎ Modified</span>', unsafe_allow_html=True)
            if modified:
                for line_no, old, new in modified:
                    st.markdown(
                        f'<div class="result-pill pill-modified">'
                        f'<span class="pill-icon">≠</span>'
                        f'<div><span class="pill-line">L{line_no}</span>'
                        f'<br><span style="opacity:.6">OLD →</span> {old}'
                        f'<br><span style="opacity:.6">NEW →</span> {new}</div>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
            else:
                st.markdown("<small style='color:#8899aa'>No lines modified.</small>", unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        # ── Download ──
        result = format_output(added, removed, modified)
        st.markdown("<br>", unsafe_allow_html=True)
        st.download_button(
            "⬇  Download Result File",
            data=result,
            file_name="text_diff_result.txt",
            mime="text/plain",
            key="download",
            use_container_width=True
        )

    else:
        st.warning("⚠️  Please provide both Original and Revised text before running the diff.")