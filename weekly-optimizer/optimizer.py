#!/usr/bin/env python3
"""Weekly Optimization Engine - Metrics tracking and optimization recommendations."""

import datetime
import json
import os
import statistics
import sys
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DEFAULT_CONFIG = {
    "report_title": "Weekly Job Search Report",
    "author": "Brandy",
    "report_output": "weekly-report.pdf",
    "activities_file": "activities.jsonl",
    "thresholds": {
        "low_response_rate": 0.1,
        "good_response_rate": 0.25,
        "low_interview_rate": 0.05,
        "good_interview_rate": 0.15,
    },
    "diagnosis_rules": [
        {
            "condition": "response_rate < 0.1",
            "recommendation": (
                "Your response rate is low. Consider: (1) Customizing cover letters more, "
                "(2) Targeting roles closer to your experience, (3) Expanding to adjacent job titles."
            ),
        },
        {
            "condition": "interview_rate < 0.05",
            "recommendation": (
                "Interview rate is very low. Consider: (1) Resume optimization, "
                "(2) Applying to more roles, (3) Reviewing job descriptions for keyword alignment."
            ),
        },
        {
            "condition": "response_rate >= 0.25 and outreach_reply_rate >= 0.3",
            "recommendation": (
                "Great response rates! Maintain current strategy and focus on interview preparation."
            ),
        },
    ],
}


class OptimizerConfig:
    """Configuration for weekly optimizer."""

    def __init__(self, config_path: Optional[str] = None):
        self.config = DEFAULT_CONFIG.copy()
        if config_path and os.path.exists(config_path):
            with open(config_path) as f:
                self.config.update(json.load(f))

    def get(self, key: str, default=None):
        return self.config.get(key, default)


# ---------------------------------------------------------------------------
# Activity Logging
# ---------------------------------------------------------------------------

ACTIVITY_TYPES = {"application", "outreach", "interview", "offer"}


class ActivityLogger:
    """Log and retrieve job search activities."""

    def __init__(self, activities_file: str = "activities.jsonl"):
        self.activities_file = activities_file

    def log_activity(self, activity_type: str, activity_date: Optional[str] = None, **kwargs):
        """Append an activity to the log file."""
        if activity_type not in ACTIVITY_TYPES:
            raise ValueError(f"Invalid activity type: {activity_type}")

        if activity_date is None:
            activity_date = date.today().isoformat()

        record = {"date": activity_date, "type": activity_type, **kwargs}
        with open(self.activities_file, "a") as f:
            f.write(json.dumps(record) + "\n")

    def load_activities(self) -> list[dict]:
        """Load all activities from file."""
        if not os.path.exists(self.activities_file):
            return []

        activities = []
        with open(self.activities_file) as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        activities.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
        return activities

    def get_activities_since(self, since_date: date) -> list[dict]:
        """Get activities from a given date onward."""
        activities = self.load_activities()
        cutoff = since_date.isoformat()
        return [a for a in activities if a.get("date", "") >= cutoff]

    def get_activities_in_range(self, start: date, end: date) -> list[dict]:
        """Get activities within a date range (inclusive)."""
        activities = self.load_activities()
        start_str = start.isoformat()
        end_str = end.isoformat()
        return [
            a
            for a in activities
            if start_str <= a.get("date", "") <= end_str
        ]


# ---------------------------------------------------------------------------
# Metrics Calculator
# ---------------------------------------------------------------------------


class MetricsCalculator:
    """Calculate job search metrics from activities."""

    def calculate(self, activities: list[dict]) -> dict:
        """Calculate all metrics from a list of activities."""
        applications = [a for a in activities if a.get("type") == "application"]
        outreach_records = [a for a in activities if a.get("type") == "outreach"]
        interviews = [a for a in activities if a.get("type") == "interview"]
        offers = [a for a in activities if a.get("type") == "offer"]

        apps_submitted = len([a for a in applications if a.get("status") == "submitted"])
        apps_with_response = len(
            [a for a in applications if a.get("status") in ("replied", "interview", "offer")]
        )
        apps_total = apps_submitted

        outreach_sent = len(outreach_records)
        outreach_replies = len([o for o in outreach_records if o.get("status") == "replied"])

        interviews_count = len([i for i in interviews if i.get("status") in ("scheduled", "completed")])
        interviews_completed = len([i for i in interviews if i.get("status") == "completed"])

        offers_received = len([o for o in offers if o.get("status") == "received"])

        response_rate = apps_with_response / apps_total if apps_total > 0 else 0.0
        interview_rate = interviews_count / apps_total if apps_total > 0 else 0.0
        outreach_reply_rate = outreach_replies / outreach_sent if outreach_sent > 0 else 0.0

        return {
            "applications_submitted": apps_submitted,
            "applications_total": apps_total,
            "applications_with_response": apps_with_response,
            "response_rate": round(response_rate, 3),
            "outreach_sent": outreach_sent,
            "outreach_replies": outreach_replies,
            "outreach_reply_rate": round(outreach_reply_rate, 3),
            "interviews_count": interviews_count,
            "interviews_completed": interviews_completed,
            "interview_rate": round(interview_rate, 3),
            "offers_received": offers_received,
        }

    def weekly_summary(self, logger: ActivityLogger) -> dict:
        """Get metrics for the current week (Monday to today)."""
        today = date.today()
        start_of_week = today - timedelta(days=today.weekday())
        activities = logger.get_activities_in_range(start_of_week, today)
        return self.calculate(activities)

    def last_week_summary(self, logger: ActivityLogger) -> dict:
        """Get metrics for last week."""
        today = date.today()
        start_of_week = today - timedelta(days=today.weekday())
        last_week_end = start_of_week - timedelta(days=1)
        last_week_start = last_week_end - timedelta(days=6)
        activities = logger.get_activities_in_range(last_week_start, last_week_end)
        return self.calculate(activities)

    def cumulative_summary(self, logger: ActivityLogger) -> dict:
        """Get cumulative metrics over all time."""
        activities = logger.load_activities()
        return self.calculate(activities)


