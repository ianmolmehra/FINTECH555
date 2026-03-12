# =============================================================================
# FINTECH555 — Decision Intelligence Platform
# File: app/ui/report.py
# Purpose: Master report orchestrator. Enriches data, runs all 19 analytics
#          modules, and renders the full tabbed interactive report on the page.
# Academic: Demonstrates complete ML pipeline — data → features → models → XAI
# =============================================================================

import streamlit as st
import pandas as pd
import numpy as np

# ── Feature engineering pipeline — runs once after upload
from preprocessing.cleaner import enrich_dataframe

# ── Analytics modules — each computes a specific behavioral/statistical metric
from analytics.decision_score   import compute_decision_intelligence_score
from analytics.panic_detection  import detect_panic_and_biases
from analytics.loss_attribution import compute_loss_attribution
from analytics.simulations      import patience_gap_simulation
from analytics.trader_dna       import profile_trader_dna
from analytics.skill_vs_luck    import compute_skill_vs_luck
from analytics.tax_advisor      import compute_tax_insights
from analytics.sector_heatmap   import compute_sector_heatmap
from analytics.annual_review    import compute_annual_review
from analytics.drawdown         import compute_drawdown
from analytics.streak_analysis  import compute_streak_analysis
from analytics.time_pattern     import compute_time_patterns
from analytics.capital_efficiency import compute_capital_efficiency
from analytics.kelly_criterion  import compute_kelly_criterion
from analytics.bayesian_winrate import compute_bayesian_winrate
from analytics.efficient_frontier import compute_efficient_frontier
from analytics.trade_tagger     import compute_trade_tags
from analytics.peer_comparison  import compute_peer_comparison

# ── XAI rule engine — multi-condition behavioral explanation generator
from explainability.xai import generate_xai_report

# ── UI components — reusable cards, badges, strips
from ui.components import (
    section_header, kpi_strip, score_badge,
    insight_card, action_card, risk_flag_card, divider
)

# ── Chart builders — all Plotly charts with dark FinTech theme
from ui.charts import (
    chart_cumulative_pnl, chart_dis_breakdown, chart_panic_radar,
    chart_loss_attribution_pie, chart_patience_simulation,
    chart_sector_heatmap, chart_skill_vs_luck, chart_monthly_pnl,
    chart_hold_distribution, chart_dna_scores,
)

# ── New UI components for Modules 11-19
from ui.fingerprint_card   import render_fingerprint_card
from ui.progress_timeline  import render_progress_timeline
from ui.worst_day_view     import render_worst_day_forensic
from ui.report_card        import render_report_card

# ── Export utilities
from utils.export import export_excel_report


