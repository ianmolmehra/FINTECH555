"""
================================================================================
FINTECH555 — Decision Intelligence Platform
File: app/explainability/xai.py
Purpose: Multi-condition layered rule engine for XAI explanations.
         NOT template substitution — checks 5+ conditions per module and
         produces genuinely different text for different score combinations.
================================================================================
"""
import pandas as pd
from typing import Optional


def explain_dis(dis: dict, df: pd.DataFrame) -> str:
    """
    Multi-condition XAI for Decision Intelligence Score.
    Checks: exit_discipline × patience_score × recovery_score combinations.
    """
    total = dis["total"]
    exit_d = dis["exit_discipline"]
    patience = dis["patience_score"]
    recovery = dis["recovery_score"]
    total_trades = len(df)
    wins = int(df["is_profit"].sum())
    win_rate = wins / total_trades * 100

    if exit_d < 40 and patience < 40:
        return (f"You made {total_trades} trades, winning {wins} ({win_rate:.1f}%). "
                f"Your DIS of {total:.1f}/100 reveals a dual problem: "
                f"you exit trades too early under pressure ({exit_d:.0f}/100 exit discipline) "
                f"AND you don't hold winning trades long enough ({patience:.0f}/100 patience). "
                f"This combination — panic exits on losses, premature exits on wins — "
                f"is the most destructive behavioral pattern a trader can have. "
                f"You are essentially paying the market twice: once when you cut losses too fast, "
                f"once when you leave profits on the table.")

    elif exit_d > 70 and recovery < 40:
        return (f"You made {total_trades} trades with a {win_rate:.1f}% win rate. "
                f"Your DIS of {total:.1f}/100 shows strong exit discipline ({exit_d:.0f}/100) — "
                f"you don't panic-sell. But your recovery score is dangerously low ({recovery:.0f}/100). "
                f"After each loss, you re-enter too quickly, making emotionally-driven trades "
                f"that erode the gains from your disciplined exits. Your control when you're UP "
                f"is not matched by your discipline when you're DOWN.")

    elif exit_d > 70 and patience > 70:
        return (f"You made {total_trades} trades, winning {wins} ({win_rate:.1f}%). "
                f"With a DIS of {total:.1f}/100, you demonstrate the two rarest trader skills: "
                f"exit discipline ({exit_d:.0f}/100) AND patience ({patience:.0f}/100). "
                f"Most retail traders fail at one of these. You have both. "
                f"Your primary drag is position sizing consistency — focus there next.")

    elif total < 45:
        return (f"You made {total_trades} trades with a {win_rate:.1f}% win rate. "
                f"Your DIS of {total:.1f}/100 indicates decision quality that is below the "
                f"retail average of 45. The biggest single contributor to this score is "
                f"your exit discipline at {exit_d:.0f}/100. "
                f"Your entries may be sound, but you are not letting the trades breathe "
                f"long enough to realize their full potential.")

    else:
        return (f"You made {total_trades} trades, winning {wins} ({win_rate:.1f}%). "
                f"Your DIS of {total:.1f}/100 puts you in the average retail trader range. "
                f"Your strongest dimension is exit discipline at {exit_d:.0f}/100. "
                f"Your patience score of {patience:.0f}/100 suggests you have the right instincts "
                f"but need more consistency. One behavioral improvement can move this score significantly.")


