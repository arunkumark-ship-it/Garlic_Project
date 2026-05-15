"""utils/style.py  —  Shared CSS injected once on every page."""
import streamlit as st

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');
:root{
  --green:#1a7f4b;--green2:#25a862;--gold:#e8a020;
  --dark:#0d1f14;--card:#f5f9f6;--border:#c8e6d4;
  --text:#1a2e22;--muted:#5a7a65;
}
html,body,[class*="css"]{font-family:'DM Sans',sans-serif;color:var(--text)}
h1,h2,h3{font-family:'Syne',sans-serif}
.stApp{background:#eef5f0}
header[data-testid="stHeader"]{background:transparent}

/* Topbar */
.topbar{display:flex;align-items:center;justify-content:space-between;
  background:var(--green);color:#fff;padding:.75rem 1.5rem;
  border-radius:14px;margin-bottom:1.2rem;
  box-shadow:0 4px 20px rgba(26,127,75,.2)}
.topbar-title{font-family:'Syne',sans-serif;font-weight:700;font-size:1.1rem}
.role-badge{background:rgba(255,255,255,.25);padding:3px 12px;border-radius:20px;
  font-size:.72rem;font-weight:700;text-transform:uppercase;letter-spacing:.5px}
.uid-chip{font-family:monospace;font-size:.72rem;background:rgba(255,255,255,.15);
  padding:3px 10px;border-radius:20px}

/* Section label */
.sl{font-family:'Syne',sans-serif;font-weight:700;font-size:.75rem;
  letter-spacing:.8px;text-transform:uppercase;color:var(--green);
  padding-bottom:.4rem;border-bottom:2px solid var(--border);margin-bottom:.8rem}
.sl-amber{color:#854f0b}
.sl-blue{color:#185fa5}

/* Card */
.fcard{background:#fff;border-radius:16px;padding:1.4rem 1.2rem;
  box-shadow:0 2px 16px rgba(0,0,0,.06);border:1px solid var(--border);
  margin-bottom:1rem}

/* Pills */
.pill{display:inline-block;font-size:.75rem;padding:3px 12px;
  border-radius:20px;font-weight:600}
.pill-pend{background:#fff3cd;color:#856404}
.pill-done{background:#d4edda;color:#1a7f4b}
.pill-fail{background:#f8d7da;color:#842029}
.pill-part{background:#cce5ff;color:#004085}
.pill-active{background:#d4edda;color:#1a7f4b}
.pill-offline{background:#e2e3e5;color:#383d41}
.pill-on{background:#d4edda;color:#1a7f4b}
.pill-off{background:#e2e3e5;color:#383d41}

/* Map box */
.map-frame{border-radius:12px;overflow:hidden;border:2px solid var(--border);margin-top:.5rem}

/* Streamlit overrides */
div[data-testid="stTextInput"] input,
div[data-testid="stSelectbox"] select,
div[data-testid="stNumberInput"] input,
div[data-testid="stTextArea"] textarea{
  border-radius:10px !important;border-color:var(--border) !important}
.stButton>button{border-radius:12px !important;font-family:'Syne',sans-serif !important;font-weight:700 !important}
.stButton>button[kind="primary"]{background:var(--green) !important;border:none !important;color:#fff !important}
div[data-testid="stTabs"] button[role="tab"]{font-family:'Syne',sans-serif;font-weight:600}
.stSuccess{border-radius:10px !important}
.stAlert{border-radius:10px !important}
</style>
"""

def inject():
    st.markdown(CSS, unsafe_allow_html=True)

def map_embed(address: str, height: int = 280) -> str:
    if not address or not address.strip():
        return ""
    enc = address.strip().replace(" ", "+")
    return f"""
    <div class="map-frame">
      <iframe width="100%" height="{height}" frameborder="0"
        style="border:0;display:block" allowfullscreen
        src="https://maps.google.com/maps?q={enc}&output=embed&z=15">
      </iframe>
    </div>"""

def pill(text: str, cls: str = "pill-pend") -> str:
    return f'<span class="pill {cls}">{text}</span>'

def section(label: str, color: str = "") -> str:
    cls = f"sl sl-{color}" if color else "sl"
    return f'<div class="{cls}">{label}</div>'