def render_report(df_raw: pd.DataFrame):
    """
    Master report entry point. Called by layout.py after successful file upload.

    Pipeline:
      1. Feature engineering (enrich_dataframe)
      2. Run all 19 analytics modules in parallel
      3. Generate XAI rule-engine explanations
      4. Render tabbed UI with all visualizations
      5. Export options

    Args:
        df_raw: Validated, standardized DataFrame from broker_parser + validator.
    """

    # ═══════════════════════════════════════════════════════════════════
    # STEP 1: FEATURE ENGINEERING
    # Runs once; all modules consume this enriched df with 20+ features
    # ═══════════════════════════════════════════════════════════════════
    with st.spinner("🧠 FINTECH555 is analyzing your trades…"):
        # Enrich: adds pnl_pct, hold_days, is_panic, streaks, sector, etc.
        df = enrich_dataframe(df_raw)

        # ── STEP 2: Run all analytics modules
        # Each module accepts the enriched df and returns a structured dict

        dis     = compute_decision_intelligence_score(df)   # Module 1: DIS score
        panic   = detect_panic_and_biases(df)               # Module 2: Behavioral biases
        loss    = compute_loss_attribution(df)              # Module 4: Loss causes
        sim     = patience_gap_simulation(df)               # Module 3: Monte Carlo patience
        dna     = profile_trader_dna(df, panic)             # Module 5: Trader DNA
        skill   = compute_skill_vs_luck(df)                 # Module 6: Skill vs Luck
        sector  = compute_sector_heatmap(df)                # Module 7: Sector heatmap
        tax     = compute_tax_insights(df)                  # Module 8: Tax intelligence
        annual  = compute_annual_review(df)                 # Module 9: YoY review
        draw    = compute_drawdown(df)                      # Module 11: Drawdown
        streak  = compute_streak_analysis(df)               # Module 12: Streak analysis
        time_p  = compute_time_patterns(df)                 # Module 13: Day/time patterns
        cap_eff = compute_capital_efficiency(df)            # Module 14: Capital efficiency
        kelly   = compute_kelly_criterion(df)               # Module 15: Kelly criterion
        bayes   = compute_bayesian_winrate(df)              # Module 16: Bayesian win rate
        frontier= compute_efficient_frontier(df)            # Module 17: Efficient frontier
        tags    = compute_trade_tags(df, dis, panic, kelly) # Module 18: Trade auto-tagger
        peer    = compute_peer_comparison(df, dis, panic, skill, draw)  # Module 19: Peer comparison

        # ── Step 3: XAI rule engine — generates personalized explanations
        # Multi-condition engine: checks 5+ conditions per module, not templates
        xai = generate_xai_report(df, dis, panic, loss, sim, dna, skill, tax, sector)

    # ═══════════════════════════════════════════════════════════════════
    # STEP 4: RENDER UI
    # ═══════════════════════════════════════════════════════════════════

    # ── Platform header bar
    st.markdown(f"""
    <div style="background:linear-gradient(90deg,#0A1A0A,#0D2B0D);border:1px solid #00C85333;
         border-radius:12px;padding:1rem 1.5rem;margin-bottom:1.2rem;display:flex;
         align-items:center;justify-content:space-between;">
        <div>
            <h2 style="margin:0;color:#00C853;">🧠 Decision Intelligence Report</h2>
            <p style="margin:0;color:#81C784;font-size:0.85rem;">
                AI-powered post-trade behavioral analytics · Not investment advice
            </p>
        </div>
        <div style="text-align:right;color:#4CAF50;font-size:0.8rem;">
            {len(df)} trades analyzed · All analytics are local and private
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Executive KPI strip — top-level numbers at a glance
    total_pnl = df["pnl"].sum()
    win_rate  = df["is_profit"].mean() * 100
    kpi_strip([
        ("Total Trades",     len(df)),
        ("Win Rate",         f"{win_rate:.1f}%"),
        ("Total PnL",        f"₹{total_pnl:,.0f}"),
        ("After-Tax PnL",    f"₹{tax.get('after_tax_pnl', total_pnl):,.0f}"),
        ("Tax Paid",         f"₹{tax.get('total_tax_paid', 0):,.0f}"),
        ("Avg Hold (Days)",  f"{df['hold_days'].mean():.1f}"),
    ])

    divider()

    # ── Behavioral Fingerprint Card — visual trader personality summary
    render_fingerprint_card(dis, panic, dna, skill, draw)

    divider()

    # ── Executive XAI Summary
    section_header("📋 Executive Summary")
    st.markdown(xai.get("summary", "Analysis complete."))
    for title, desc in xai.get("risk_flags", []):
        risk_flag_card(title, desc)

    divider()

    # ═══════════════════════════════════════════════════════════════════
    # TABBED REPORT — 12 tabs covering all 19 modules
    # Each tab follows the 5-part structure: KPI strip → chart → breakdown
    # → XAI card → action box
    # ═══════════════════════════════════════════════════════════════════
    tabs = st.tabs([
        "🎯 Decision Score",    # Module 1
        "😨 Panic & Bias",      # Module 2
        "⏳ Patience Gap",      # Module 3
        "📉 Loss & Drawdown",   # Modules 4 + 11
        "🧬 Trader DNA",        # Module 5
        "🎲 Skill vs Luck",     # Module 6
        "🔮 Prediction",        # Module 10
        "🌡️ Sector & Market",   # Modules 7 + 17
        "💰 Tax & Capital",     # Modules 8 + 14 + 15
        "📊 Streaks & Time",    # Modules 12 + 13
        "📅 Annual Review",     # Module 9
        "👥 Peer & Portfolio",  # Modules 16 + 19 + Tags
    ])

    # ──────────────────────────────────────────────────────────────────
    # TAB 0: DECISION INTELLIGENCE SCORE (Module 1)
    # Formula: Weighted sum of 5 sub-components (exit, entry, sizing, patience, recovery)
    # ──────────────────────────────────────────────────────────────────
    with tabs[0]:
        section_header("🎯 Decision Intelligence Score",
                       "Measures decision quality independent of profit outcome.")

        c1, c2, c3, c4, c5 = st.columns(5)
        for col, (label, val) in zip(
            [c1, c2, c3, c4, c5],
            [("DIS Score",    f"{dis.get('score', 0)}/100"),
             ("Grade",        dis.get("grade", "N/A")),
             ("Exit Disc.",   f"{dis.get('exit_discipline', 0):.0f}/25"),
             ("Entry Qual.",  f"{dis.get('entry_quality', 0):.0f}/20"),
             ("Recovery",     f"{dis.get('recovery_score', 0):.0f}/20")]
        ):
            with col:
                st.metric(label, val)

        c1, c2 = st.columns([1, 1])
        with c1:
            try:
                st.plotly_chart(chart_dis_breakdown(dis), use_container_width=True)
            except Exception as e:
                st.info(f"Chart building: {e}")
        with c2:
            # What-If Improvement Slider — educational: shows which lever matters most
            st.markdown("#### 🔧 What-If Improvement Simulator")
            st.caption("Drag to see how improving one dimension changes your total DIS score.")
            exit_boost     = st.slider("Improve Exit Discipline +", 0, 15, 0, key="exit_slider")
            patience_boost = st.slider("Improve Patience Score +", 0, 10, 0, key="pat_slider")
            # Linear improvement: add the boost to respective component scores
            simulated_score = min(100, dis.get("score", 0) + exit_boost + patience_boost)
            delta = simulated_score - dis.get("score", 0)
            st.metric("Simulated DIS Score", f"{simulated_score}/100",
                      delta=f"+{delta:.0f}" if delta > 0 else "0")

        # XAI explanation card
        xai_dis = xai.get("explanations", {}).get("Decision Intelligence Score", {})
        insight_card("🧠 Why Your DIS Score Is What It Is",
                     xai_dis.get("key_insight", "Upload more trades for deeper insight."))
        action_card("HIGH",
                    xai_dis.get("what_to_do", "Focus on exit discipline — it has the highest DIS weight (25 pts)."))

    # ──────────────────────────────────────────────────────────────────
    # TAB 1: BEHAVIORAL BIAS & PANIC DETECTION (Module 2)
    # KMeans clustering (k=3): Disciplined / Reactive / Impulsive profiles
    # ──────────────────────────────────────────────────────────────────
    with tabs[1]:
        section_header("😨 Behavioral Bias & Panic Detection",
                       "KMeans clustering detects 5 behavioral biases across all trades.")

        bias_cols = st.columns(5)
        bias_labels = ["Panic %", "Revenge %", "Loss Aversion", "Overconfidence", "Disposition"]
        bias_keys   = ["panic_pct", "revenge_pct", "loss_aversion_score",
                       "overconfidence_score", "disposition_score"]
        for col, label, key in zip(bias_cols, bias_labels, bias_keys):
            with col:
                val = panic.get(key, 0)
                st.metric(label, f"{val:.1f}{'%' if '%' in label else '/100'}")

        c1, c2 = st.columns([1.2, 0.8])
        with c1:
            try:
                st.plotly_chart(chart_panic_radar(panic), use_container_width=True)
            except Exception as e:
                st.info(f"Radar chart: {e}")
        with c2:
            st.markdown(f"**Behavioral Profile:** `{panic.get('profile', 'Reactive')}`")
            st.markdown(f"**Behavioral Health Score:** {panic.get('behavioral_health_score', 50)}/100")
            bhs = panic.get("monthly_bhs")
            if bhs is not None and len(bhs) > 1:
                st.markdown("**Monthly Behavioral Health Trend:**")
                st.line_chart(bhs.set_index("month")["bhs"])

        xai_panic = xai.get("explanations", {}).get("Panic Detection", {})
        insight_card("😨 Your Behavioral Fingerprint",
                     xai_panic.get("key_insight", "Behavioral analysis complete."))
        action_card("HIGH", xai_panic.get("what_to_do", "Pause after 2 consecutive losses."))

    # ──────────────────────────────────────────────────────────────────
    # TAB 2: PATIENCE GAP SIMULATOR (Module 3)
    # GBM: S(t) = S(0) * exp((mu - sigma²/2)*t + sigma*sqrt(t)*Z)
    # ──────────────────────────────────────────────────────────────────
    with tabs[2]:
        section_header("⏳ Patience Gap Simulator",
                       "Monte Carlo simulation: what if you held losing trades longer?")

        sim_vals = sim.get("scenario_pnl", {})
        sim_cols = st.columns(len(sim_vals) if sim_vals else 4)
        for col, (scenario, pnl) in zip(sim_cols, sim_vals.items()):
            with col:
                delta = pnl - df["pnl"].sum()
                st.metric(scenario, f"₹{pnl:,.0f}", delta=f"₹{delta:+,.0f}")

        try:
            st.plotly_chart(chart_patience_simulation(sim), use_container_width=True)
        except Exception as e:
            st.info(f"Simulation chart: {e}")

        insight_card("⏳ The Cost of Impatience",
                     sim.get("insight", "Patience gap analysis complete."))
        action_card("MEDIUM", "Set a minimum hold rule: never exit a losing trade before day 5.")

    # ──────────────────────────────────────────────────────────────────
    # TAB 3: LOSS ATTRIBUTION + DRAWDOWN (Modules 4 + 11)
    # Random Forest + SHAP: distributes prediction credit across features
    # Max Drawdown: (Peak - Trough) / Peak × 100
    # ──────────────────────────────────────────────────────────────────
    with tabs[3]:
        section_header("📉 Loss Attribution & Drawdown Analysis",
                       "Why you lost money AND how deep the drawdown went.")

        # ── Loss Attribution metrics
        loss_cols = st.columns(4)
        loss_keys = [("Total Losses", f"{loss.get('total_losses', 0)}"),
                     ("Avg Loss",     f"₹{loss.get('avg_loss', 0):,.0f}"),
                     ("Top Cause",    loss.get("top_cause", "N/A")),
                     ("Preventable",  f"{loss.get('preventable_pct', 0):.0f}%")]
        for col, (label, val) in zip(loss_cols, loss_keys):
            with col:
                st.metric(label, val)

        c1, c2 = st.columns(2)
        with c1:
            try:
                st.plotly_chart(chart_loss_attribution_pie(loss), use_container_width=True)
            except Exception as e:
                st.info(f"Loss pie chart: {e}")
        with c2:
            # ── Drawdown metrics (Module 11)
            st.markdown("#### 📉 Drawdown Metrics")
            dd_cols = st.columns(2)
            with dd_cols[0]:
                st.metric("Max Drawdown",  f"{draw.get('max_drawdown_pct', 0):.1f}%")
                st.metric("Calmar Ratio",  f"{draw.get('calmar_ratio', 0):.2f}")
            with dd_cols[1]:
                st.metric("Duration (days)",  f"{draw.get('max_drawdown_duration', 0)}")
                st.metric("Avg Recovery",     f"{draw.get('avg_recovery_days', 0):.0f}d")

            # Drawdown area chart — shows underwater periods visually
            drawdown_series = draw.get("rolling_drawdown")
            if drawdown_series is not None and len(drawdown_series) > 0:
                st.markdown("**Rolling Drawdown:**")
                st.area_chart(drawdown_series)

        xai_loss = xai.get("explanations", {}).get("Loss Attribution", {})
        insight_card("📉 Your Loss Pattern Explained",
                     xai_loss.get("key_insight", "Loss attribution complete."))
        action_card("HIGH", xai_loss.get("what_to_do", "Eliminate panic exits — they are your #1 loss cause."))

    # ──────────────────────────────────────────────────────────────────
    # TAB 4: TRADER DNA PROFILE (Module 5)
    # 6-dimensional scoring matrix → archetype classification
    # ──────────────────────────────────────────────────────────────────
    with tabs[4]:
        section_header("🧬 Trader DNA Profile",
                       "6-dimensional behavioral fingerprint classifies your trading archetype.")

        dna_cols = st.columns(3)
        dna_dims = ["precision", "patience", "consistency",
                    "risk_control", "adaptability", "sector_mastery"]
        for i, dim in enumerate(dna_dims):
            with dna_cols[i % 3]:
                st.metric(dim.replace("_", " ").title(), f"{dna.get(dim, 0):.0f}/100")

        c1, c2 = st.columns([1.2, 0.8])
        with c1:
            try:
                st.plotly_chart(chart_dna_scores(dna), use_container_width=True)
            except Exception as e:
                st.info(f"DNA radar: {e}")
        with c2:
            st.markdown(f"### Your Archetype: **{dna.get('archetype', 'Reactive Trader')}**")
            st.markdown(dna.get("archetype_description", ""))
            st.markdown(f"**Recommended Style:** {dna.get('style_recommendation', 'Swing trading with defined exits.')}")

        insight_card("🧬 Your Trading DNA",
                     dna.get("insight", "DNA profile analysis complete."))
        action_card("MEDIUM", dna.get("action", "Focus on your strongest dimension to maximize edge."))

    # ──────────────────────────────────────────────────────────────────
    # TAB 5: SKILL VS LUCK (Module 6)
    # Monte Carlo z-score + Autocorrelation + Logistic Regression
    # + Sharpe Ratio + Sortino Ratio + KS Test + Bootstrap CI
    # ──────────────────────────────────────────────────────────────────
    with tabs[5]:
        section_header("🎲 Skill vs Luck Decomposition",
                       "3-method decomposition: Monte Carlo + Autocorrelation + Logistic Regression.")

        s_cols = st.columns(5)
        skill_metrics = [
            ("Skill %",      f"{skill.get('skill_pct', 50):.0f}%"),
            ("Sharpe Ratio", f"{skill.get('sharpe', 0):.2f}"),
            ("Sortino",      f"{skill.get('sortino', 0):.2f}"),
            ("KS p-value",   f"{skill.get('ks_pvalue', 1):.3f}"),
            ("Bootstrap CI", f"{skill.get('ci_lower', 0):.0f}–{skill.get('ci_upper', 100):.0f}%"),
        ]
        for col, (label, val) in zip(s_cols, skill_metrics):
            with col:
                st.metric(label, val)

        try:
            st.plotly_chart(chart_skill_vs_luck(skill), use_container_width=True)
        except Exception as e:
            st.info(f"Skill chart: {e}")

        xai_skill = xai.get("explanations", {}).get("Skill vs Luck", {})
        insight_card("🎲 Is Your Edge Real?",
                     xai_skill.get("key_insight", "Skill analysis complete."))
        action_card("HIGH", xai_skill.get("what_to_do", "Track 30 more trades to confirm statistical edge."))

    # ──────────────────────────────────────────────────────────────────
    # TAB 6: PREDICTION ENGINE (Module 10)
    # GBM + Ridge Regression + k-NN Regressor
    # FIX: next_win_prob is already 0–100, do NOT multiply by 100
    # FIX: accuracy is 0.0–0.95, cap display at 95%
    # ──────────────────────────────────────────────────────────────────
    with tabs[6]:
        section_header("🔮 Predictive Analytics Engine",
                       "GBM predicts next-trade win probability from your own behavioral history.")

        try:
            from analytics.prediction_engine import compute_predictions
            pred = compute_predictions(df)
            p_cols = st.columns(4)
            with p_cols[0]:
                # next_win_prob is stored as 0–100 float (e.g. 73.0) — display directly
                st.metric("Next Win Probability", f"{pred.get('next_win_prob', 50):.1f}%")
            with p_cols[1]:
                st.metric("Recommended Hold", f"{pred.get('next_hold_rec', 10):.0f} days")
            with p_cols[2]:
                # accuracy is 0.0–0.95 float — multiply by 100 for %, cap at 95
                st.metric("Model Accuracy", f"{min(pred.get('accuracy', 0) * 100, 95):.0f}%")
            with p_cols[3]:
                st.metric("Data Sufficient", "✅ Yes" if pred.get("sufficient_data") else "⚠️ Need More")

            if pred.get("sufficient_data"):
                st.markdown("**Top Predictive Features (SHAP):**")
                feat_imp = pred.get("feature_imp", {})
                if feat_imp:
                    feat_df = pd.DataFrame(
                        list(feat_imp.items()),
                        columns=["Feature", "Importance"]
                    ).sort_values("Importance", ascending=False)
                    st.bar_chart(feat_df.set_index("Feature"))
            else:
                st.info(f"Need at least 15 trades for ML prediction. You have {len(df)} so far.")

        except Exception as e:
            st.info(f"Prediction engine: {e}")

    # ──────────────────────────────────────────────────────────────────
    # TAB 7: SECTOR HEATMAP + EFFICIENT FRONTIER (Modules 7 + 17)
    # Treemap + Gini + Herfindahl + Markowitz frontier
    # ──────────────────────────────────────────────────────────────────
    with tabs[7]:
        section_header("🌡️ Sector Skill Heatmap & Efficient Frontier",
                       "Where you make money — and the optimal sector allocation.")

        sector_stats = sector.get("sector_stats", pd.DataFrame())
        if not sector_stats.empty:
            s_cols = st.columns(4)
            with s_cols[0]:
                st.metric("Best Sector",       sector.get("best_sector", "N/A"))
            with s_cols[1]:
                st.metric("Worst Sector",      sector.get("worst_sector", "N/A"))
            with s_cols[2]:
                st.metric("Gini Coefficient",  f"{sector.get('gini', 0):.3f}")
            with s_cols[3]:
                st.metric("Herfindahl Index",  f"{sector.get('herfindahl', 0):.3f}")

            try:
                st.plotly_chart(chart_sector_heatmap(sector), use_container_width=True)
            except Exception as e:
                st.info(f"Sector heatmap: {e}")

        # ── Efficient Frontier (Module 17)
        st.markdown("---")
        st.markdown("#### 📊 Markowitz Efficient Frontier")
        frontier_data = frontier.get("frontier_data")
        if frontier_data is not None and not frontier_data.empty:
            f_cols = st.columns(3)
            with f_cols[0]:
                st.metric("Current Volatility",     f"{frontier.get('current_vol', 0):.1f}%")
            with f_cols[1]:
                st.metric("Optimal Volatility",     f"{frontier.get('optimal_vol', 0):.1f}%")
            with f_cols[2]:
                st.metric("Vol Reduction Possible", f"{frontier.get('vol_reduction', 0):.1f}%")
            st.markdown(frontier.get("insight", ""))
        else:
            st.info("Need 3+ sectors with 3+ trades each for Markowitz optimization.")

    # ──────────────────────────────────────────────────────────────────
    # TAB 8: TAX INTELLIGENCE + CAPITAL EFFICIENCY + KELLY (Modules 8, 14, 15)
    # ──────────────────────────────────────────────────────────────────
    with tabs[8]:
        section_header("💰 Tax, Capital Efficiency & Kelly Criterion",
                       "STCG/LTCG classification + optimal position sizing using Kelly formula.")

        # ── Tax Intelligence (Module 8)
        st.markdown("#### 💰 Tax Intelligence")
        t_cols = st.columns(4)
        with t_cols[0]:
            st.metric("Total Tax Paid",         f"₹{tax.get('total_tax_paid', 0):,.0f}")
        with t_cols[1]:
            st.metric("STCG Tax",               f"₹{tax.get('stcg_tax', 0):,.0f}")
        with t_cols[2]:
            st.metric("LTCG Tax",               f"₹{tax.get('ltcg_tax', 0):,.0f}")
        with t_cols[3]:
            st.metric("Tax Optimization Score", f"{tax.get('tax_opt_score', 0):.0f}/100")

        monthly_tax = tax.get("monthly_tax")
        if monthly_tax is not None and not monthly_tax.empty:
            st.markdown("**Monthly Tax Liability:**")
            st.bar_chart(monthly_tax.set_index("month")["tax"] if "month" in monthly_tax.columns
                         else monthly_tax.iloc[:, :2].set_index(monthly_tax.columns[0]))

        st.markdown("---")

        # ── Capital Efficiency (Module 14)
        st.markdown("#### 💹 Capital Efficiency Curve")
        cap_cols = st.columns(3)
        with cap_cols[0]:
            st.metric("Pearson r (Capital vs PnL%)", f"{cap_eff.get('pearson_r', 0):.3f}")
        with cap_cols[1]:
            st.metric("Capital Efficiency Score",    f"{cap_eff.get('efficiency_score', 0):.0f}/100")
        with cap_cols[2]:
            st.metric("Optimal Capital Band",
                      f"₹{cap_eff.get('optimal_min', 0):,.0f}–₹{cap_eff.get('optimal_max', 0):,.0f}")
        st.info(cap_eff.get("insight", "Capital efficiency analysis complete."))

        st.markdown("---")

        # ── Kelly Criterion (Module 15)
        st.markdown("#### 📐 Kelly Criterion — Optimal Position Sizing")
        k_cols = st.columns(4)
        with k_cols[0]:
            st.metric("Full Kelly f*",            f"{kelly.get('full_kelly', 0)*100:.1f}%")
        with k_cols[1]:
            st.metric("Half Kelly (Recommended)", f"{kelly.get('half_kelly', 0)*100:.1f}%")
        with k_cols[2]:
            st.metric("Current Avg Sizing",       f"{kelly.get('current_avg_sizing', 0)*100:.1f}%")
        with k_cols[3]:
            st.metric("Kelly Adherence Score",    f"{kelly.get('adherence_score', 0):.0f}/100")
        st.info(kelly.get("insight", "Kelly criterion analysis complete."))

    # ──────────────────────────────────────────────────────────────────
    # TAB 9: STREAK ANALYSIS + TIME PATTERNS (Modules 12 + 13)
    # Run-Length Encoding + Chi-Squared Test
    # ──────────────────────────────────────────────────────────────────
    with tabs[9]:
        section_header("📊 Streak Analysis & Time Patterns",
                       "Run-length encoding reveals streak behavior; Chi-squared tests day-of-week bias.")

        # ── Streak Analysis
        st.markdown("#### 🔥 Streak Analysis")
        str_cols = st.columns(4)
        with str_cols[0]:
            st.metric("Longest Win Streak",      streak.get("longest_win_streak", 0))
        with str_cols[1]:
            st.metric("Longest Loss Streak",     streak.get("longest_loss_streak", 0))
        with str_cols[2]:
            st.metric("Post-Loss Re-entry Rate", f"{streak.get('post_loss_reentry_rate', 0):.0f}%")
        with str_cols[3]:
            st.metric("Post-Loss Win Rate",      f"{streak.get('post_loss_win_rate', 0):.0f}%")
        st.info(streak.get("insight", "Streak analysis complete."))

        st.markdown("---")

        # ── Time & Day Pattern Analysis (Module 13)
        st.markdown("#### 📅 Day-of-Week Pattern Analysis")
        dow_data = time_p.get("dow_stats", pd.DataFrame())
        if not dow_data.empty:
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**Win Rate by Day of Week:**")
                st.bar_chart(dow_data.set_index("day")["win_rate"] if "day" in dow_data.columns
                             else dow_data.iloc[:, :2].set_index(dow_data.columns[0]))
            with c2:
                st.markdown("**Avg PnL by Day of Week:**")
                st.bar_chart(dow_data.set_index("day")["avg_pnl"] if "day" in dow_data.columns
                             else dow_data.iloc[:, :2].set_index(dow_data.columns[0]))
        t_cols = st.columns(3)
        with t_cols[0]:
            st.metric("Best Trading Day",  time_p.get("best_day", "N/A"))
        with t_cols[1]:
            st.metric("Worst Trading Day", time_p.get("worst_day", "N/A"))
        with t_cols[2]:
            st.metric("Chi² p-value",      f"{time_p.get('chi2_pvalue', 1):.3f}")
        st.info(time_p.get("insight", "Time pattern analysis complete."))

    # ──────────────────────────────────────────────────────────────────
    # TAB 10: ANNUAL REVIEW (Module 9)
    # YoY grouped bar charts + Report Card grades
    # ──────────────────────────────────────────────────────────────────
    with tabs[10]:
        section_header("📅 Annual Review — Year-over-Year Performance",
                       "How has your decision-making quality evolved over time?")

        annual_stats = annual.get("annual_stats", pd.DataFrame())
        if not annual_stats.empty:
            st.dataframe(annual_stats, use_container_width=True)
            grades = annual.get("grades", {})
            if grades:
                st.markdown("**📊 Report Card:**")
                grade_df = pd.DataFrame(grades).T
                st.dataframe(grade_df, use_container_width=True)
        else:
            st.info("Upload multiple years of trade data to see year-over-year comparison.")

        # ── Progress Timeline (new UI component)
        render_progress_timeline(df, panic)

    # ──────────────────────────────────────────────────────────────────
    # TAB 11: BAYESIAN WIN RATE + PEER COMPARISON + TRADE TAGS + WORST DAY
    # (Modules 16 + 19 + 18 + Forensics)
    # ──────────────────────────────────────────────────────────────────
    with tabs[11]:
        section_header("👥 Bayesian Analysis, Peer Comparison & Trade Tags")

        # ── Bayesian Win Rate (Module 16)
        st.markdown("#### 🎲 Bayesian Win Rate — How Confident Are We?")
        b_cols = st.columns(4)
        with b_cols[0]:
            st.metric("Posterior Win Rate",    f"{bayes.get('posterior_mean', 50):.1f}%")
        with b_cols[1]:
            st.metric("95% Credible Interval",
                      f"{bayes.get('ci_lower', 0):.1f}%–{bayes.get('ci_upper', 100):.1f}%")
        with b_cols[2]:
            st.metric("Trades to Stabilize",  f"{bayes.get('trades_to_stability', '?')}")
        with b_cols[3]:
            st.metric("Evidence Strength",    bayes.get("evidence_strength", "Weak"))
        st.info(bayes.get("insight", "Bayesian win rate analysis complete."))

        st.markdown("---")

        # ── Peer Comparison (Module 19)
        st.markdown("#### 👥 Peer Comparison — Where Do You Stand?")
        peer_cols = st.columns(3)
        with peer_cols[0]:
            st.metric("Overall Percentile", f"{peer.get('overall_percentile', 50):.0f}th")
        with peer_cols[1]:
            st.metric("Better Than", f"{peer.get('overall_percentile', 50):.0f}% of retail traders")
        with peer_cols[2]:
            st.metric("Peer Category", peer.get("peer_category", "Average"))
        st.info(peer.get("insight", "Peer comparison analysis complete."))

        st.markdown("---")

        # ── Trade Auto-Tagger (Module 18)
        st.markdown("#### 🏷️ Auto-Tagged Trade History")
        tag_df = tags.get("tagged_df", pd.DataFrame())
        if not tag_df.empty:
            # Display filterable tagged trades table
            tag_filter = st.multiselect("Filter by tag:", tags.get("all_tags", []))
            display_df = tag_df.copy()
            if tag_filter:
                display_df = display_df[display_df["tags"].apply(
                    lambda x: any(t in str(x) for t in tag_filter)
                )]
            st.dataframe(display_df, use_container_width=True, height=300)

        st.markdown("---")

        # ── Worst Day Forensic Breakdown (new UI component)
        render_worst_day_forensic(df)

    # ═══════════════════════════════════════════════════════════════════
    # REPORT CARD — Master Score Summary
    # ═══════════════════════════════════════════════════════════════════
    divider()
    render_report_card(dis, panic, skill, tax, draw, peer)

    # ═══════════════════════════════════════════════════════════════════
    # EXPORT SECTION
    # ═══════════════════════════════════════════════════════════════════
    divider()
    section_header("⬇️ Export Report")
    e_cols = st.columns(2)
    with e_cols[0]:
        try:
            xlsx_bytes = export_excel_report(df, dis, panic, loss, sim, tax)
            st.download_button(
                "📊 Export Excel Report",
                data=xlsx_bytes,
                file_name="FINTECH555_report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )
        except Exception as e:
            st.info(f"Excel export ready after analytics complete.")

    with e_cols[1]:
        summary_text = _build_text_summary(df, dis, panic, skill, tax, xai)
        st.download_button(
            "📝 Export Text Summary",
            data=summary_text,
            file_name="FINTECH555_summary.txt",
            mime="text/plain",
            use_container_width=True,
        )


def _build_text_summary(df, dis, panic, skill, tax, xai) -> str:
    """
    Build plain-text report summary for download.
    Formats all key metrics into a readable text report.
    """
    lines = [
        "=" * 60,
        "FINTECH555 — DECISION INTELLIGENCE PLATFORM",
        "Post-Trade AI Analytics Report",
        "=" * 60,
        "",
        f"Total Trades     : {len(df)}",
        f"Win Rate         : {df['is_profit'].mean()*100:.1f}%",
        f"Total PnL        : Rs. {df['pnl'].sum():,.0f}",
        f"After-Tax PnL    : Rs. {tax.get('after_tax_pnl', df['pnl'].sum()):,.0f}",
        "",
        f"Decision Score   : {dis.get('score', 0)}/100 ({dis.get('grade', 'N/A')})",
        f"Behavioral Health: {panic.get('behavioral_health_score', 0)}/100",
        f"Skill vs Luck    : {skill.get('skill_pct', 50):.0f}% Skill",
        f"Sharpe Ratio     : {skill.get('sharpe', 0):.2f}",
        "",
        "EXECUTIVE SUMMARY:",
        xai.get("summary", "").replace("**", ""),
        "",
        "TOP ACTIONS:",
    ]
    for a in xai.get("top_actions", []):
        lines.append(f"  [{a.get('priority', 'HIGH')}] {a.get('action', '')}")
    lines += [
        "",
        "=" * 60,
        "Generated by FINTECH555 — Decision Intelligence Platform",
        "Not investment advice. For educational purposes only.",
    ]
    return "\n".join(lines)