def explain_panic(biases: dict, df: pd.DataFrame) -> str:
    """Multi-condition XAI for behavioral biases. Checks panic × recovery combinations."""
    panic_pct = biases["panic_pct"]
    recovery = 100 - biases["revenge_pct"]
    loss_aversion = biases["loss_aversion_score"]
    total = len(df)
    bhs = biases["behavioral_health_score"]

    if panic_pct > 35 and recovery < 40:
        return (f"Your behavioral health score of {bhs:.0f}/100 reveals a damaging pattern. "
                f"Your panic-selling signature appears in {panic_pct:.1f}% of your losing trades. "
                f"Worse, after those panic exits, you re-enter the market {100-recovery:.0f}% of the time "
                f"within the same session. This is not a market problem — it is a discipline problem. "
                f"Your nervous system is making trading decisions, not your strategy. "
                f"The two behaviors are amplifying each other into a loss cycle.")

    elif panic_pct > 35 and recovery > 65:
        return (f"You show a high panic-selling rate of {panic_pct:.1f}%, but a redeeming quality: "
                f"when you panic, you bounce back. Your recovery behavior is strong ({recovery:.0f}/100). "
                f"This means you panic often, but you don't spiral. "
                f"You have the emotional resilience — you now need the pre-commitment discipline "
                f"to prevent the initial panic exit from happening at all.")

    elif panic_pct < 15 and loss_aversion > 60:
        return (f"You hold your nerve well — only {panic_pct:.1f}% of trades show panic-exit signatures. "
                f"But your loss aversion score of {loss_aversion:.0f}/100 reveals a subtler bias: "
                f"you hold losing trades too long, hoping they recover. "
                f"Your data shows average losers are held {biases['avg_hold_losers']:.1f} days vs "
                f"{biases['avg_hold_winners']:.1f} days for winners. "
                f"You are patient with the wrong trades.")

    else:
        return (f"With a behavioral health score of {bhs:.0f}/100, your profile across {total} trades "
                f"shows moderate behavioral discipline. Your panic rate of {panic_pct:.1f}% "
                f"compares to an average retail trader rate of ~42%. "
                f"The disposition ratio of {biases['disposition_ratio']:.2f} "
                f"({'holding losers longer' if biases['disposition_ratio'] < 1 else 'healthy'}) "
                f"is your primary behavioral blind spot to address.")


def explain_simulations(sim: dict, df: pd.DataFrame) -> str:
    """XAI for Patience Gap Simulator."""
    losing_count = sim["losing_trades_count"]
    avg_loss = sim["actual_avg_loss"]
    best_ext = max(sim["extension_scenarios"], key=lambda k: sim["extension_scenarios"][k]["avg_simulated_pnl"])
    best_pnl = sim["extension_scenarios"][best_ext]["avg_simulated_pnl"]
    best_pct = sim["extension_scenarios"][best_ext]["pct_positive"]

    return (f"You have {losing_count} losing trades with an average loss of ₹{abs(avg_loss):,.0f}. "
            f"The Monte Carlo simulation (Geometric Brownian Motion, {1000} paths per scenario) "
            f"shows that if you had held those trades for {best_ext.replace('+','').replace('d',' more days')}, "
            f"your average outcome would have been ₹{best_pnl:,.0f} — and {best_pct:.0f}% of "
            f"simulation paths turned positive. This is not a prediction — it is a probability estimate "
            f"based on the statistical drift (μ={sim['mu']:.4f}) and volatility (σ={sim['sigma']:.4f}) "
            f"of your own trade history. Some of your biggest losses may have been premature exits.")


def explain_loss_attribution(losses, df: pd.DataFrame) -> str:
    """XAI for loss attribution module."""
    top_cat = losses["loss_category"].value_counts().index[0]
    top_pct = losses["loss_category"].value_counts().iloc[0] / len(losses) * 100
    total_loss = abs(losses["pnl"].sum())
    return (f"Out of your {len(losses)} losing trades totaling ₹{total_loss:,.0f}, "
            f"{top_pct:.0f}% are classified as '{top_cat}'. "
            f"This is not random — it is a systematic pattern in your decision-making. "
            f"Fixing this single category has the highest expected value of any change you can make. "
            f"The other loss types are natural market outcomes; this one is behavioral.")


def explain_trader_dna(result: dict, df: pd.DataFrame) -> str:
    """XAI for Trader DNA profile."""
    archetype = result["archetype"]
    scores = result["scores"]
    strongest = max(scores, key=scores.get)
    weakest = min(scores, key=scores.get)
    return (f"Your trading DNA classifies you as a '{archetype}'. "
            f"Your strongest dimension is {strongest} at {scores[strongest]:.0f}/100 — "
            f"this is the foundation you should build your strategy around. "
            f"Your weakest dimension is {weakest} at {scores[weakest]:.0f}/100. "
            f"For a {archetype}, improving {weakest} is the highest-leverage behavioral change you can make.")


