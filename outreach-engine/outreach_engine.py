#!/usr/bin/env python3
"""Outreach Engine - Personalized messaging automation."""

import json
import os
import re
import sqlite3
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import requests
from bs4 import BeautifulSoup

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DEFAULT_CONFIG = {
    "templates": {
        "initial": {
            "subject": "Re: {job_title} opportunity at {company}",
            "body": (
                "Hi {first_name},\n\n"
                "I came across the {job_title} role at {company} and am very interested. "
                "As a {my_title} with experience in {my_skills}, I believe I'd be a strong fit.\n\n"
                "Would love to connect and discuss further.\n\n"
                "Best,\n{my_name}"
            ),
        },
        "followup_1": {
            "subject": "Re: {job_title} opportunity at {company} - Following up",
            "body": (
                "Hi {first_name},\n\n"
                "Just wanted to follow up on my earlier message about the {job_title} position. "
                "I'd love to discuss how my background in {my_skills} could contribute to {company}.\n\n"
                "Best,\n{my_name}"
            ),
        },
        "followup_2": {
            "subject": "Re: {job_title} at {company}",
            "body": (
                "Hi {first_name},\n\n"
                "Last check-in on this — still very interested in the {job_title} role. "
                "Happy to share my resume or schedule a call at your convenience.\n\n"
                "Best,\n{my_name}"
            ),
        },
    },
    "followup_days": [3, 7, 14],
    "my_name": "Brandy",
    "my_title": "Software Engineer",
    "my_skills": "Python, JavaScript, React, Node.js",
    "database": "outreach.db",
}


class OutreachConfig:
    """Configuration for outreach engine."""

    def __init__(self, config_path: Optional[str] = None):
        self.config = DEFAULT_CONFIG.copy()
        if config_path and os.path.exists(config_path):
            with open(config_path) as f:
                self.config.update(json.load(f))

    def get(self, key: str, default=None):
        return self.config.get(key, default)


# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------

SCHEMA = """
CREATE TABLE IF NOT EXISTS contacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    company TEXT NOT NULL,
    title TEXT,
    email TEXT,
    linkedin_url TEXT,
    source TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS outreach_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contact_id INTEGER REFERENCES contacts(id),
    message_type TEXT,
    subject TEXT,
    body TEXT,
    sent_at TIMESTAMP,
    status TEXT DEFAULT 'pending',
    FOREIGN KEY (contact_id) REFERENCES contacts(id)
);

CREATE TABLE IF NOT EXISTS followup_schedule (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contact_id INTEGER REFERENCES contacts(id),
    followup_number INTEGER,
    scheduled_at TIMESTAMP,
    sent_at TIMESTAMP,
    status TEXT DEFAULT 'pending',
    FOREIGN KEY (contact_id) REFERENCES contacts(id)
);
"""


