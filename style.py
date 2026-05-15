import sys as _sys, os as _os
_ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
for _p in [_ROOT, _os.path.join(_ROOT,"utils"), _os.path.join(_ROOT,"pages")]:
    if _p not in _sys.path:
        _sys.path.insert(0, _p)

"""utils/style.py — Shared CSS and HTML helpers"""
import streamlit as st

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');
:root{
  --green:#1a7f4b;--green2:#25a862;
  --dark:#0d1f14;--border:#c8e6d4;--text:#1a2e22;--muted:#5a7a65;
}
html,body,[class*="css"]{font-family:'DM Sans',sans-serif;color:var(--text)}
h1,h2,h3{font-family:'Syne',sans-serif}
.stApp{background:#eef5f0}
header[data-testid="stHeader"]{background:transparent}
.sl{font-family:'Syne',sans-serif;font-weight:700;font-size:.75rem;
  letter-spacing:.8px;text-transform:uppercase;color:var(--green);
  padding-bottom:.4rem;border-bottom:2px solid var(--border);margin-bottom:.8rem}
.sl-amber{color:#854f0b}
.sl-blue{color:#185fa5}
.map-frame{border-radius:12px;overflow:hidden;border:2px solid var(--border);margin-top:.5rem}
.pill{display:inline-block;font-size:.75rem;padding:3px 12px;border-radius:20px;font-weight:600}
.pill-pend{background:#fff3cd;color:#856404}
.pill-done{background:#d4edda;color:#1a7f4b}
.pill-fail{background:#f8d7da;color:#842029}
.pill-part{background:#cce5ff;color:#004085}
.pill-on{background:#d4edda;color:#1a7f4b}
.pill-off{background:#e2e3e5;color:#383d41}
div[data-testid="stTextInput"] input,
div[data-testid="stSelectbox"] select,
div[data-testid="stNumberInput"] input,
div[data-testid="stTextArea"] textarea{
  border-radius:10px !important;border-color:var(--border) !important}
.stButton>button{border-radius:12px !important;
  font-family:'Syne',sans-serif !important;font-weight:700 !important}
.stButton>button[kind="primary"]{
  background:var(--green) !important;border:none !important;color:#fff !important}
</style>
"""

def inject():
    st.markdown(CSS, unsafe_allow_html=True)

def map_embed(address: str, height: int = 260) -> str:
    if not address or not address.strip():
        return ""
    enc = address.strip().replace(" ", "+")
    return (f'<div class="map-frame">'
            f'<iframe width="100%" height="{height}" frameborder="0" '
            f'style="border:0;display:block" allowfullscreen '
            f'src="https://maps.google.com/maps?q={enc}&output=embed&z=15">'
            f'</iframe></div>')

def pill(text: str, cls: str = "pill-pend") -> str:
    return f'<span class="pill {cls}">{text}</span>'

def section(label: str, color: str = "") -> str:
    cls = f"sl sl-{color}" if color else "sl"
    return f'<div class="{cls}">{label}</div>'