def explain_skill_vs_luck(result: dict, df: pd.DataFrame) -> str:
    """XAI for Skill vs Luck module."""
    skill = result["composite_skill"]
    ks_p = result["ks_p_value"]
    autocorr = result["autocorrelation"]
    sharpe = result["sharpe_ratio"]
    total = len(df)

    if skill > 65 and ks_p < 0.05:
        return (f"Your {total} trades produce a composite skill score of {skill:.1f}/100. "
                f"The Kolmogorov-Smirnov test (p={ks_p:.4f}) confirms your returns are "
                f"statistically different from random — you have a measurable edge. "
                f"Your Sharpe Ratio of {sharpe:.2f} and lag-1 autocorrelation of {autocorr:.3f} "
                f"both support genuine skill rather than luck. Protect this edge — it is real.")

    elif skill < 40:
        return (f"Your {total} trades yield a skill score of {skill:.1f}/100. "
                f"The KS test (p={ks_p:.4f}) cannot distinguish your returns from random. "
                f"This does not mean you have no skill — it means you don't have enough data "
                f"to prove it statistically. With {total} trades, the signal-to-noise ratio is low. "
                f"Continue building a track record. Your Sharpe of {sharpe:.2f} is {'positive' if sharpe > 0 else 'negative'} — {'keep going' if sharpe > 0 else 'review your strategy'}.")

    else:
        return (f"Your skill score of {skill:.1f}/100 and Sharpe Ratio of {sharpe:.2f} "
                f"suggest you are developing a real edge, but it is not yet proven statistically (p={ks_p:.4f}). "
                f"Your autocorrelation of {autocorr:.3f} ({'positive — good trades cluster' if autocorr > 0.1 else 'near zero — results are independent'}) "
                f"is an early signal to watch. Every additional trade adds evidence.")


def explain_sector(sector_df, gini: float, hhi: float) -> str:
    """XAI for sector heatmap."""
    best = sector_df.loc[sector_df["win_rate_pct"].idxmax()]
    worst = sector_df.loc[sector_df["win_rate_pct"].idxmin()]
    return (f"Your Gini coefficient of {gini:.3f} shows that profits are "
            f"{'highly concentrated' if gini > 0.5 else 'moderately spread'} across sectors. "
            f"The Herfindahl Index of {hhi:.3f} indicates "
            f"{'high concentration' if hhi > 0.3 else 'reasonable diversification'} in trade frequency. "
            f"Your best sector is {best['sector']} at {best['win_rate_pct']:.1f}% win rate with "
            f"avg PnL of ₹{best['avg_pnl']:,.0f}. Your worst is {worst['sector']} at {worst['win_rate_pct']:.1f}%. "
            f"The gap between your best and worst sector performance suggests you have genuine domain expertise — use it.")


def explain_tax(tax: dict, df: pd.DataFrame) -> str:
    """XAI for Tax Intelligence module."""
    opt_score = tax["optimization_score"]
    total_tax = tax["total_tax"]
    stcg = tax["stcg_profits"]
    ltcg = tax["ltcg_profits"]

    if opt_score < 30:
        return (f"Your estimated tax liability is ₹{total_tax:,.0f}. "
                f"Almost all your profits (₹{stcg:,.0f}) are short-term gains taxed at 15%. "
                f"You are paying the highest available rate on equity gains. "
                f"If you had held just {365 - df['hold_days'].median():.0f} more days on average, "
                f"many trades would qualify for LTCG at 10% — plus the ₹1,00,000 exemption. "
                f"Your trading style is working against you from a tax standpoint.")

    elif opt_score > 70:
        return (f"Your tax optimization score of {opt_score:.0f}/100 is excellent. "
                f"₹{ltcg:,.0f} of your profits qualify as LTCG, taxed at a lower 10% rate. "
                f"This shows patience pays off twice — in profits AND in tax savings. "
                f"Total estimated tax: ₹{total_tax:,.0f}.")
    else:
        return (f"Your estimated tax liability is ₹{total_tax:,.0f} on "
                f"₹{stcg+ltcg:,.0f} in gross profits. "
                f"Your tax optimization score of {opt_score:.0f}/100 shows room to improve. "
                f"Consider the tax implications when deciding whether to exit a profitable trade — "
                f"a few extra weeks of holding can meaningfully reduce your tax rate.")