# ---------------------------------------------------------------------------
# Diagnosis Engine
# ---------------------------------------------------------------------------


class DiagnosisEngine:
    """Evaluate diagnosis rules and produce recommendations."""

    def __init__(self, config: OptimizerConfig):
        self.config = config

    def evaluate(self, metrics: dict) -> list[str]:
        """Return list of recommendations based on metrics."""
        recommendations = []
        rules = self.config.get("diagnosis_rules", [])

        for rule in rules:
            condition = rule.get("condition", "")
            try:
                # Safely evaluate condition against metrics
                if eval(condition, {}, metrics):
                    recommendations.append(rule.get("recommendation", ""))
            except Exception:
                continue

        return recommendations


# ---------------------------------------------------------------------------
# Report Generator (PDF)
# ---------------------------------------------------------------------------

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        Paragraph,
        SimpleDocTemplate,
        Spacer,
        Table,
        TableStyle,
    )

    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False


class ReportGenerator:
    """Generate weekly PDF report."""

    def __init__(self, config: OptimizerConfig, logger: ActivityLogger, calculator: MetricsCalculator):
        self.config = config
        self.logger = logger
        self.calculator = calculator
        self.diagnosis = DiagnosisEngine(config)

    def generate_pdf(self, output_path: str) -> bool:
        """Generate PDF report. Returns True on success."""
        if not PDF_AVAILABLE:
            print("Error: reportlab not installed. PDF generation unavailable.", file=sys.stderr)
            return False

        today = date.today()
        start_of_week = today - timedelta(days=today.weekday())

        weekly = self.calculator.weekly_summary(self.logger)
        last_week = self.calculator.last_week_summary(self.logger)
        cumulative = self.calculator.cumulative_summary(self.logger)
        recommendations = self.diagnosis.evaluate(weekly)

        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=0.75 * inch,
            leftMargin=0.75 * inch,
            topMargin=0.75 * inch,
            bottomMargin=0.75 * inch,
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "CustomTitle",
            parent=styles["Heading1"],
            fontSize=18,
            spaceAfter=20,
        )
        heading_style = ParagraphStyle(
            "CustomHeading",
            parent=styles["Heading2"],
            fontSize=13,
            spaceBefore=15,
            spaceAfter=8,
        )
        body_style = ParagraphStyle("CustomBody", parent=styles["Normal"], fontSize=10)

        story = []

        # Header
        title = self.config.get("report_title", "Weekly Report")
        story.append(Paragraph(f"{title}", title_style))
        story.append(
            Paragraph(
                f"Week of {start_of_week.strftime('%B %d')} - {today.strftime('%B %d, %Y')} | "
                f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}",
                body_style,
            )
        )
        story.append(Spacer(1, 0.3 * inch))

        # Metrics table: this week vs last week
        story.append(Paragraph("Weekly Metrics Comparison", heading_style))

        table_data = [
            ["Metric", "This Week", "Last Week", "Change"],
            [
                "Applications",
                str(weekly["applications_submitted"]),
                str(last_week["applications_submitted"]),
                self._change_str(weekly["applications_submitted"], last_week["applications_submitted"]),
            ],
            [
                "Response Rate",
                f"{weekly['response_rate']:.1%}",
                f"{last_week['response_rate']:.1%}",
                self._change_str(weekly["response_rate"], last_week["response_rate"]),
            ],
            [
                "Outreach Sent",
                str(weekly["outreach_sent"]),
                str(last_week["outreach_sent"]),
                self._change_str(weekly["outreach_sent"], last_week["outreach_sent"]),
            ],
            [
                "Outreach Reply Rate",
                f"{weekly['outreach_reply_rate']:.1%}",
                f"{last_week['outreach_reply_rate']:.1%}",
                self._change_str(weekly["outreach_reply_rate"], last_week["outreach_reply_rate"]),
            ],
            [
                "Interviews",
                str(weekly["interviews_count"]),
                str(last_week["interviews_count"]),
                self._change_str(weekly["interviews_count"], last_week["interviews_count"]),
            ],
            [
                "Offers",
                str(weekly["offers_received"]),
                str(last_week["offers_received"]),
                self._change_str(weekly["offers_received"], last_week["offers_received"]),
            ],
        ]

        table = Table(table_data, colWidths=[2 * inch, 1.2 * inch, 1.2 * inch, 1.2 * inch])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4472C4")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ("ALIGN", (1, 0), (-1, -1), "CENTER"),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#DCE6F1"), colors.white]),
                ]
            )
        )
        story.append(table)
        story.append(Spacer(1, 0.25 * inch))

        # Cumulative stats
        story.append(Paragraph("Cumulative Totals", heading_style))
        cum_data = [
            ["Total Applications", "Total Responses", "Total Interviews", "Offers"],
            [
                str(cumulative["applications_total"]),
                str(cumulative["applications_with_response"]),
                str(cumulative["interviews_count"]),
                str(cumulative["offers_received"]),
            ],
        ]
        cum_table = Table(cum_data, colWidths=[1.5 * inch] * 4)
        cum_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4472C4")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#DCE6F1")),
                ]
            )
        )
        story.append(cum_table)
        story.append(Spacer(1, 0.25 * inch))

        # Recommendations
        if recommendations:
            story.append(Paragraph("Diagnosis & Recommendations", heading_style))
            for rec in recommendations:
                story.append(Paragraph(f"• {rec}", body_style))
                story.append(Spacer(1, 0.1 * inch))

        # Recent activity log
        story.append(Paragraph("Recent Activity", heading_style))
        recent = self.logger.get_activities_since(start_of_week)
        if recent:
            act_data = [["Date", "Type", "Company/Contact", "Status"]]
            for a in recent[-15:]:  # last 15
                act_data.append(
                    [
                        a.get("date", ""),
                        a.get("type", ""),
                        a.get("company", a.get("contact_id", "")),
                        a.get("status", ""),
                    ]
                )
            act_table = Table(act_data, colWidths=[1 * inch, 1 * inch, 2.2 * inch, 1.3 * inch])
            act_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4472C4")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, -1), 8),
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                        (
                            "ROWBACKGROUNDS",
                            (0, 1),
                            (-1, -1),
                            [colors.HexColor("#DCE6F1"), colors.white],
                        ),
                    ]
                )
            )
            story.append(act_table)
        else:
            story.append(Paragraph("No activity logged this week.", body_style))

        doc.build(story)
        return True

    def _change_str(self, current: float, previous: float) -> str:
        """Format change as +N or -N string."""
        diff = current - previous
        if diff > 0:
            return f"+{diff:.0f}"
        elif diff < 0:
            return f"{diff:.0f}"
        else:
            return "0"


