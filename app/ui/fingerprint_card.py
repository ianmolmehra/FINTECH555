import streamlit as st

def render_fingerprint_card(dis, panic, dna, skill, draw):
    words = _generate_words(dis, panic, dna, skill, draw)
    color_map = {"green": "#00C853", "red": "#FF5252", "amber": "#FFD600"}
    words_html = ""
    for word, color in words:
        hex_color = color_map[color]
        words_html += f'<div style="font-size:1.8rem;font-weight:900;color:{hex_color};letter-spacing:0.05em;line-height:1.5;text-shadow:0 0 20px {hex_color}44;">{word}</div>'
    html = (
        '<div style="background:linear-gradient(135deg,#060D06,#0D2B0D);border:2px solid #00C85344;border-radius:16px;padding:24px 32px;margin:16px 0;text-align:center;">'
        '<p style="color:#81C784;font-size:0.85rem;margin:0 0 12px 0;letter-spacing:0.1em;">🧬 YOUR BEHAVIORAL FINGERPRINT</p>'
        + words_html +
        '<p style="color:#4CAF50;font-size:0.78rem;margin:14px 0 0 0;">AI-generated from 5 analytical dimensions · Updates with every upload</p>'
        '</div>'
    )
    st.markdown(html, unsafe_allow_html=True)

def _generate_words(dis, panic, dna, skill, draw):
    words = []
    patience_score = dis.get("sub_scores", {}).get("patience_score", 10)
    dis_score = dis.get("score", 50)
    if dis_score >= 75:
        words.append(("Disciplined.", "green"))
    elif patience_score >= 14:
        words.append(("Patient.", "green"))
    elif patience_score >= 8:
        words.append(("Reactive.", "amber"))
    else:
        words.append(("Impulsive.", "red"))

    sizing_score = dis.get("sub_scores", {}).get("sizing_control", 8)
    overconf = panic.get("overconfidence_score", 50)
    if sizing_score >= 12 and overconf < 40:
        words.append(("Precise.", "green"))
    elif overconf > 65:
        words.append(("Oversized.", "red"))
    elif sizing_score < 6:
        words.append(("Inconsistent.", "red"))
    else:
        words.append(("Cautious.", "amber"))

    panic_pct = panic.get("panic_pct", 25)
    revenge_pct = panic.get("revenge_pct", 15)
    bhs = panic.get("behavioral_health_score", 50)
    if panic_pct > 35 and revenge_pct > 20:
        words.append(("Panic-prone.", "red"))
    elif bhs >= 70:
        words.append(("Composed.", "green"))
    elif panic_pct > 25:
        words.append(("Nervous.", "amber"))
    else:
        words.append(("Resilient.", "green"))

    skill_pct = skill.get("skill_pct", 50)
    sharpe = skill.get("sharpe", 0)
    if skill_pct >= 65 and sharpe > 0.8:
        words.append(("Skilled.", "green"))
    elif skill_pct >= 55:
        words.append(("Developing.", "amber"))
    else:
        words.append(("Luck-dependent.", "red"))

    max_dd = draw.get("max_drawdown_pct", 25)
    calmar = draw.get("calmar_ratio", 0.5)
    if max_dd < 12 and calmar > 1.5:
        words.append(("Risk-aware.", "green"))
    elif max_dd > 30:
        words.append(("Overexposed.", "red"))
    elif max_dd < 20:
        words.append(("Balanced.", "amber"))
    else:
        words.append(("Volatile.", "red"))

    return words