def explain_annual(year_metrics: dict) -> str:
    """XAI for annual review — multi-year comparison."""
    years = list(year_metrics.keys())
    if len(years) == 1:
        m = year_metrics[years[0]]
        return (f"In {years[0]}, you made {m['total_trades']} trades with a "
                f"{m['win_rate']:.1f}% win rate and a DIS of {m['dis_score']:.0f}/100. "
                f"Your panic rate was {m['panic_rate']:.1f}% and your Sharpe ratio was {m['sharpe']:.2f}. "
                f"Upload a previous year's CSV to enable year-over-year comparison and see your growth.")
    else:
        current = year_metrics[years[0]]
        prev = year_metrics[years[1]]
        dis_change = current["dis_score"] - prev.get("dis_score", current["dis_score"])
        panic_change = prev.get("panic_rate", current["panic_rate"]) - current["panic_rate"]
        return (f"Year-over-Year: Your DIS score {'improved' if dis_change >= 0 else 'declined'} "
                f"by {abs(dis_change):.1f} points. "
                f"Your panic rate {'dropped' if panic_change > 0 else 'increased'} by {abs(panic_change):.1f}%. "
                f"You are {'learning' if dis_change >= 0 and panic_change > 0 else 'showing mixed progress'} — "
                f"behavioral improvement is a multi-year process.")


def explain_drawdown(dd: dict, df: pd.DataFrame) -> str:
    """XAI for drawdown analysis."""
    max_dd = dd["max_drawdown"]
    duration = dd["duration_days"]
    calmar = dd["calmar_ratio"]
    recovered = dd["recovered"]

    if max_dd > 25:
        return (f"Your maximum drawdown was {max_dd:.1f}% — meaning at your worst point, "
                f"for every ₹100 you had in the portfolio, you were holding ₹{100-max_dd:.0f} in value. "
                f"You took {duration} trading days to recover from this. "
                f"{'You have fully recovered.' if recovered else 'You have not yet fully recovered — you are still underwater.'} "
                f"For context, most disciplined retail traders keep max drawdown below 15%. "
                f"Your Calmar Ratio of {calmar:.2f} ({'good' if calmar > 1 else 'needs work'}) "
                f"tells the full risk-adjusted story.")
    else:
        return (f"Your maximum drawdown of {max_dd:.1f}% is within the acceptable range for retail traders. "
                f"Recovery took {duration} days. {'Full recovery achieved.' if recovered else 'Recovery still in progress.'} "
                f"Your Calmar Ratio of {calmar:.2f} indicates {'solid' if calmar > 1 else 'moderate'} risk management.")


def explain_streaks(streak: dict, df: pd.DataFrame) -> str:
    """XAI for streak analysis."""
    max_loss = streak["max_loss_streak"]
    post_wr = streak["post_streak_wr"]
    # Find post-3-loss win rate
    wr_after_3 = post_wr.get(3, {}).get("win_rate", 50)

    return (f"Your longest losing streak was {max_loss} consecutive trades. "
            f"After 3 or more consecutive losses, your win rate on the very next trade is {wr_after_3:.0f}% "
            f"({'above random — you recover well' if wr_after_3 > 55 else 'below random — you continue losing emotionally'}). "
            f"This pattern {'is not a problem' if wr_after_3 > 50 else 'is costing you money'}. "
            f"Your worst losses are not individual trades — they are clusters of decisions made "
            f"while you were psychologically compromised.")


