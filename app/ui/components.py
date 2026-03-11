# =============================================================================
# FINTECH555 — Reusable UI Components: KPI Strip, XAI Card, Action Box
# =============================================================================
import streamlit as st


def kpi_strip(metrics: list):
    """
    Render horizontal KPI strip with metric cards.
    Accepts both tuples (label, value) and dicts {"label":..., "value":...}.
    """
    cols = st.columns(len(metrics))
    for col, m in zip(cols, metrics):
        with col:
            if isinstance(m, (list, tuple)):
                label = m[0]
                value = m[1]
                delta = m[2] if len(m) > 2 else None
            else:
                label = m["label"]
                value = m["value"]
                delta = m.get("delta")
            st.metric(label=label, value=value, delta=delta)


def xai_card(text: str):
    """Render the AI analyst explanation card."""
    st.markdown(f'<div class="xai-card">🧠 <strong>AI Analysis:</strong><br><br>{text}</div>', unsafe_allow_html=True)


def action_box(text: str):
    """Render the single actionable recommendation box."""
    st.markdown(f'<div class="action-box">⚡ <strong>ACTION:</strong> {text}</div>', unsafe_allow_html=True)


def grade_badge_html(grade: str, score: float) -> str:
    colors = {"A": "#00C853", "B": "#64DD17", "C": "#FFD600", "D": "#FF9800", "F": "#FF5252"}
    letter = grade[0] if grade else "C"
    return f'<span style="background:{colors.get(letter,"#81C784")};color:#000;padding:4px 12px;border-radius:20px;font-weight:700;">{grade} ({score})</span>'


def section_header(title: str, subtitle: str = ""):
    """Styled section header with optional subtitle."""
    st.markdown(f"""
    <div style="border-left:4px solid #00C853;padding:6px 0 6px 14px;margin:16px 0 10px 0;">
        <h3 style="color:#00C853;margin:0;font-size:1.15rem;">{title}</h3>
        {'<p style="color:#81C784;margin:2px 0 0 0;font-size:0.82rem;">' + subtitle + '</p>' if subtitle else ''}
    </div>
    """, unsafe_allow_html=True)


def insight_card(title: str, text: str):
    """Render an XAI insight card with analyst voice text."""
    st.markdown(f"""
    <div style="background:#0D1A0D;border:1px solid #00C85333;border-left:4px solid #00C853;
         border-radius:8px;padding:14px 18px;margin:10px 0;">
        <div style="color:#00C853;font-weight:700;font-size:0.9rem;margin-bottom:6px;">{title}</div>
        <div style="color:#C8E6C9;font-size:0.88rem;line-height:1.6;">{text}</div>
    </div>
    """, unsafe_allow_html=True)


def action_card(priority: str, text: str):
    """Render an action recommendation card. priority: HIGH / MEDIUM / LOW"""
    colors = {"HIGH": "#FF5252", "MEDIUM": "#FFD600", "LOW": "#00C853"}
    color  = colors.get(priority.upper(), "#FFD600")
    st.markdown(f"""
    <div style="background:#1A0F0A;border:1px solid {color}44;border-left:4px solid {color};
         border-radius:8px;padding:12px 16px;margin:8px 0;">
        <span style="color:{color};font-weight:700;font-size:0.78rem;">⚡ ACTION [{priority}]</span>
        <div style="color:#FFE0B2;font-size:0.88rem;margin-top:4px;line-height:1.5;">{text}</div>
    </div>
    """, unsafe_allow_html=True)


def risk_flag_card(title: str, description: str):
    """Render a risk warning flag card."""
    st.markdown(f"""
    <div style="background:#1A0808;border:1px solid #FF525244;border-left:4px solid #FF5252;
         border-radius:8px;padding:10px 16px;margin:6px 0;">
        <div style="color:#FF5252;font-weight:700;font-size:0.85rem;">{title}</div>
        <div style="color:#FFCDD2;font-size:0.82rem;margin-top:3px;">{description}</div>
    </div>
    """, unsafe_allow_html=True)


def score_badge(score: float, max_score: float = 100, label: str = ""):
    """Render a color-coded score badge."""
    pct   = (score / max_score) * 100
    color = "#00C853" if pct >= 65 else "#FFD600" if pct >= 45 else "#FF5252"
    st.markdown(f"""
    <span style="background:{color}22;color:{color};border:1px solid {color}44;
         padding:3px 10px;border-radius:12px;font-size:0.82rem;font-weight:700;">
        {label + ': ' if label else ''}{score:.0f}/{max_score:.0f}
    </span>
    """, unsafe_allow_html=True)


def divider():
    """Render a styled section divider."""
    st.markdown("<hr style='border:0;border-top:1px solid #1B2B1B;margin:20px 0;'>",
                unsafe_allow_html=True)