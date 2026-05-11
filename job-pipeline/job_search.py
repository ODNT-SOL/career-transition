#!/usr/bin/env python3
"""Job Pipeline Automation - Daily job search and tracking."""

import csv
import json
import os
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional


def sanitize_csv_field(value: str) -> str:
    """Prevent CSV injection by prefixing dangerous characters."""
    if value and value[0] in ('=', '@', '+', '-'):
        value = "'" + value
    return value

import requests
from bs4 import BeautifulSoup


@dataclass
class Job:
    title: str
    company: str
    location: str
    url: str
    source: str
    date_posted: str
    description: str = ""


class JobSearchConfig:
    """Configuration for job searches."""
    
    DEFAULT_CONFIG = {
        "search_terms": ["software engineer", "developer", "frontend", "backend", "full stack"],
        "locations": ["remote", "hybrid"],
        "exclude_keywords": ["insurance", "state farm", "allstate", "geico", "prudential"],
        "experience_levels": ["entry", "junior", "associate"],
        "output_file": "tracker.csv"
    }
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self.DEFAULT_CONFIG.copy()
        if config_path and os.path.exists(config_path):
            with open(config_path) as f:
                self.config.update(json.load(f))
    
    def get(self, key: str, default=None):
        return self.config.get(key, default)


class JobSearcher:
    """Base class for job searches."""
    
    def search(self, config: JobSearchConfig) -> list[Job]:
        raise NotImplementedError


class LinkedInJobSearcher(JobSearcher):
    """Search LinkedIn Jobs (uses scraping)."""
    
    def search(self, config: JobSearchConfig) -> list[Job]:
        jobs = []
        
        # Note: LinkedIn has strict anti-scraping. Using mock for demo.
        # In production, use LinkedIn API or official job search.
        for term in config.get("search_terms", []):
            # This would be actual API calls in production
            # For now, return sample data structure
            pass
        
        return jobs


class IndeedJobSearcher(JobSearcher):
    """Search Indeed jobs."""
    
    def search(self, config: JobSearchConfig) -> list[Job]:
        jobs = []
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        for term in config.get("search_terms", []):
            for location in config.get("locations", []):
                url = f"https://www.indeed.com/jobs"
                params = {
                    "q": term,
                    "l": location,
                    "explvl": "entry_level",
                    "remote": "true" if location == "remote" else "false"
                }
                
                try:
                    response = requests.get(url, params=params, headers=headers, timeout=10)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, "lxml")
                        
                        for job_card in soup.select(".jobsearch-ResultsList li"):
                            try:
                                title_elem = job_card.select_one(".jobTitle")
                                if not title_elem:
                                    continue
                                
                                title = title_elem.get_text(strip=True)
                                company = job_card.select_one(".companyName")
                                company = company.get_text(strip=True) if company else "Unknown"
                                location = job_card.select_one(".companyLocation")
                                location = location.get_text(strip=True) if location else "Unknown"
                                date_elem = job_card.select_one(".date")
                                date_posted = date_elem.get_text(strip=True) if date_elem else ""
                                
                                # Filter checks
                                if self._should_exclude(company, config):
                                    continue
                                
                                # Safely get href attribute
                                job_url = ""
                                if title_elem and title_elem.a:
                                    job_url = "https://www.indeed.com" + title_elem.a.get("href", "")
                                
                                jobs.append(Job(
                                    title=title,
                                    company=company,
                                    location=location,
                                    url=job_url,
                                    source="Indeed",
                                    date_posted=date_posted
                                ))
                            except Exception:
                                continue
                except Exception as e:
                    print(f"Error searching Indeed: {e}", file=sys.stderr)
        
        return jobs
    
    def _should_exclude(self, company: str, config: JobSearchConfig) -> bool:
        """Check if job should be excluded based on filters."""
        company_lower = company.lower()
        for exclude in config.get("exclude_keywords", []):
            if exclude.lower() in company_lower:
                return True
        return False


class CSVTracker:
    """Track jobs in CSV file."""
    
    def __init__(self, output_file: str):
        self.output_file = output_file
    
    def save_jobs(self, jobs: list[Job]) -> None:
        """Save jobs to CSV, appending new ones."""
        existing_urls = set()
        
        if os.path.exists(self.output_file):
            with open(self.output_file, "r", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    existing_urls.add(row.get("url", ""))
        
        new_jobs = [j for j in jobs if j.url not in existing_urls]
        
        if not new_jobs:
            print("No new jobs to save")
            return
        
        file_exists = os.path.exists(self.output_file) and os.path.getsize(self.output_file) > 0
        
        with open(self.output_file, "a", newline="", encoding="utf-8") as f:
            fieldnames = ["date_found", "title", "company", "location", "url", "source", "date_posted", "status"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            if not file_exists:
                writer.writeheader()
            
            today = datetime.now().strftime("%Y-%m-%d")
            for job in new_jobs:
                writer.writerow({
                    "date_found": today,
                    "title": sanitize_csv_field(job.title),
                    "company": sanitize_csv_field(job.company),
                    "location": sanitize_csv_field(job.location),
                    "url": job.url,
                    "source": job.source,
                    "date_posted": job.date_posted,
                    "status": "new"
                })
        
        print(f"Saved {len(new_jobs)} new jobs to {self.output_file}")


def run_job_search(config_path: Optional[str] = None, config: Optional[JobSearchConfig] = None) -> None:
    """Main entry point for job search."""
    if config is None:
        config = JobSearchConfig(config_path)
    
    print(f"Searching for jobs...")
    print(f"  Terms: {config.get('search_terms')}")
    print(f"  Locations: {config.get('locations')}")
    
    # Search Indeed
    indeed = IndeedJobSearcher()
    jobs = indeed.search(config)
    
    # Also search LinkedIn (placeholder - needs API)
    linkedin = LinkedInJobSearcher()
    jobs.extend(linkedin.search(config))
    
    print(f"Found {len(jobs)} jobs")
    
    # Save to tracker
    output_file = config.get("output_file", "tracker.csv")
    tracker = CSVTracker(output_file)
    tracker.save_jobs(jobs)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Job Pipeline Automation")
    parser.add_argument("--config", help="Path to config JSON file")
    parser.add_argument("--config-output", help="Path to output CSV file")
    args = parser.parse_args()
    
    # Create config and apply any output override
    config = JobSearchConfig(args.config)
    if args.config_output:
        config.config["output_file"] = args.config_output
    
    run_job_search(args.config, config)