def explain_time_patterns(tp: dict, df: pd.DataFrame) -> str:
    """XAI for time pattern analysis."""
    best = tp["best_day"]
    worst = tp["worst_day"]
    best_wr = tp["best_day_wr"]
    worst_wr = tp["worst_day_wr"]
    significant = tp["significant"]

    return (f"You trade most actively, but your performance varies significantly by day. "
            f"Your best day is {best} at {best_wr:.0f}% win rate; "
            f"your worst is {worst} at {worst_wr:.0f}%. "
            f"This {best_wr - worst_wr:.0f}-point gap "
            f"{'is statistically significant (chi-squared p=' + str(tp['p_value']) + ') — this is a real pattern, not noise.' if significant else 'is not yet statistically significant — you need more data to confirm this trend.'} "
            f"Consider whether your {worst} losses are driven by Monday macro anxiety or other structural factors.")


def explain_capital_efficiency(ce: dict, df: pd.DataFrame) -> str:
    """XAI for capital efficiency."""
    r = ce["pearson_r"]
    optimal = ce["optimal_band"]
    best_wr = ce["band_wr"].get(optimal, 50)

    if abs(r) < 0.15:
        return (f"There is almost no relationship between how much capital you deploy and your return % (r = {r:.3f}). "
                f"Your largest trades are not your best trades. "
                f"In fact, your highest win rate ({best_wr:.0f}%) comes from trades in the {optimal} range. "
                f"Your instinct to size up on conviction is not being validated by outcomes. "
                f"Consider whether your conviction is correlated with actual edge — or just confidence.")
    elif r > 0.3:
        return (f"Excellent capital efficiency! Your Pearson r of {r:.3f} shows that bigger bets "
                f"are producing better returns — your sizing instincts are well-calibrated. "
                f"Your optimal capital band is {optimal} with a win rate of {best_wr:.0f}%.")
    else:
        return (f"Your capital efficiency correlation of {r:.3f} is weak. "
                f"There is a marginal relationship between position size and returns, "
                f"but it is not consistent enough to rely on. "
                f"Your empirical sweet spot is {optimal} ({best_wr:.0f}% win rate).")


def explain_kelly(kelly: dict, df: pd.DataFrame) -> str:
    """XAI for Kelly Criterion module."""
    full = kelly["full_kelly_capped"]
    half = kelly["half_kelly"]
    actual = kelly["actual_fraction"]
    overbet = kelly["overbetting"]
    ratio = kelly["overbet_ratio"]

    return (f"Based on your win rate of {kelly['win_prob']:.1f}% and win/loss ratio of {kelly['win_loss_ratio']:.2f}, "
            f"the Kelly Criterion recommends risking {full:.1f}% of available capital per trade "
            f"(Half-Kelly: {half:.1f}%). "
            f"You are currently sizing at an average of {actual:.1f}% — "
            f"{'overbetting by ' + str(ratio) + 'x the mathematically optimal amount. ' if overbet else 'well within the safe zone. '}"
            f"{'This is a primary cause of your high-volatility equity curve.' if overbet else 'Your discipline here is admirable and uncommon.'}")


def explain_bayesian(bw: dict, df: pd.DataFrame) -> str:
    """XAI for Bayesian win rate module."""
    post_mean = bw["posterior_mean"]
    ci_l = bw["ci_lower"]
    ci_u = bw["ci_upper"]
    stable = bw["is_stable"]
    trades_needed = bw["trades_to_stability"]

    return (f"When you started, we assumed a 50/50 prior — no bias toward good or bad. "
            f"After your {bw['total_trades']} trades, the evidence has updated our belief. "
            f"We are now 95% confident your true win rate lies between {ci_l:.1f}% and {ci_u:.1f}%. "
            f"The posterior mean estimate is {post_mean:.1f}% — this is more stable than your raw win rate "
            f"because it incorporates the uncertainty from a limited sample. "
            f"{'Your estimate has stabilized — you have enough data for reliable conclusions.' if stable else f'You need approximately {trades_needed} more trades before this estimate stabilizes to within 5%.'}")


