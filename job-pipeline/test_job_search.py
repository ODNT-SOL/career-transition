#!/usr/bin/env python3
"""Tests for job_search.py"""

import unittest
from job_search import JobSearchConfig, sanitize_csv_field, Job


class TestSanitizeCsvField(unittest.TestCase):
    def test_prefix_dangerous_chars(self):
        self.assertEqual(sanitize_csv_field("=cmd|foo"), "'=cmd|foo")
        self.assertEqual(sanitize_csv_field("@foo"), "'@foo")
        self.assertEqual(sanitize_csv_field("+bar"), "'+bar")
        self.assertEqual(sanitize_csv_field("-baz"), "'-baz")
    
    def test_normal_text_unchanged(self):
        self.assertEqual(sanitize_csv_field("Normal text"), "Normal text")
        self.assertEqual(sanitize_csv_field(""), "")
    
    def test_empty_string(self):
        self.assertEqual(sanitize_csv_field(""), "")


class TestJobSearchConfig(unittest.TestCase):
    def test_default_config(self):
        config = JobSearchConfig()
        self.assertIn("software engineer", config.get("search_terms"))
        self.assertIn("insurance", config.get("exclude_keywords"))
        self.assertIn("remote", config.get("locations"))
    
    def test_config_override(self):
        import json
        import tempfile
        import os
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"search_terms": ["python developer"]}, f)
            temp_path = f.name
        try:
            config = JobSearchConfig(temp_path)
            self.assertEqual(config.get("search_terms"), ["python developer"])
        finally:
            os.unlink(temp_path)


class TestJob(unittest.TestCase):
    def test_job_dataclass(self):
        job = Job(
            title="Software Engineer",
            company="Test Corp",
            location="Remote",
            url="https://example.com",
            source="Indeed",
            date_posted="2 days ago"
        )
        self.assertEqual(job.title, "Software Engineer")
        self.assertEqual(job.company, "Test Corp")


if __name__ == "__main__":
    unittest.main()
