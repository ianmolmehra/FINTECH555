# =============================================================================
# FINTECH555 — Decision Intelligence Platform
# File: app/api_integration/llm_explainer_stub.py
# Purpose: Stub for Claude/GPT LLM-powered personalized trade explanations.
#          Phase 1: Rule-based XAI in xai.py. Phase 2: Replace with API call.
# =============================================================================
# TODO Phase 2: pip install anthropic openai

from typing import Optional, Dict, Any


# ── LLM Prompt Template — pass all computed scores as structured context
# This prompt is ready-to-use. Just add API key and uncomment the API call.
EXPLANATION_PROMPT_TEMPLATE = """
You are an expert FinTech behavioral analyst with hedge fund experience.
Analyze the following trader's performance data and provide a personalized,
honest, and actionable analysis. Address the trader directly as "you".
Use specific numbers. Be a real analyst, not a chatbot.

TRADER PERFORMANCE DATA:
- Total Trades: {total_trades}
- Win Rate: {win_rate:.1f}%
- Total PnL: ₹{total_pnl:,.0f}
- Decision Intelligence Score: {dis_score}/100 ({dis_grade})
- Panic Rate: {panic_rate:.1f}%
- Skill vs Luck: {skill_pct:.0f}% Skill / {luck_pct:.0f}% Luck
- Max Drawdown: {max_drawdown:.1f}%
- Kelly Adherence: {kelly_adherence:.1f}%
- Avg Hold Days: {avg_hold:.1f}
- Top Behavioral Biases: {biases}

Provide a 4-6 sentence personalized analysis explaining:
1. What the numbers reveal about this trader's decision-making psychology
2. The single most damaging pattern in their trading behavior
3. One concrete, measurable action they can take immediately to improve
"""


def generate_llm_explanation(scores: Dict[str, Any]) -> Optional[str]:
    """
    Generate a personalized LLM explanation using the trader's computed scores.
    Phase 1: Returns None — rule-based XAI in xai.py is used instead.
    Phase 2: Pass API key and uncomment the API call block.

    Args:
        scores: Dict of all computed analytics scores from all modules.
                Keys match the prompt template placeholders above.

    Returns:
        Personalized explanation string from Claude/GPT, or None in Phase 1.
    """
    # Phase 2 — Claude API (Anthropic):
    # TODO: Add your Anthropic API key as environment variable ANTHROPIC_API_KEY
    # import anthropic
    # client = anthropic.Anthropic()  # Reads ANTHROPIC_API_KEY from environment
    # prompt = EXPLANATION_PROMPT_TEMPLATE.format(**scores)
    # message = client.messages.create(
    #     model="claude-opus-4-5",
    #     max_tokens=1024,
    #     messages=[{"role": "user", "content": prompt}]
    # )
    # return message.content[0].text

    # Phase 2 — OpenAI GPT API (alternative):
    # TODO: Add your OpenAI API key as environment variable OPENAI_API_KEY
    # import openai
    # client = openai.OpenAI()  # Reads OPENAI_API_KEY from environment
    # response = client.chat.completions.create(
    #     model="gpt-4o",
    #     messages=[
    #         {"role": "system", "content": "You are an expert FinTech behavioral analyst."},
    #         {"role": "user", "content": EXPLANATION_PROMPT_TEMPLATE.format(**scores)}
    #     ]
    # )
    # return response.choices[0].message.content

    return None  # Phase 1: stub — xai.py rule engine is active instead


def build_scores_context(df, dis, panic, skill, tax, drawdown_data=None) -> Dict[str, Any]:
    """
    Build the scores context dictionary to pass into generate_llm_explanation().
    Extracts all key metrics into a flat dict matching the prompt template.
    """
    return {
        "total_trades":    len(df),
        "win_rate":        df["Is Profit"].mean() * 100,
        "total_pnl":       df["PnL"].sum(),
        "dis_score":       dis.get("score", 0),
        "dis_grade":       dis.get("grade", "N/A"),
        "panic_rate":      panic.get("panic_pct", 0),
        "skill_pct":       skill.get("skill_pct", 50),
        "luck_pct":        skill.get("luck_pct", 50),
        "max_drawdown":    drawdown_data.get("max_drawdown_pct", 0) if drawdown_data else 0,
        "kelly_adherence": 0,  # TODO: wire from kelly_criterion module
        "avg_hold":        df.get("Hold Days", df.iloc[:, 0] * 0).mean() if "Hold Days" in df.columns else 0,
        "biases":          ", ".join(panic.get("detected_biases", ["None detected"])),
    }