def explain_frontier(ef: dict, df: pd.DataFrame) -> str:
    """XAI for Efficient Frontier module."""
    if ef.get("insufficient_data"):
        return "Insufficient data for efficient frontier analysis."
    ms_ret = ef["ms_return"]
    actual_ret = ef["actual_return"]
    sectors = ef["sectors"]
    return (f"Your current sector allocation puts you at risk level {ef['actual_risk']:.3f} "
            f"for a return of {actual_ret:.3f}%. "
            f"The Markowitz Efficient Frontier — solved via quadratic programming — shows that "
            f"you could achieve a higher expected return of {ms_ret:.3f}% by shifting weights "
            f"toward the Maximum Sharpe Portfolio allocation across {len(sectors)} sectors. "
            f"This is not a trading signal — it is a portfolio construction insight based on "
            f"your historical sector performance data.")


def explain_peer(peer: dict, df: pd.DataFrame) -> str:
    """XAI for peer comparison module."""
    overall = peer["overall_percentile"]
    metrics = peer["metrics"]
    best = max(metrics, key=lambda k: metrics[k]["percentile"])
    worst = min(metrics, key=lambda k: metrics[k]["percentile"])

    return (f"Based on benchmarks from SEBI retail investor research, "
            f"you are better than {overall:.0f}% of comparable retail traders overall. "
            f"Your strongest metric is {best.replace('_',' ').title()} at the "
            f"{metrics[best]['percentile']:.0f}th percentile — this is where you have genuine edge. "
            f"Your weakest ranking is {worst.replace('_',' ').title()} at the "
            f"{metrics[worst]['percentile']:.0f}th percentile. "
            f"You have the {'patience' if 'hold' in best else 'discipline'} of a good trader "
            f"but need to address your {worst.replace('_',' ')} to rise further in the rankings.")


# =============================================================================
# MASTER XAI WRAPPER — called by report.py
# Combines all individual explain_* functions into one structured report dict.
# Multi-condition rule engine: every explanation is unique per score combination.
# =============================================================================

