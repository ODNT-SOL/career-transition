#!/usr/bin/env python3
"""Unit tests for optimizer.py."""

import json
import os
import tempfile
import unittest

from optimizer import ActivityLogger, DiagnosisEngine, MetricsCalculator, OptimizerConfig


class TestOptimizerConfig(unittest.TestCase):
    def test_default_config(self):
        config = OptimizerConfig()
        self.assertIn("diagnosis_rules", config.config)
        self.assertEqual(config.get("author"), "Brandy")

    def test_config_override(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({"author": "Test", "report_title": "Custom"}, f)
            path = f.name
        try:
            config = OptimizerConfig(path)
            self.assertEqual(config.get("author"), "Test")
            self.assertEqual(config.get("report_title"), "Custom")
        finally:
            os.unlink(path)


class TestActivityLogger(unittest.TestCase):
    def setUp(self):
        self.db_file = tempfile.mktemp(suffix=".jsonl")
        self.logger = ActivityLogger(self.db_file)

    def tearDown(self):
        if os.path.exists(self.db_file):
            os.unlink(self.db_file)

    def test_log_and_load_activity(self):
        self.logger.log_activity("application", "2025-05-12", company="TechCorp", role="SWE", status="submitted")
        activities = self.logger.load_activities()
        self.assertEqual(len(activities), 1)
        self.assertEqual(activities[0]["type"], "application")
        self.assertEqual(activities[0]["company"], "TechCorp")

    def test_log_invalid_type_raises(self):
        with self.assertRaises(ValueError):
            self.logger.log_activity("invalid_type")

    def test_get_activities_since(self):
        self.logger.log_activity("application", "2025-01-01", company="A")
        self.logger.log_activity("application", "2025-06-01", company="B")
        from datetime import date
        result = self.logger.get_activities_since(date(2025, 5, 15))
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["company"], "B")

    def test_get_activities_in_range(self):
        self.logger.log_activity("application", "2025-05-10", company="A")
        self.logger.log_activity("application", "2025-05-15", company="B")
        self.logger.log_activity("application", "2025-05-20", company="C")
        from datetime import date
        result = self.logger.get_activities_in_range(date(2025, 5, 12), date(2025, 5, 18))
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["company"], "B")


class TestMetricsCalculator(unittest.TestCase):
    def test_calculate_empty(self):
        calc = MetricsCalculator()
        m = calc.calculate([])
        self.assertEqual(m["applications_submitted"], 0)
        self.assertEqual(m["response_rate"], 0.0)
        self.assertEqual(m["interview_rate"], 0.0)

    def test_calculate_applications(self):
        calc = MetricsCalculator()
        activities = [
            {"type": "application", "status": "submitted"},
            {"type": "application", "status": "replied"},
            {"type": "application", "status": "submitted"},
        ]
        m = calc.calculate(activities)
        # apps_total = only status=submitted = 2, apps_with_response = status=replied = 1
        self.assertEqual(m["applications_submitted"], 2)
        self.assertEqual(m["applications_with_response"], 1)
        self.assertAlmostEqual(m["response_rate"], 0.5, places=2)  # 1/2

    def test_calculate_interviews(self):
        calc = MetricsCalculator()
        activities = [
            {"type": "application", "status": "submitted"},
            {"type": "application", "status": "submitted"},
            {"type": "interview", "status": "scheduled"},
        ]
        m = calc.calculate(activities)
        self.assertEqual(m["interviews_count"], 1)
        self.assertAlmostEqual(m["interview_rate"], 0.5, places=2)

    def test_calculate_outreach(self):
        calc = MetricsCalculator()
        activities = [
            {"type": "outreach", "status": "sent"},
            {"type": "outreach", "status": "sent"},
            {"type": "outreach", "status": "replied"},
        ]
        m = calc.calculate(activities)
        # outreach_sent counts ALL outreach records = 3, replies = 1
        self.assertEqual(m["outreach_sent"], 3)
        self.assertEqual(m["outreach_replies"], 1)
        self.assertAlmostEqual(m["outreach_reply_rate"], 1 / 3, places=2)


class TestDiagnosisEngine(unittest.TestCase):
    def setUp(self):
        self.config = OptimizerConfig()
        self.engine = DiagnosisEngine(self.config)

    def test_low_response_rate_triggers(self):
        metrics = {"response_rate": 0.05, "interview_rate": 0.1, "outreach_reply_rate": 0.1}
        recs = self.engine.evaluate(metrics)
        self.assertTrue(any("response rate" in r.lower() for r in recs))

    def test_good_rates_triggers_positive(self):
        metrics = {"response_rate": 0.3, "interview_rate": 0.1, "outreach_reply_rate": 0.35}
        recs = self.engine.evaluate(metrics)
        self.assertTrue(any("great" in r.lower() or "maintain" in r.lower() for r in recs))

    def test_no_matching_rules(self):
        metrics = {"response_rate": 0.15, "interview_rate": 0.1, "outreach_reply_rate": 0.1}
        recs = self.engine.evaluate(metrics)
        # response_rate=0.15 is not <0.1, interview_rate=0.1 is not <0.05
        # response_rate=0.15 is not >=0.25, so no rules match
        self.assertEqual(len(recs), 0)


if __name__ == "__main__":
    unittest.main()
