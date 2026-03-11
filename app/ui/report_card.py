# =============================================================================
# FINTECH555 — Decision Intelligence Platform
# File: app/ui/report_card.py
# Purpose: Master Report Card — single-page summary of all module scores.
#          Grade system: A (≥80), B (≥65), C (≥50), D (≥35), F (<35)
# =============================================================================

import streamlit as st


def score_to_grade(score: float, max_score: float = 100) -> tuple:
    """
    Convert numeric score to letter grade with color.
    Grade thresholds: A≥80, B≥65, C≥50, D≥35, F<35.
    Returns (grade_letter, color_hex).
    """
    pct = (score / max_score) * 100  # Normalize to percentage first
    if pct >= 80:   return "A", "#00C853"   # Green: excellent
    elif pct >= 65: return "B", "#69F0AE"   # Light green: good
    elif pct >= 50: return "C", "#FFD600"   # Amber: average
    elif pct >= 35: return "D", "#FF9800"   # Orange: below average
    else:           return "F", "#FF5252"   # Red: poor


def render_report_card(dis: dict, panic: dict, skill: dict,
                       tax: dict, draw: dict, peer: dict):
    """
    Render the master Report Card with letter grades per dimension.
    Displayed at the bottom of the report as a single unified scorecard.

    Args:
        dis:   Decision Intelligence Score result (Module 1)
        panic: Panic detection result (Module 2)
        skill: Skill vs Luck result (Module 6)
        tax:   Tax intelligence result (Module 8)
        draw:  Drawdown analysis result (Module 11)
        peer:  Peer comparison result (Module 19)
    """
    st.markdown("### 📊 FINTECH555 — Master Report Card")
    st.caption("Letter grades assigned per dimension based on score thresholds.")

    # ── Define all graded dimensions with their scores
    # Each entry: (display_label, score, max_score, description)
    dimensions = [
        ("Decision Intelligence",   dis.get("score", 0),                       100, "Overall decision quality"),
        ("Behavioral Health",        panic.get("behavioral_health_score", 0),   100, "Panic, revenge, bias control"),
        ("Exit Discipline",          dis.get("exit_discipline", 0),              25, "Exit timing precision"),
        ("Skill Level",              skill.get("skill_pct", 50),                100, "Skill vs luck decomposition"),
        ("Sharpe Ratio (norm.)",     min(100, max(0, skill.get("sharpe", 0) * 40)), 100, "Risk-adjusted return"),
        ("Tax Efficiency",           tax.get("tax_opt_score", 0),               100, "LTCG optimization score"),
        ("Drawdown Control",         max(0, 100 - draw.get("max_drawdown_pct", 50) * 2), 100, "Peak-to-trough loss control"),
        ("Peer Percentile",          peer.get("overall_percentile", 50),        100, "vs. retail investor benchmark"),
    ]

    # ── Render grade cards in a 4-column grid
    cols = st.columns(4)
    for i, (label, score, max_s, desc) in enumerate(dimensions):
        grade, color = score_to_grade(score, max_s)
        with cols[i % 4]:
            # Each card shows: grade letter (large), score, label, description
            st.markdown(f"""
            <div style="
                background: #111811;
                border: 1px solid {color}44;
                border-top: 3px solid {color};
                border-radius: 10px;
                padding: 14px 12px;
                text-align: center;
                margin: 4px 0;
            ">
                <div style="font-size:2.2rem;font-weight:900;color:{color};line-height:1;">{grade}</div>
                <div style="font-size:0.9rem;color:#E8F5E9;font-weight:600;margin:4px 0 2px;">
                    {score:.0f}/{max_s}
                </div>
                <div style="font-size:0.75rem;color:#81C784;font-weight:600;">{label}</div>
                <div style="font-size:0.68rem;color:#4CAF50;margin-top:3px;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    # ── Overall composite grade
    all_scores = [s / m * 100 for _, s, m, _ in dimensions]
    composite = sum(all_scores) / len(all_scores)
    comp_grade, comp_color = score_to_grade(composite, 100)

    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #0A1A0A, #0D2B0D);
        border: 2px solid {comp_color};
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        margin-top: 16px;
    ">
        <span style="color:#81C784;font-size:0.85rem;">OVERALL COMPOSITE GRADE</span>
        <div style="font-size:3rem;font-weight:900;color:{comp_color};line-height:1.2;">
            {comp_grade} — {composite:.0f}/100
        </div>
        <p style="color:#4CAF50;margin:8px 0 0;font-size:0.85rem;">
            Based on {len(dimensions)} analytical dimensions · 
            {peer.get('overall_percentile', 50):.0f}th percentile vs retail traders
        </p>
    </div>
    """, unsafe_allow_html=True)