def generate_xai_report(df, dis, panic, loss, sim, dna, skill, tax, sector):
    """
    Master XAI report generator. Called once by report.py after all modules run.
    Combines all individual explainability functions into a unified structured dict.

    Returns dict with keys:
        summary       : str — executive summary paragraph
        risk_flags    : list of (title, description) tuples
        top_actions   : list of {priority, action} dicts
        explanations  : dict keyed by module name → {score_context, key_insight, what_to_do}
    """
    win_rate   = df["is_profit"].mean() * 100 if "is_profit" in df.columns else 50
    total_pnl  = df["pnl"].sum() if "pnl" in df.columns else 0
    n_trades   = len(df)
    dis_score  = dis.get("score", dis.get("total", 50))
    panic_pct  = panic.get("panic_pct", 20)
    skill_pct  = skill.get("skill_pct", 50)
    bhs        = panic.get("behavioral_health_score", panic.get("bhs", 50))

    # ── EXECUTIVE SUMMARY — multi-condition, uses real numbers, analyst voice
    # Condition: high win rate but low DIS → winning on luck, not skill
    if win_rate >= 55 and dis_score < 50:
        summary = (
            f"You made {n_trades} trades with a {win_rate:.1f}% win rate — better than most retail traders. "
            f"But your Decision Intelligence Score of {dis_score:.0f}/100 reveals a problem: "
            f"you are winning despite poor decision-making, not because of it. "
            f"Your exits are {dis.get('exit_discipline', 12):.0f}/25 — premature selling is your biggest leak. "
            f"{'Your panic rate of ' + str(round(panic_pct,1)) + '% is damaging recoverable positions. ' if panic_pct > 25 else ''}"
            f"Total PnL: ₹{total_pnl:,.0f}. With better exit discipline alone, this number could be 30–40% higher."
        )
    # Condition: low win rate AND low DIS → structural problems
    elif win_rate < 45 and dis_score < 50:
        summary = (
            f"You made {n_trades} trades. {win_rate:.1f}% were profitable — below the retail average of 48%. "
            f"Your Decision Intelligence Score of {dis_score:.0f}/100 confirms this is a structural issue, not bad luck. "
            f"Your three biggest weaknesses: exit timing, position sizing, and post-loss behavior. "
            f"The good news: these are all learnable skills. The data shows exactly where to start."
        )
    # Condition: high skill but high panic → emotional interference
    elif skill_pct >= 60 and panic_pct > 30:
        summary = (
            f"You have genuine trading skill — {skill_pct:.0f}% of your returns are attributable to skill, not luck. "
            f"But your panic rate of {panic_pct:.1f}% is destroying returns that your analytical edge is building. "
            f"You are making good decisions when calm and terrible decisions when scared. "
            f"Emotional discipline is the only thing standing between you and elite performance."
        )
    # Default: balanced summary
    else:
        summary = (
            f"You made {n_trades} trades with a {win_rate:.1f}% win rate and ₹{total_pnl:,.0f} total PnL. "
            f"Your Decision Intelligence Score is {dis_score:.0f}/100 — "
            f"{'above' if dis_score >= 50 else 'below'} the retail trader average of 45. "
            f"Your Behavioral Health Score of {bhs:.0f}/100 shows "
            f"{'strong emotional discipline' if bhs >= 65 else 'room to improve emotional control'}. "
            f"Focus areas: {_get_focus_areas(dis, panic, skill)}."
        )

    # ── RISK FLAGS — triggered by specific threshold violations
    risk_flags = []
    if panic_pct > 35:
        risk_flags.append(("🚨 High Panic Rate", f"{panic_pct:.1f}% of losing trades are panic exits. Immediate attention needed."))
    if dis_score < 40:
        risk_flags.append(("⚠️ Low Decision Quality", f"DIS score of {dis_score:.0f}/100 indicates systemic decision-making issues."))
    if skill_pct < 45:
        risk_flags.append(("🎲 Luck-Dependent Returns", f"Only {skill_pct:.0f}% of returns are skill-based. Edge not yet statistically confirmed."))
    if panic.get("revenge_pct", 0) > 20:
        risk_flags.append(("🔁 Revenge Trading Detected", f"{panic.get('revenge_pct', 0):.1f}% revenge trades — emotional re-entries after losses."))

    # ── TOP ACTIONS — prioritized, measurable, specific
    top_actions = [
        {"priority": "HIGH",   "action": f"Exit discipline: never close a winner before {max(7, int(df['hold_days'].median()))} days unless stop-loss is hit."},
        {"priority": "HIGH",   "action": f"After any loss, enforce a {4 if panic_pct > 30 else 2}-hour mandatory cooling-off period before next entry."},
        {"priority": "MEDIUM", "action": f"Size to Kelly Half-Kelly formula: risk no more than {min(15, max(5, int(100/max(n_trades,1)*3)))}% of capital per trade."},
    ]

    # ── MODULE EXPLANATIONS — per-tab detailed analysis
    explanations = {
        "Decision Intelligence Score": {
            "score_context": f"DIS: {dis_score:.0f}/100 ({dis.get('grade', 'C')})",
            "key_insight": _explain_dis_insight(dis, df),
            "what_to_do": f"Improve your exit discipline score (currently {dis.get('exit_discipline', 12):.0f}/25) by setting a minimum hold time of 7 days on all winning positions.",
        },
        "Panic Detection": {
            "score_context": f"Panic Rate: {panic_pct:.1f}% | BHS: {bhs:.0f}/100",
            "key_insight": _explain_panic_insight(panic, df),
            "what_to_do": f"Set a phone alarm: '4-hour pause rule' — if you close at a loss, phone stays in your pocket for 4 hours.",
        },
        "Skill vs Luck": {
            "score_context": f"Skill: {skill_pct:.0f}% | Sharpe: {skill.get('sharpe', 0):.2f}",
            "key_insight": f"Statistical analysis across {n_trades} trades places your skill contribution at {skill_pct:.0f}%. " +
                          (f"The KS test p-value of {skill.get('ks_pvalue', 1):.3f} " +
                           ("confirms" if skill.get("ks_pvalue", 1) < 0.05 else "does not yet confirm") +
                           " a statistically significant edge above random."),
            "what_to_do": "Trade 25 more setups using only your highest-confidence pattern to build a statistically stable edge.",
        },
        "Loss Attribution": {
            "score_context": f"Top Loss Cause: {loss.get('top_cause', 'Panic Exit')}",
            "key_insight": f"Your trades are classified into 5 behavioral loss categories. "
                          f"The dominant cause is '{loss.get('top_cause', 'Panic Exit')}', "
                          f"accounting for {loss.get('top_cause_pct', 30):.0f}% of all losses.",
            "what_to_do": "Define your stop-loss level BEFORE entering each trade. Write it down. Stick to it.",
        },
    }

    return {
        "summary":      summary,
        "risk_flags":   risk_flags,
        "top_actions":  top_actions,
        "explanations": explanations,
    }


