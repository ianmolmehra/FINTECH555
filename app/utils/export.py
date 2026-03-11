# ============================================================
# export.py — PDF and Excel report export utilities
# Generates client-ready downloadable reports
# ============================================================

import io
import pandas as pd
from fpdf import FPDF
import xlsxwriter


def export_pdf_report(df, dis, panic, loss, sim, skill, tax, xai) -> bytes:
    """
    Generates a clean multi-page PDF report using fpdf2.
    Returns bytes suitable for st.download_button.
    """
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # ── Cover header ─────────────────────────────────────────────
    pdf.set_fill_color(10, 15, 10)
    pdf.rect(0, 0, 210, 45, "F")
    pdf.set_text_color(0, 200, 83)
    pdf.set_font("Helvetica", "B", 22)
    pdf.set_y(12)
    pdf.cell(0, 10, "Decision Intelligence Report", align="C", ln=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(138, 158, 138)
    pdf.cell(0, 8, "AI-Powered Post-Trade Behavioral Analytics", align="C", ln=True)
    pdf.ln(10)

    # ── Key Metrics ───────────────────────────────────────────────
    pdf.set_text_color(255, 255, 255)
    pdf.set_fill_color(17, 24, 17)
    _pdf_section(pdf, "Portfolio Summary")
    total_pnl = df["PnL"].sum()
    win_rate  = df["Is Profit"].mean() * 100
    metrics = [
        ("Total Trades",       str(len(df))),
        ("Win Rate",           f"{win_rate:.1f}%"),
        ("Total PnL",          f"Rs {total_pnl:,.0f}"),
        ("After-Tax PnL",      f"Rs {tax['after_tax_pnl']:,.0f}"),
        ("Decision Score",     f"{dis['score']}/100 ({dis['grade']})"),
        ("Skill vs Luck",      f"{skill['skill_pct']}% Skill"),
    ]
    for label, value in metrics:
        pdf.set_text_color(138, 158, 138)
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(75, 7, label + ":", ln=False)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 7, value, ln=True)

    # ── Executive Summary ─────────────────────────────────────────
    _pdf_section(pdf, "Executive Summary")
    pdf.set_text_color(220, 220, 220)
    pdf.set_font("Helvetica", "", 10)
    summary_clean = xai["summary"].replace("**", "").replace("*", "")
    pdf.multi_cell(0, 6, summary_clean)

    # ── Top Action Items ─────────────────────────────────────────
    _pdf_section(pdf, "Top 3 Action Items")
    for action in xai["top_actions"]:
        priority_clean = action["priority"].replace("🔴", "[HIGH]").replace("🟡", "[MED]").replace("🟢", "[STD]")
        pdf.set_text_color(0, 200, 83)
        pdf.set_font("Helvetica", "B", 9)
        pdf.cell(0, 6, priority_clean, ln=True)
        pdf.set_text_color(220, 220, 220)
        pdf.set_font("Helvetica", "", 9)
        pdf.multi_cell(0, 5, action["action"])
        pdf.ln(2)

    # ── XAI Module Explanations ───────────────────────────────────
    pdf.add_page()
    _pdf_section(pdf, "AI Explanations by Module")
    for module, details in xai["explanations"].items():
        pdf.set_text_color(0, 200, 83)
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 7, module, ln=True)
        for key in ["score_context", "key_insight", "what_to_do"]:
            val = details.get(key, "").replace("**", "").replace("*", "")
            if val:
                pdf.set_text_color(138, 158, 138)
                pdf.set_font("Helvetica", "I", 9)
                pdf.cell(0, 5, key.replace("_", " ").title() + ":", ln=True)
                pdf.set_text_color(220, 220, 220)
                pdf.set_font("Helvetica", "", 9)
                pdf.multi_cell(0, 5, val)
        pdf.ln(4)

    # ── Return as bytes ───────────────────────────────────────────
    return bytes(pdf.output())


