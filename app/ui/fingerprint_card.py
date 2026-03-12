# =============================================================================
# FINTECH555 — Decision Intelligence Platform
# File: app/ui/fingerprint_card.py
# Purpose: Behavioral Fingerprint Card — auto-generates a 5-word personality
#          summary from all module scores. Most memorable demo-day feature.
# Design: Large text, dark card, color-coded words (green=strength, red=weakness)
# =============================================================================

import streamlit as st


def render_fingerprint_card(dis: dict, panic: dict, dna: dict,
                             skill: dict, draw: dict):
    """
    Render the Behavioral Fingerprint Card at the top of the report.

    Generates a 5-word trader personality phrase from score combinations.
    Each word is derived from a unique score threshold condition — not a template.
    Example outputs:
        'Patient. Oversized. Panic-prone. Sector-blind. Improving.'
        'Disciplined. Precise. Loss-averse. Pharma-edge. Accelerating.'

    Args:
        dis:   Decision Intelligence Score result dict (Module 1)
        panic: Panic & Bias detection result dict (Module 2)
        dna:   Trader DNA result dict (Module 5)
        skill: Skill vs Luck result dict (Module 6)
        draw:  Drawdown analysis result dict (Module 11)
    """
    # ── Generate 5-word fingerprint from score thresholds
    words = _generate_words(dis, panic, dna, skill, draw)

    # ── Color map: green = strength, red = weakness, amber = neutral
    color_map = {"green": "#00C853", "red": "#FF5252", "amber": "#FFD600"}

    # ── Build HTML for each word separately — avoids .format() clash with CSS braces
    words_html = ""
    for word, color in words:
        hex_color = color_map[color]
        words_html += (
            f'<div style="'
            f'font-size:1.8rem;'
            f'font-weight:900;'
            f'color:{hex_color};'
            f'letter-spacing:0.05em;'
            f'line-height:1.5;'
            f'text-shadow:0 0 20px {hex_color}44;'
            f'">{word}</div>'
        )

    # ── Assemble full card — no .format() call, no conflicting braces
    html = (
        '<div style="'
        'background:linear-gradient(135deg,#060D06,#0D2B0D);'
        'border:2px solid #00C85344;'
        'border-radius:16px;'
        'padding:24px 32px;'
        'margin:16px 0;'
        'text-align:center;'
        '">'
        '<p style="color:#81C784;font-size:0.85rem;margin:0 0 12px 0;letter-spacing:0.1em;">'
        '🧬 YOUR BEHAVIORAL FINGERPRINT'
        '</p>'
        + words_html +
        '<p style="color:#4CAF50;font-size:0.78rem;margin:14px 0 0 0;">'
        'AI-generated from 5 analytical dimensions · Updates with every upload'
        '</p>'
        '</div>'
    )

    st.markdown(html, unsafe_allow_html=True)


def _generate_words(dis: dict, panic: dict, dna: dict,
                    skill: dict, draw: dict) -> list:
    """
    Generate the 5-word fingerprint by checking score thresholds.
    Each dimension maps to exactly one word based on multi-condition logic.
    Returns list of (word, color) tuples.
    """
    words = []

    # ── DIMENSION 1: Decision Quality (from DIS patience sub-score)
    # Patience score: 0-20 range from decision_score.py
    patience_score = dis.get("sub_scores", {}).get("patience_score", 10)
    dis_score = dis.get("score", 50)
    if dis_score >= 75:
        words.append(("Disciplined.", "green"))    # High DIS = genuinely disciplined
    elif patience_score >= 14:
        words.append(("Patient.", "green"))        # Good patience even if DIS not highest
    elif patience_score >= 8:
        words.append(("Reactive.", "amber"))       # Mid patience = reactive trader
    else:
        words.append(("Impulsive.", "red"))        # Low patience = impulsive decisions

    # ── DIMENSION 2: Position Sizing (from panic overconfidence + dis sizing)
    sizing_score = dis.get("sub_scores", {}).get("sizing_control", 8)
    overconf = panic.get("overconfidence_score", 50)
    if sizing_score >= 12 and overconf < 40:
        words.append(("Precise.", "green"))        # Good sizing + low overconfidence
    elif overconf > 65:
        words.append(("Oversized.", "red"))        # High overconfidence = overbetting
    elif sizing_score < 6:
        words.append(("Inconsistent.", "red"))     # Low sizing control
    else:
        words.append(("Cautious.", "amber"))       # Moderate, neither great nor bad

    # ── DIMENSION 3: Behavioral Pattern (from panic rates)
    panic_pct = panic.get("panic_pct", 25)
    revenge_pct = panic.get("revenge_pct", 15)
    bhs = panic.get("behavioral_health_score", 50)
    if panic_pct > 35 and revenge_pct > 20:
        words.append(("Panic-prone.", "red"))      # Both panic AND revenge = serious issue
    elif bhs >= 70:
        words.append(("Composed.", "green"))       # High behavioral health score
    elif panic_pct > 25:
        words.append(("Nervous.", "amber"))        # Moderate panic but not severe
    else:
        words.append(("Resilient.", "green"))      # Low panic = emotional resilience

    # ── DIMENSION 4: Skill Level (from skill_vs_luck)
    skill_pct = skill.get("skill_pct", 50)
    sharpe = skill.get("sharpe", 0)
    if skill_pct >= 65 and sharpe > 0.8:
        words.append(("Skilled.", "green"))        # High skill AND strong Sharpe
    elif skill_pct >= 55:
        words.append(("Developing.", "amber"))     # Moderate skill — still learning
    elif skill_pct < 45:
        words.append(("Luck-dependent.", "red"))   # Below 45% = likely lucky, not skilled

    # ── DIMENSION 5: Risk Management (from drawdown)
    max_dd = draw.get("max_drawdown_pct", 25)
    calmar = draw.get("calmar_ratio", 0.5)
    if max_dd < 12 and calmar > 1.5:
        words.append(("Risk-aware.", "green"))     # Low drawdown + good Calmar = risk master
    elif max_dd > 30:
        words.append(("Overexposed.", "red"))      # Very high drawdown = poor risk management
    elif max_dd < 20:
        words.append(("Balanced.", "amber"))       # Moderate drawdown — room to improve
    else:
        words.append(("Volatile.", "red"))         # High drawdown without Calmar to compensate

    return words