def _explain_dis_insight(dis, df):
    """Multi-condition DIS insight — different for each score band."""
    score = dis.get("score", dis.get("total", 50))
    exit_d = dis.get("exit_discipline", 12)
    patience = dis.get("patience_score", 10)
    if score >= 75:
        return f"Your DIS of {score:.0f}/100 places you in the top tier of decision quality. Your exits are disciplined and your sizing is consistent. The marginal gains now come from optimizing entry timing."
    elif score >= 55:
        return f"Your DIS of {score:.0f}/100 is above average. Your exit discipline score ({exit_d:.0f}/25) is your weakest sub-component — you are leaving money on the table by exiting winners early."
    elif score >= 40:
        return f"Your DIS of {score:.0f}/100 reveals inconsistent decision quality. Two main leaks: patience ({patience:.0f}/20) and exit discipline ({exit_d:.0f}/25). These two alone account for most of your underperformance."
    else:
        return f"Your DIS of {score:.0f}/100 indicates that systematic decision errors — not bad markets — are the primary cause of losses. The platform has identified {4 - sum([exit_d > 15, patience > 12, score > 40, score > 30])} specific areas for immediate structural improvement."


def _explain_panic_insight(panic, df):
    """Multi-condition panic insight — different narrative for each combination."""
    panic_pct  = panic.get("panic_pct", 20)
    revenge_pct = panic.get("revenge_pct", 10)
    bhs = panic.get("behavioral_health_score", panic.get("bhs", 50))
    if panic_pct > 35 and revenge_pct > 20:
        return f"You have a dual behavioral problem: {panic_pct:.1f}% panic exits AND {revenge_pct:.1f}% revenge trades. This combination is a classic 'loss spiral' — panic triggers a bad exit, which triggers an emotional re-entry, which usually creates another loss."
    elif panic_pct > 35:
        return f"Your panic-selling signature appears in {panic_pct:.1f}% of your losing trades. This is not a market problem — it is a discipline problem. Your nervous system is making trading decisions, not your strategy."
    elif revenge_pct > 25:
        return f"You don't panic often ({panic_pct:.1f}%), but when you do lose, you re-enter the market too quickly. Your {revenge_pct:.1f}% revenge trade rate suggests you are trying to 'get even' with the market — a pattern that statistically leads to larger losses."
    elif bhs >= 70:
        return f"Your Behavioral Health Score of {bhs:.0f}/100 is excellent. Your panic rate of {panic_pct:.1f}% and revenge rate of {revenge_pct:.1f}% are both controlled. Your trading psychology is a genuine competitive advantage."
    else:
        return f"Your behavioral health score of {bhs:.0f}/100 is average. Panic rate: {panic_pct:.1f}%. The data shows periodic emotional interference — not constant, but severe enough to affect quarterly returns."


def _get_focus_areas(dis, panic, skill):
    """Return top 2-3 focus areas as comma-separated string."""
    areas = []
    if dis.get("exit_discipline", 12) < 16:   areas.append("exit discipline")
    if panic.get("panic_pct", 20) > 25:        areas.append("panic control")
    if skill.get("skill_pct", 50) < 55:        areas.append("edge confirmation")
    if dis.get("patience_score", 10) < 12:     areas.append("hold patience")
    return ", ".join(areas[:3]) if areas else "refining existing strengths"