# ---------------------------------------------------------------------------
# CLI Entry Point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Weekly Optimization Engine")
    parser.add_argument("--config", help="Path to config JSON file")
    parser.add_argument("--activities", default="activities.jsonl", help="Path to activities log")
    sub = parser.add_subparsers(dest="command")

    # log
    log_p = sub.add_parser("log", help="Log a job search activity")
    log_p.add_argument("--type", required=True, choices=["application", "outreach", "interview", "offer"])
    log_p.add_argument("--date", default=None, help="Date (YYYY-MM-DD), defaults to today")
    log_p.add_argument("--company", default="")
    log_p.add_argument("--role", default="")
    log_p.add_argument("--status", default="submitted")
    log_p.add_argument("--contact-id", type=int, default=None)

    # report
    report_p = sub.add_parser("report", help="Generate weekly PDF report")
    report_p.add_argument("--output", default=None, help="Output PDF path")

    # metrics
    sub.add_parser("metrics", help="Show current week metrics")

    args = parser.parse_args()

    config = OptimizerConfig(args.config)
    logger = ActivityLogger(config.get("activities_file", args.activities))
    calculator = MetricsCalculator()

    if args.command == "log":
        kwargs = {}
        if args.company:
            kwargs["company"] = args.company
        if args.role:
            kwargs["role"] = args.role
        if args.status:
            kwargs["status"] = args.status
        if args.contact_id is not None:
            kwargs["contact_id"] = args.contact_id
        logger.log_activity(args.type, args.date, **kwargs)
        print(f"Logged {args.type} activity.")

    elif args.command == "report":
        output = args.output or config.get("report_output", "weekly-report.pdf")
        generator = ReportGenerator(config, logger, calculator)
        success = generator.generate_pdf(output)
        if success:
            print(f"Report generated: {output}")
        else:
            print("Failed to generate PDF report.", file=sys.stderr)
            sys.exit(1)

    elif args.command == "metrics":
        weekly = calculator.weekly_summary(logger)
        cumulative = calculator.cumulative_summary(logger)
        print("=== This Week ===")
        for k, v in weekly.items():
            print(f"  {k}: {v}")
        print("\n=== Cumulative ===")
        for k, v in cumulative.items():
            print(f"  {k}: {v}")

    else:
        parser.print_help()
