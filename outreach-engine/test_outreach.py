#!/usr/bin/env python3
"""Unit tests for outreach_engine.py."""

import json
import os
import tempfile
import unittest

from outreach_engine import OutreachConfig, OutreachDB, TemplateEngine


class TestOutreachConfig(unittest.TestCase):
    def test_default_config_loads(self):
        config = OutreachConfig()
        self.assertIn("Brandy", config.get("my_name"))
        self.assertIn("templates", config.config)
        self.assertIn("initial", config.get("templates"))

    def test_config_override(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({"my_name": "Test User", "my_title": "QA Engineer"}, f)
            path = f.name
        try:
            config = OutreachConfig(path)
            self.assertEqual(config.get("my_name"), "Test User")
            self.assertEqual(config.get("my_title"), "QA Engineer")
        finally:
            os.unlink(path)


class TestTemplateEngine(unittest.TestCase):
    def setUp(self):
        self.config = OutreachConfig()

    def test_render_initial_template(self):
        engine = TemplateEngine(self.config)
        subject, body = engine.render(
            "initial",
            {
                "first_name": "Jane",
                "full_name": "Jane Doe",
                "company": "TechCorp",
                "job_title": "Software Engineer",
            },
        )
        self.assertIn("TechCorp", subject)
        self.assertIn("Jane", body)
        self.assertIn("TechCorp", body)
        self.assertIn("Software Engineer", body)
        self.assertIn("Brandy", body)  # my_name from config

    def test_render_followup_template(self):
        engine = TemplateEngine(self.config)
        subject, body = engine.render(
            "followup_1",
            {
                "first_name": "John",
                "company": "StartupXYZ",
                "job_title": "Backend Developer",
            },
        )
        self.assertIn("StartupXYZ", subject)
        self.assertIn("John", body)

    def test_unknown_template_raises(self):
        engine = TemplateEngine(self.config)
        with self.assertRaises(ValueError):
            engine.render("nonexistent", {})


class TestOutreachDB(unittest.TestCase):
    def setUp(self):
        self.db_file = tempfile.mktemp(suffix=".db")
        self.db = OutreachDB(self.db_file)

    def tearDown(self):
        os.unlink(self.db_file)

    def test_add_and_get_contact(self):
        cid = self.db.add_contact(
            name="Jane Recruiter",
            company="TechCorp",
            title="Senior Recruiter",
            email="jane@techcorp.com",
            source="manual",
        )
        self.assertIsInstance(cid, int)
        contact = self.db.get_contact(cid)
        self.assertEqual(contact["name"], "Jane Recruiter")
        self.assertEqual(contact["company"], "TechCorp")
        self.assertEqual(contact["email"], "jane@techcorp.com")

    def test_list_contacts(self):
        self.db.add_contact("Alice", "CompanyA", source="manual")
        self.db.add_contact("Bob", "CompanyB", source="manual")
        contacts = self.db.list_contacts()
        self.assertEqual(len(contacts), 2)

    def test_add_and_get_message(self):
        cid = self.db.add_contact("Test Contact", "Test Co", source="manual")
        mid = self.db.add_message(cid, "initial", "Test Subject", "Test Body")
        messages = self.db.get_messages_for_contact(cid)
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0]["subject"], "Test Subject")
        self.assertEqual(messages[0]["message_type"], "initial")

    def test_mark_message_sent(self):
        cid = self.db.add_contact("Test", "Co", source="manual")
        mid = self.db.add_message(cid, "initial", "S", "B")
        self.db.mark_message_sent(mid)
        messages = self.db.get_messages_for_contact(cid)
        self.assertEqual(messages[0]["status"], "sent")

    def test_schedule_and_get_followups(self):
        from datetime import datetime, timedelta

        cid = self.db.add_contact("Followup Test", "Co", source="manual")
        future = datetime.now() + timedelta(days=5)
        self.db.schedule_followup(cid, 1, future)
        pending = self.db.get_pending_followups()
        # future date shouldn't appear in pending (scheduled_at > now)
        self.assertEqual(len(pending), 0)

    def test_contact_not_found(self):
        result = self.db.get_contact(9999)
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
