#!/usr/bin/env python3
"""Unit tests for interview_prep.py."""

import json
import os
import tempfile
import unittest

from interview_prep import (
    PrepConfig,
    STARStoryGenerator,
    TransitionNarrative,
    PitchGenerator,
    OnboardingPlan,
    load_resume,
)


SAMPLE_RESUME = {
    "name": "Jane Developer",
    "experience": [
        {
            "company": "TechCorp",
            "title": "Software Engineer",
            "bullets": [
                "Built a real-time notification system using WebSockets",
                "Led the migration of a monolithic app to microservices",
                "Reduced page load time by 40% through performance optimization",
            ],
        },
        {
            "company": "StartupXYZ",
            "title": "Junior Developer",
            "bullets": [
                "Developed customer-facing React dashboard",
                "Implemented REST API endpoints in Python",
                "Wrote unit tests achieving 80% code coverage",
            ],
        },
    ],
    "skills": ["Python", "JavaScript", "React", "Node.js", "AWS"],
}


class TestPrepConfig(unittest.TestCase):
    def test_default_config(self):
        config = PrepConfig()
        self.assertEqual(config.get("candidate_name"), "Brandy")
        self.assertEqual(config.get("target_role"), "Senior Software Engineer")

    def test_config_override(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({"candidate_name": "Test", "target_role": "CTO"}, f)
            path = f.name
        try:
            config = PrepConfig(path)
            self.assertEqual(config.get("candidate_name"), "Test")
            self.assertEqual(config.get("target_role"), "CTO")
        finally:
            os.unlink(path)


class TestSTARStoryGenerator(unittest.TestCase):
    def setUp(self):
        self.gen = STARStoryGenerator(SAMPLE_RESUME)

    def test_generate_10_stories(self):
        stories = self.gen.generate_stories(10)
        self.assertEqual(len(stories), 10)

    def test_generate_5_stories(self):
        stories = self.gen.generate_stories(5)
        self.assertEqual(len(stories), 5)

    def test_story_contains_star_sections(self):
        stories = self.gen.generate_stories(1)
        story = stories[0]
        self.assertIn("Situation:", story)
        self.assertIn("Task:", story)
        self.assertIn("Action:", story)
        self.assertIn("Result:", story)

    def test_story_contains_skill(self):
        stories = self.gen.generate_stories(1)
        story = stories[0]
        # Should mention at least one skill
        self.assertTrue(any(skill in story for skill in ["Python", "JavaScript", "React"]))


class TestTransitionNarrative(unittest.TestCase):
    def setUp(self):
        config = PrepConfig()
        self.transition = TransitionNarrative(SAMPLE_RESUME, config)

    def test_generate_contains_target_role(self):
        result = self.transition.generate("VP of Engineering")
        self.assertIn("VP of Engineering", result)

    def test_generate_contains_current_role(self):
        result = self.transition.generate("VP of Engineering")
        self.assertIn("Software Engineer", result)


class TestPitchGenerator(unittest.TestCase):
    def setUp(self):
        config = PrepConfig()
        self.pitch = PitchGenerator(SAMPLE_RESUME, config)

    def test_30sec_contains_name(self):
        result = self.pitch.generate_30sec("Acme Corp")
        self.assertIn("Brandy", result)

    def test_30sec_contains_target(self):
        result = self.pitch.generate_30sec("Acme Corp")
        self.assertIn("Acme Corp", result)

    def test_2min_contains_name(self):
        result = self.pitch.generate_2min("Acme Corp")
        self.assertIn("Brandy", result)

    def test_2min_contains_achievements(self):
        result = self.pitch.generate_2min("Acme Corp")
        self.assertIn("WebSockets", result)


class TestOnboardingPlan(unittest.TestCase):
    def test_generate_contains_30_days(self):
        config = PrepConfig()
        plan = OnboardingPlan()
        result = plan.generate(SAMPLE_RESUME, config)
        self.assertIn("30 Days", result)
        self.assertIn("60", result)
        self.assertIn("90", result)


class TestLoadResume(unittest.TestCase):
    def test_load_resume(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(SAMPLE_RESUME, f)
            path = f.name
        try:
            resume = load_resume(path)
            self.assertEqual(resume["name"], "Jane Developer")
            self.assertEqual(len(resume["experience"]), 2)
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()