def export_excel_report(df, dis, panic, loss, sim, tax) -> bytes:
    """
    Generates a multi-sheet Excel workbook with all analytics.
    Returns bytes suitable for st.download_button.
    """
    output = io.BytesIO()

    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        workbook = writer.book

        # ── Formats ──────────────────────────────────────────────
        header_fmt = workbook.add_format({
            "bold": True, "bg_color": "#0D2B0D",
            "font_color": "#00C853", "border": 1, "align": "center"
        })
        green_fmt  = workbook.add_format({"font_color": "#00C853", "bold": True})
        red_fmt    = workbook.add_format({"font_color": "#FF5252", "bold": True})
        money_fmt  = workbook.add_format({"num_format": "₹#,##0.00"})
        pct_fmt    = workbook.add_format({"num_format": "0.00%"})

        # ── Sheet 1: Trade Log ────────────────────────────────────
        display_cols = ["Stock Symbol", "Buy Date", "Sell Date", "Buy Price",
                        "Sell Price", "Quantity", "PnL", "PnL %", "Hold Days",
                        "Trade Result", "Is Panic", "Tax Type", "After Tax PnL"]
        available = [c for c in display_cols if c in df.columns]
        df[available].to_excel(writer, sheet_name="Trade Log", index=False)
        ws = writer.sheets["Trade Log"]
        for col_num, col_name in enumerate(available):
            ws.write(0, col_num, col_name, header_fmt)
            ws.set_column(col_num, col_num, 14)

        # ── Sheet 2: Analytics Summary ────────────────────────────
        summary_data = {
            "Metric": [
                "Total Trades", "Win Rate %", "Total PnL",
                "After-Tax PnL", "Tax Paid",
                "Decision Score", "DIS Grade",
                "Behavioral Health Score",
                "Panic Selling %", "Skill %", "Luck %",
            ],
            "Value": [
                len(df), round(df["Is Profit"].mean() * 100, 1), round(df["PnL"].sum(), 2),
                round(tax["after_tax_pnl"], 2), round(tax["total_tax_paid"], 2),
                dis["score"], dis["grade"],
                panic.get("behavioral_health_score", 0),
                panic.get("panic_selling", {}).get("pct", 0),
                0, 0,  # skill data passed separately
            ]
        }
        pd.DataFrame(summary_data).to_excel(writer, sheet_name="Analytics Summary", index=False)
        ws2 = writer.sheets["Analytics Summary"]
        ws2.write(0, 0, "Metric", header_fmt)
        ws2.write(0, 1, "Value", header_fmt)
        ws2.set_column(0, 0, 28)
        ws2.set_column(1, 1, 18)

        # ── Sheet 3: Loss Attribution ──────────────────────────────
        if loss["categories"]:
            loss_rows = []
            for cause, data in loss["categories"].items():
                loss_rows.append({
                    "Root Cause":   cause,
                    "Trade Count":  data["trade_count"],
                    "Total Loss":   data["total_loss"],
                    "Avg Loss":     data["avg_loss"],
                    "Share %":      data["share_pct"],
                })
            pd.DataFrame(loss_rows).to_excel(writer, sheet_name="Loss Attribution", index=False)
            ws3 = writer.sheets["Loss Attribution"]
            for col_num, col_name in enumerate(["Root Cause", "Trade Count", "Total Loss", "Avg Loss", "Share %"]):
                ws3.write(0, col_num, col_name, header_fmt)
                ws3.set_column(col_num, col_num, 16)

        # ── Sheet 4: Tax Intelligence ──────────────────────────────
        if not tax["monthly_tax"].empty:
            tax["monthly_tax"].to_excel(writer, sheet_name="Tax Monthly", index=False)

    return output.getvalue()


def _pdf_section(pdf: "FPDF", title: str):
    """Helper to render a section header in the PDF."""
    pdf.ln(5)
    pdf.set_fill_color(0, 60, 20)
    pdf.set_text_color(0, 200, 83)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 9, "  " + title, fill=True, ln=True)
    pdf.ln(2)