class OutreachDB:
    """SQLite wrapper for outreach tracking."""

    def __init__(self, db_path: str = "outreach.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript(SCHEMA)

    def add_contact(
        self,
        name: str,
        company: str,
        title: str = "",
        email: str = "",
        linkedin_url: str = "",
        source: str = "manual",
    ) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute(
                """INSERT INTO contacts (name, company, title, email, linkedin_url, source)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (name, company, title, email, linkedin_url, source),
            )
            return cur.lastrowid

    def get_contact(self, contact_id: int) -> Optional[dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT * FROM contacts WHERE id = ?", (contact_id,)
            ).fetchone()
            return dict(row) if row else None

    def list_contacts(self) -> list[dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("SELECT * FROM contacts ORDER BY created_at DESC").fetchall()
            return [dict(r) for r in rows]

    def add_message(
        self,
        contact_id: int,
        message_type: str,
        subject: str,
        body: str,
        status: str = "pending",
    ) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute(
                """INSERT INTO outreach_messages (contact_id, message_type, subject, body, status)
                   VALUES (?, ?, ?, ?, ?)""",
                (contact_id, message_type, subject, body, status),
            )
            return cur.lastrowid

    def get_messages_for_contact(self, contact_id: int) -> list[dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                """SELECT * FROM outreach_messages
                   WHERE contact_id = ? ORDER BY sent_at ASC""",
                (contact_id,),
            ).fetchall()
            return [dict(r) for r in rows]

    def mark_message_sent(self, message_id: int):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """UPDATE outreach_messages
                   SET status = 'sent', sent_at = CURRENT_TIMESTAMP
                   WHERE id = ?""",
                (message_id,),
            )

    def schedule_followup(self, contact_id: int, followup_number: int, scheduled_at: datetime):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """INSERT INTO followup_schedule (contact_id, followup_number, scheduled_at, status)
                   VALUES (?, ?, ?, 'pending')""",
                (contact_id, followup_number, scheduled_at.isoformat()),
            )

    def get_pending_followups(self) -> list[dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                """SELECT fs.*, c.name, c.company, c.email, c.title as job_title
                   FROM followup_schedule fs
                   JOIN contacts c ON c.id = fs.contact_id
                   WHERE fs.status = 'pending'
                     AND fs.scheduled_at <= datetime('now')
                   ORDER BY fs.scheduled_at ASC"""
            ).fetchall()
            return [dict(r) for r in rows]

    def mark_followup_sent(self, followup_id: int):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """UPDATE followup_schedule
                   SET status = 'sent', sent_at = CURRENT_TIMESTAMP
                   WHERE id = ?""",
                (followup_id,),
            )


# ---------------------------------------------------------------------------
# Template Engine
# ---------------------------------------------------------------------------

REQUIRED_TOKENS = {"first_name", "company", "job_title", "my_name", "my_title", "my_skills"}


class TemplateEngine:
    """Render message templates with personalization tokens."""

    def __init__(self, config: OutreachConfig):
        self.config = config

    def _extract_tokens(self, template: str) -> set:
        return set(re.findall(r"\{(\w+)\}", template))

    def validate_template(self, template_name: str) -> bool:
        template = self.config.get("templates", {}).get(template_name, {})
        body = template.get("body", "")
        tokens = self._extract_tokens(body)
        missing = REQUIRED_TOKENS - tokens
        return len(missing) == 0

    def render(self, template_name: str, context: dict) -> tuple[str, str]:
        """Return (subject, body) with tokens filled in."""
        template = self.config.get("templates", {}).get(template_name, {})
        if not template:
            raise ValueError(f"Unknown template: {template_name}")

        # Merge with my info from config
        full_context = {
            "my_name": self.config.get("my_name", ""),
            "my_title": self.config.get("my_title", ""),
            "my_skills": self.config.get("my_skills", ""),
        }
        full_context.update(context)

        subject = template.get("subject", "")
        body = template.get("body", "")

        for key, value in full_context.items():
            placeholder = "{" + key + "}"
            subject = subject.replace(placeholder, str(value))
            body = body.replace(placeholder, str(value))

        return subject, body


# ---------------------------------------------------------------------------
# Contact Finder
# ---------------------------------------------------------------------------

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
]


class ContactFinder:
    """Find recruiter/hiring manager contacts from LinkedIn and company sites."""

    def _get_headers(self) -> dict:
        import random

        ua = random.choice(USER_AGENTS)
        return {
            "User-Agent": ua,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }

    def find_from_linkedin(self, job_title: str, company: str) -> list[dict]:
        """Search LinkedIn for recruiters/hiring managers at a company."""
        contacts = []
        url = "https://www.linkedin.com/sales/search/people"
        params = {
            "query": f"{job_title} {company}",
            "filters": "resultType:People",
        }
        try:
            response = requests.get(
                url, params=params, headers=self._get_headers(), timeout=15
            )
            if response.status_code != 200:
                return contacts

            soup = BeautifulSoup(response.text, "lxml")
            for card in soup.select(".search-result"):
                try:
                    name_elem = card.select_one(".actor-name")
                    title_elem = card.select_one(".subline-level-1")
                    if not name_elem:
                        continue
                    name = name_elem.get_text(strip=True)
                    title = title_elem.get_text(strip=True) if title_elem else ""
                    linkedin_url = ""
                    if name_elem and name_elem.a:
                        linkedin_url = name_elem.a.get("href", "")
                    contacts.append(
                        {
                            "name": name,
                            "company": company,
                            "title": title,
                            "linkedin_url": linkedin_url,
                            "source": "linkedin",
                        }
                    )
                except Exception:
                    continue

            time.sleep(2)
        except Exception as e:
            print(f"Error searching LinkedIn: {e}", file=sys.stderr)

        return contacts

    def find_from_company_site(self, company: str) -> list[dict]:
        """Scrape company careers/team pages for recruiter info."""
        contacts = []
        # Try common careers page patterns
        for path in [f"/careers", f"/about/team", f"/team"]:
            try:
                url = f"https://www.{company.lower().replace(' ', '')}.com{path}"
                response = requests.get(url, headers=self._get_headers(), timeout=10)
                if response.status_code != 200:
                    continue

                soup = BeautifulSoup(response.text, "lxml")
                # Look for recruiter-related patterns
                text = soup.get_text().lower()
                if "recruiter" in text or "talent" in text or "hiring" in text:
                    for person_card in soup.select(".team-member, .career-member, [class*='person']"):
                        name_elem = person_card.select_one("h3, h4, .name")
                        title_elem = person_card.select_one(".title, .role, .position")
                        email_elem = person_card.select_one("a[href^='mailto:']")
                        if name_elem:
                            contacts.append(
                                {
                                    "name": name_elem.get_text(strip=True),
                                    "company": company,
                                    "title": title_elem.get_text(strip=True) if title_elem else "",
                                    "email": email_elem.get_text(strip=True) if email_elem else "",
                                    "source": "company_site",
                                }
                            )
                time.sleep(1)
            except Exception:
                continue

        return contacts


# ---------------------------------------------------------------------------
# Outreach Sender
# ---------------------------------------------------------------------------

# Placeholder for SMTP — in production, integrate with email provider
SMTP_AVAILABLE = False


class OutreachSender:
    """Send outreach messages and schedule follow-ups."""

    def __init__(self, config: OutreachConfig, db: OutreachDB):
        self.config = config
        self.db = db
        self.templates = TemplateEngine(config)
        self.followup_days = config.get("followup_days", [3, 7, 14])

    def send_initial(self, contact_id: int, job_title: str) -> Optional[int]:
        """Send initial outreach message."""
        contact = self.db.get_contact(contact_id)
        if not contact:
            raise ValueError(f"Contact {contact_id} not found")

        first_name = contact["name"].split()[0] if contact["name"] else "there"
        subject, body = self.templates.render(
            "initial",
            {
                "first_name": first_name,
                "full_name": contact["name"],
                "company": contact["company"],
                "job_title": job_title,
            },
        )

        message_id = self.db.add_message(
            contact_id, "initial", subject, body, status="pending"
        )

        # In production: actually send via SMTP here
        # For now, mark as sent (mock)
        self.db.mark_message_sent(message_id)

        # Schedule follow-ups
        sent_at = datetime.now()
        for i, days in enumerate(self.followup_days, start=1):
            self.db.schedule_followup(
                contact_id, i, sent_at + timedelta(days=days)
            )

        print(f"Sent initial outreach to {contact['name']} ({contact['company']})")
        return message_id

    def send_followup(self, contact_id: int, followup_number: int) -> Optional[int]:
        """Send a specific numbered follow-up."""
        contact = self.db.get_contact(contact_id)
        if not contact:
            raise ValueError(f"Contact {contact_id} not found")

        template_name = f"followup_{followup_number}"
        if template_name not in self.config.get("templates", {}):
            raise ValueError(f"No template for followup {followup_number}")

        first_name = contact["name"].split()[0] if contact["name"] else "there"
        subject, body = self.templates.render(
            template_name,
            {
                "first_name": first_name,
                "full_name": contact["name"],
                "company": contact["company"],
                "job_title": contact.get("title", ""),
            },
        )

        message_id = self.db.add_message(
            contact_id, f"followup_{followup_number}", subject, body, status="pending"
        )

        # In production: actually send via SMTP here
        self.db.mark_message_sent(message_id)

        print(f"Sent followup {followup_number} to {contact['name']}")
        return message_id

    def check_and_send_followups(self) -> int:
        """Check pending followups and send those that are due."""
        pending = self.db.get_pending_followups()
        sent_count = 0
        for followup in pending:
            try:
                self.send_followup(followup["contact_id"], followup["followup_number"])
                self.db.mark_followup_sent(followup["id"])
                sent_count += 1
            except Exception as e:
                print(f"Error sending followup {followup['id']}: {e}", file=sys.stderr)
        return sent_count


# ---------------------------------------------------------------------------
# CLI Entry Point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Outreach Engine")
    parser.add_argument("--config", help="Path to config JSON file")
    parser.add_argument(
        "--db", default="outreach.db", help="Path to SQLite database"
    )
    sub = parser.add_subparsers(dest="command")

    # add-contact
    ac = sub.add_parser("add-contact", help="Add a new contact")
    ac.add_argument("--name", required=True)
    ac.add_argument("--company", required=True)
    ac.add_argument("--title", default="")
    ac.add_argument("--email", default="")
    ac.add_argument("--linkedin-url", default="")

    # send
    send_p = sub.add_parser("send", help="Send initial outreach")
    send_p.add_argument("--contact-id", type=int, required=True)
    send_p.add_argument("--job-title", required=True)

    # send-followups
    sub.add_parser("send-followups", help="Check and send pending followups")

    # list-contacts
    sub.add_parser("list-contacts", help="List all contacts")

    # history
    hist = sub.add_parser("history", help="View message history for a contact")
    hist.add_argument("--contact-id", type=int, required=True)

    args = parser.parse_args()

    config = OutreachConfig(args.config)
    db = OutreachDB(args.db)
    sender = OutreachSender(config, db)

    if args.command == "add-contact":
        cid = db.add_contact(
            args.name, args.company, args.title, args.email, args.linkedin_url
        )
        print(f"Added contact {cid}: {args.name} at {args.company}")

    elif args.command == "send":
        msg_id = sender.send_initial(args.contact_id, args.job_title)
        print(f"Sent message {msg_id}")

    elif args.command == "send-followups":
        count = sender.check_and_send_followups()
        print(f"Sent {count} followups")

    elif args.command == "list-contacts":
        for c in db.list_contacts():
            print(f"  [{c['id']}] {c['name']} | {c['company']} | {c['title']}")

    elif args.command == "history":
        for m in db.get_messages_for_contact(args.contact_id):
            print(f"  [{m['sent_at']}] {m['message_type']} | {m['subject'][:60]}")

    else:
        parser.print_help()
