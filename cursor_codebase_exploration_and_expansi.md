# Codebase exploration and expansion
_Exported on 1/10/2026 at 16:14:36 MST from Cursor (2.2.43)_

---

**User**

Can you explore my codebase to understand what everything does and how each process functions? I'd like to continue from this point and expand on functionalities.

---

**Cursor**

## What’s Here
- `main_get_jobs.py` orchestrates the multi-step search pipeline: ensures the `jobs_ran.csv` log, prompts for a job title, runs LinkedIn scraping (`job_search.py`), then enriches with apply URLs (`job_url_details.py`) and merges/dedupes details (`merge_job_details.py`). It also supports a fourth aggregation step (command wired but script not shown).```90:188:main_get_jobs.py
logging.info("Starting job search pipeline...")
...
logging.info("PIPELINE 1: Running the JOB SEARCH pipeline:")
cmd = ['python3', './job_search/job_extraction/job_search.py', '--job_title', job_title]
...
logging.info("PIPELINE 2: Running the JOB URL DETAILS pipeline:")
cmd = ['python3', './job_search/job_extraction/job_url_details.py', '--job_title', job_title, '--filename', latest_csv]
...
logging.info("PIPELINE 3: Running the JOB DETAILS MERGE pipeline:")
cmd = ['python3', './job_search/job_extraction/merge_job_details.py', '--job_title', job_title]
``` 
- `job_search/job_extraction/job_search.py` is the LinkedIn scraper. It prompts for salary range, job type, search type, and work geography (from `config.py`), builds a LinkedIn search URL, loads stored cookies, scrapes paginated results with Selenium, and saves CSV+JSON plus metrics.```221:382:job_search/job_extraction/job_search.py
search_params = get_search_parameters()
...
df = perform_linkedin_search(job_title, search_params)
...
saved_path = save_results(df, job_title, search_params, search_folder)
metrics_tracker.save_run_metrics(...)
metrics_tracker.update_jobs_aggregation(...)
``` 
- `job_search/job_extraction/job_url_details.py` visits each scraped job URL to extract an external apply link (or flags “Easy Apply”), using Selenium with multiple selectors/fallbacks and debug captures. It writes enriched CSV/JSON for later steps. (File is long; logic centers on `extract_application_url` and driver setup.)
- `job_search/job_extraction/merge_job_details.py` consolidates per-run CSVs into a master aggregated file, dedupes by URL and by company+title, filters salaries and engineering roles, and emits salary-filtered variants.```116:199:job_search/job_extraction/merge_job_details.py
salary_filtered_df = filter_by_salary(df, min_salary)
salary_filtered_df = filter_out_engineering_jobs(salary_filtered_df)
...
json.dump(output_data, f, indent=2, ensure_ascii=False)
``` 
- `job_search/job_extraction/driver_utils.py` centralizes undetected-chromedriver creation with random ports/profiles, anti-detection flags, and cleanup.```61:152:job_search/job_extraction/driver_utils.py
def create_driver(...):
    ...
    driver = uc.Chrome(..., version_main=chrome_version, use_subprocess=True, headless=headless)
...
def cleanup_driver(driver, temp_dir=None):
    driver.quit()
    shutil.rmtree(cleanup_dir, ignore_errors=True)
``` 
- Auto-application system (`job_search/auto_application`):
  - README explains config and usage; `user_config.json` holds personal info/resume paths.
  - `main_apply.py` loads jobs from a CSV (prefers `application_url`), skips already-applied via `ApplicationTracker`, detects board type, picks a form filler (Greenhouse/Workday/generic), fills forms, and logs attempts.```177:270:job_search/auto_application/main_apply.py
config = load_config()
jobs_df = load_jobs_from_csv(args.csv_file, limit=args.limit)
tracker = ApplicationTracker()
...
result = process_job_application(job_row, driver, config, tracker, args.auto_submit)
...
cleanup_driver(driver)
``` 
- Supporting run scripts:
  - `run_get_jobs.sh` activates env and calls `main_get_jobs.py`.
  - `run_auto_apply.sh` wraps `main_apply.py` with flags for headless/limit/delay/auto_submit.
  - `run_job_analysis.sh` sets up venvs (KeyBERT/YAKE/spaCy), merges job details, and runs `job_text_analysis.job_processor` for individual and aggregated analysis (requires `OPENAI_API_KEY`).
- Metrics/logging: `job_search/metrics` stores run metrics and aggregated job stats; `job_search/job_search_results` holds raw scrape outputs; `job_search/job_post_details/<title>` holds enriched and aggregated job detail CSV/JSON.

## How the processes fit together
1) Search & scrape: `main_get_jobs.py` → `job_search.py` prompts for filters, scrapes LinkedIn with stored cookies, saves CSV/JSON + metrics.  
2) Enrich apply URLs: `job_url_details.py` opens each job URL, extracts external apply link or flags Easy Apply, writes enriched CSV/JSON.  
3) Merge & aggregate: `merge_job_details.py` dedupes across runs, keeps master + salary-filtered (non-engineering) variants, updates JSON metadata.  
4) Auto-apply: `run_auto_apply.sh` / `main_apply.py` take any jobs CSV (ideally with `application_url`), fill ATS forms, log outcomes, prevent duplicates.  
5) Text analysis: `run_job_analysis.sh` merges details and runs NLP keyword/topic extraction per job and aggregated (KeyBERT/YAKE/spaCy/OpenAI).

## Expansion ideas
- Make the search pipeline non-interactive by allowing CLI flags/env for salary range, job type, and geography (fall back to prompts).  
- Add resilience to LinkedIn auth: detect missing/expired cookies early and prompt/guide manual refresh; optionally support username/password + MFA token for automation.  
- Harden apply-link extraction: cap retries, add structured outputs for failure reasons, and unit-test selectors against saved HTML in `debug_snapshots`.  
- Streamline aggregation: consider writing master + salary-filtered JSON/CSV in one place and exposing a latest-artifacts pointer for downstream steps.  
- Auto-apply safety: add a dry-run flag that stops before form submission but captures field mappings; expand form fillers for Lever/Workday edge cases.  
- Observability: centralize logs (per run folders) and add a lightweight status dashboard summarizing counts, failures, and where to resume.

## Quick usage reminders
- Run full search pipeline: `./run_get_jobs.sh` (prompts interactively).  
- Enrich/merge manually: `python3 job_search/job_extraction/job_url_details.py --job_title "<title>" --filename <csv>` then `python3 job_search/job_extraction/merge_job_details.py --job_title "<title>"`.  
- Auto-apply: `./run_auto_apply.sh --csv_file <path> [--limit N] [--delay 10] [--headless] [--auto_submit]`.  
- Analysis: `./run_job_analysis.sh "<job title>"` with `OPENAI_API_KEY` set.

Tell me which area you want to deepen first (config-driven search, more ATS fillers, analytics), and I’ll propose concrete changes/PR plan.

```python
- `job_search/job_extraction/job_search.py` is the LinkedIn scraper. It prompts for salary range, job type, search type, and work geography (from `config.py`), builds a LinkedIn search URL, loads stored cookies, scrapes paginated results with Selenium, and saves CSV+JSON plus metrics.```221:382:job_search/job_extraction/job_search.py
search_params = get_search_parameters()
...
df = perform_linkedin_search(job_title, search_params)
...
saved_path = save_results(df, job_title, search_params, search_folder)
metrics_tracker.save_run_metrics(...)
metrics_tracker.update_jobs_aggregation(...)
```

```plaintext
- `job_search/job_extraction/job_search.py` is the LinkedIn scraper. It prompts for salary range, job type, search type, and work geography (from `config.py`), builds a LinkedIn search URL, loads stored cookies, scrapes paginated results with Selenium, and saves CSV+JSON plus metrics.```221:382:job_search/job_extraction/job_search.py
search_params = get_search_parameters()
...
df = perform_linkedin_search(job_title, search_params)
...
saved_path = save_results(df, job_title, search_params, search_folder)
metrics_tracker.save_run_metrics(...)
metrics_tracker.update_jobs_aggregation(...)
```

```python
- `job_search/job_extraction/driver_utils.py` centralizes undetected-chromedriver creation with random ports/profiles, anti-detection flags, and cleanup.```61:152:job_search/job_extraction/driver_utils.py
def create_driver(...):
    ...
    driver = uc.Chrome(..., version_main=chrome_version, use_subprocess=True, headless=headless)
...
def cleanup_driver(driver, temp_dir=None):
    driver.quit()
    shutil.rmtree(cleanup_dir, ignore_errors=True)
```

```plaintext
- `job_search/job_extraction/driver_utils.py` centralizes undetected-chromedriver creation with random ports/profiles, anti-detection flags, and cleanup.```61:152:job_search/job_extraction/driver_utils.py
def create_driver(...):
    ...
    driver = uc.Chrome(..., version_main=chrome_version, use_subprocess=True, headless=headless)
...
def cleanup_driver(driver, temp_dir=None):
    driver.quit()
    shutil.rmtree(cleanup_dir, ignore_errors=True)
```

```python
- Supporting run scripts:
  - `run_get_jobs.sh` activates env and calls `main_get_jobs.py`.
  - `run_auto_apply.sh` wraps `main_apply.py` with flags for headless/limit/delay/auto_submit.
  - `run_job_analysis.sh` sets up venvs (KeyBERT/YAKE/spaCy), merges job details, and runs `job_text_analysis.job_processor` for individual and aggregated analysis (requires `OPENAI_API_KEY`).
- Metrics/logging: `job_search/metrics` stores run metrics and aggregated job stats; `job_search/job_search_results` holds raw scrape outputs; `job_search/job_post_details/<title>` holds enriched and aggregated job detail CSV/JSON.

## How the processes fit together
1) Search & scrape: `main_get_jobs.py` → `job_search.py` prompts for filters, scrapes LinkedIn with stored cookies, saves CSV/JSON + metrics.  
2) Enrich apply URLs: `job_url_details.py` opens each job URL, extracts external apply link or flags Easy Apply, writes enriched CSV/JSON.  
3) Merge & aggregate: `merge_job_details.py` dedupes across runs, keeps master + salary-filtered (non-engineering) variants, updates JSON metadata.  
4) Auto-apply: `run_auto_apply.sh` / `main_apply.py` take any jobs CSV (ideally with `application_url`), fill ATS forms, log outcomes, prevent duplicates.  
5) Text analysis: `run_job_analysis.sh` merges details and runs NLP keyword/topic extraction per job and aggregated (KeyBERT/YAKE/spaCy/OpenAI).

## Expansion ideas
- Make the search pipeline non-interactive by allowing CLI flags/env for salary range, job type, and geography (fall back to prompts).  
- Add resilience to LinkedIn auth: detect missing/expired cookies early and prompt/guide manual refresh; optionally support username/password + MFA token for automation.  
- Harden apply-link extraction: cap retries, add structured outputs for failure reasons, and unit-test selectors against saved HTML in `debug_snapshots`.  
- Streamline aggregation: consider writing master + salary-filtered JSON/CSV in one place and exposing a latest-artifacts pointer for downstream steps.  
- Auto-apply safety: add a dry-run flag that stops before form submission but captures field mappings; expand form fillers for Lever/Workday edge cases.  
- Observability: centralize logs (per run folders) and add a lightweight status dashboard summarizing counts, failures, and where to resume.

## Quick usage reminders
- Run full search pipeline: `./run_get_jobs.sh` (prompts interactively).  
- Enrich/merge manually: `python3 job_search/job_extraction/job_url_details.py --job_title "<title>" --filename <csv>` then `python3 job_search/job_extraction/merge_job_details.py --job_title "<title>"`.  
- Auto-apply: `./run_auto_apply.sh --csv_file <path> [--limit N] [--delay 10] [--headless] [--auto_submit]`.  
- Analysis: `./run_job_analysis.sh "<job title>"` with `OPENAI_API_KEY` set.

Tell me which area you want to deepen first (config-driven search, more ATS fillers, analytics), and I’ll propose concrete changes/PR plan.
```

```plaintext
- Supporting run scripts:
  - `run_get_jobs.sh` activates env and calls `main_get_jobs.py`.
  - `run_auto_apply.sh` wraps `main_apply.py` with flags for headless/limit/delay/auto_submit.
  - `run_job_analysis.sh` sets up venvs (KeyBERT/YAKE/spaCy), merges job details, and runs `job_text_analysis.job_processor` for individual and aggregated analysis (requires `OPENAI_API_KEY`).
- Metrics/logging: `job_search/metrics` stores run metrics and aggregated job stats; `job_search/job_search_results` holds raw scrape outputs; `job_search/job_post_details/<title>` holds enriched and aggregated job detail CSV/JSON.

## How the processes fit together
1) Search & scrape: `main_get_jobs.py` → `job_search.py` prompts for filters, scrapes LinkedIn with stored cookies, saves CSV/JSON + metrics.  
2) Enrich apply URLs: `job_url_details.py` opens each job URL, extracts external apply link or flags Easy Apply, writes enriched CSV/JSON.  
3) Merge & aggregate: `merge_job_details.py` dedupes across runs, keeps master + salary-filtered (non-engineering) variants, updates JSON metadata.  
4) Auto-apply: `run_auto_apply.sh` / `main_apply.py` take any jobs CSV (ideally with `application_url`), fill ATS forms, log outcomes, prevent duplicates.  
5) Text analysis: `run_job_analysis.sh` merges details and runs NLP keyword/topic extraction per job and aggregated (KeyBERT/YAKE/spaCy/OpenAI).

## Expansion ideas
- Make the search pipeline non-interactive by allowing CLI flags/env for salary range, job type, and geography (fall back to prompts).  
- Add resilience to LinkedIn auth: detect missing/expired cookies early and prompt/guide manual refresh; optionally support username/password + MFA token for automation.  
- Harden apply-link extraction: cap retries, add structured outputs for failure reasons, and unit-test selectors against saved HTML in `debug_snapshots`.  
- Streamline aggregation: consider writing master + salary-filtered JSON/CSV in one place and exposing a latest-artifacts pointer for downstream steps.  
- Auto-apply safety: add a dry-run flag that stops before form submission but captures field mappings; expand form fillers for Lever/Workday edge cases.  
- Observability: centralize logs (per run folders) and add a lightweight status dashboard summarizing counts, failures, and where to resume.

## Quick usage reminders
- Run full search pipeline: `./run_get_jobs.sh` (prompts interactively).  
- Enrich/merge manually: `python3 job_search/job_extraction/job_url_details.py --job_title "<title>" --filename <csv>` then `python3 job_search/job_extraction/merge_job_details.py --job_title "<title>"`.  
- Auto-apply: `./run_auto_apply.sh --csv_file <path> [--limit N] [--delay 10] [--headless] [--auto_submit]`.  
- Analysis: `./run_job_analysis.sh "<job title>"` with `OPENAI_API_KEY` set.

Tell me which area you want to deepen first (config-driven search, more ATS fillers, analytics), and I’ll propose concrete changes/PR plan.
```

```python
def create_driver(...):
    ...
    driver = uc.Chrome(..., version_main=chrome_version, use_subprocess=True, headless=headless)
...
def cleanup_driver(driver, temp_dir=None):
    driver.quit()
    shutil.rmtree(cleanup_dir, ignore_errors=True)
```

```python
config = load_config()
jobs_df = load_jobs_from_csv(args.csv_file, limit=args.limit)
tracker = ApplicationTracker()
...
result = process_job_application(job_row, driver, config, tracker, args.auto_submit)
...
cleanup_driver(driver)
```

---

**User**

Great.

Let's tackle all the expansion ideas you have one-by-one.

I've create a file to track the tasks we should do to manage/imporve this framework. Please add any tasks as you see fit to it. Let me know if you have any questsions - let's start with Task 1, Sub-Task A.

@backlog.md 

---

**Cursor**

```python
"""
Extract job-description variables to optimize the base resume.

Supports LLM-powered extraction (OpenAI) with a KeyBERT fallback.
Outputs a markdown file per job with incremental IDs and metadata.
"""

import argparse
import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd

OUTPUT_DIR = Path("job_search/auto_application/variables_extracted")
DEFAULT_MODEL = "gpt-4o-mini"


# -----------------------------
# Helpers
# -----------------------------
def sanitize(text: str) -> str:
    """Filesystem-friendly token."""
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_") or "job"


def next_file_id(output_dir: Path) -> int:
    """Find the next numeric ID based on existing files."""
    existing = []
    for f in output_dir.glob("*.md"):
        m = re.match(r"(\d+)_", f.name)
        if m:
            existing.append(int(m.group(1)))
    return (max(existing) if existing else 0) + 1


def read_description_from_csv(csv_path: Path, row: int, column: Optional[str]) -> str:
    df = pd.read_csv(csv_path)
    if df.empty:
        raise ValueError("CSV is empty.")

    if row >= len(df) or row < 0:
        raise IndexError(f"Row {row} out of range; CSV has {len(df)} rows.")

    candidate_cols = [column] if column else []
    candidate_cols += ["job_description", "description", "jd", "full_text"]

    for col in candidate_cols:
        if col and col in df.columns:
            val = df.iloc[row][col]
            if isinstance(val, str) and val.strip():
                return val

    raise ValueError(f"Could not find a non-empty description column in {candidate_cols}.")


def load_description(args: argparse.Namespace) -> str:
    if args.description_text:
        return args.description_text

    if args.description_file:
        path = Path(args.description_file)
        if not path.exists():
            raise FileNotFoundError(f"Description file not found: {path}")
        return path.read_text(encoding="utf-8")

    if args.source_csv:
        return read_description_from_csv(Path(args.source_csv), args.row, args.description_column)

    raise ValueError("No description provided. Use --description_text, --description_file, or --source_csv.")


# -----------------------------
# Extraction methods
# -----------------------------
def extract_with_llm(description: str, job_title: str, company: str, model: str = DEFAULT_MODEL) -> Dict[str, Any]:
    try:
        from openai import OpenAI  # Imported lazily to avoid hard dependency if unused

        client = OpenAI()
        prompt = (
            "You are extracting variables from a job description to optimize a resume. "
            "Use the provided label schema:\n"
            "- Content Type: Conceptual (C), Methodological (M), Technical (T), Operational (O), Tactical (Ta)\n"
            "- Info Architecture: Theory (TH), Methodology (MT), Framework (FR), Process (PR), Technique (TC), Tool (TL), Metric (ME), Model (MO)\n"
            "- Skills: Hard (HS), Soft (SS), Cognitive (CG), Domain Knowledge (DK)\n"
            "- Competency Level: Awareness, Knowledge, Skill, Mastery\n"
            "- Problem Types: Diagnostic (DG), Optimization (OP), Troubleshooting (TS), Innovation (IN), Prevention (PV)\n"
            "- Solution Approaches: Approach (AC), Strategy (ST), Tactic (TA), Heuristic (HE), Algorithm (AL)\n"
            "Return a concise JSON object with arrays for each category, a 'top_requirements' list, and a one-paragraph 'role_focus_summary'. "
            "Keep entries short and specific to the description."
        )

        messages = [
            {"role": "system", "content": "You extract structured variables from job descriptions for resume optimization."},
            {
                "role": "user",
                "content": json.dumps(
                    {
                        "job_title": job_title,
                        "company": company,
                        "description": description,
                        "instructions": prompt,
                    },
                    ensure_ascii=False,
                ),
            },
        ]

        resp = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.2,
            response_format={"type": "json_object"},
        )
        content = resp.choices[0].message.content
        return json.loads(content)
    except Exception as e:
        raise RuntimeError(f"LLM extraction failed: {e}")


def extract_with_keybert(description: str, top_n: int = 15) -> Dict[str, Any]:
    from keybert import KeyBERT  # Imported lazily

    kw_model = KeyBERT()
    keywords = [kw for kw, _ in kw_model.extract_keywords(description, keyphrase_ngram_range=(1, 2), stop_words="english", top_n=top_n)]

    return {
        "content_types": [],
        "info_architecture": [],
        "skills": [],
        "competencies": [],
        "problem_types": [],
        "solution_approaches": [],
        "top_requirements": keywords,
        "role_focus_summary": "Extracted via keyword relevance (no LLM available).",
    }


# -----------------------------
# Rendering
# -----------------------------
def render_markdown(
    job_title: str,
    company: str,
    description_source: str,
    extraction: Dict[str, Any],
    run_method: str,
) -> str:
    today = datetime.now().strftime("%Y-%m-%d")

    def section(title: str, items: Any) -> str:
        if not items:
            return f"### {title}\n- (none)\n"
        if isinstance(items, str):
            items = [items]
        return f"### {title}\n" + "\n".join(f"- {item}" for item in items) + "\n"

    lines = [
        f"# JD Variables – {job_title} @ {company}",
        "",
        "## Metadata",
        f"- job_title: {job_title}",
        f"- company: {company}",
        f"- date_extracted: {today}",
        f"- source: {description_source}",
        f"- method: {run_method}",
        "",
        "## Extracted Variables",
        section("Content Type Labels (C/M/T/O/Ta)", extraction.get("content_types")),
        section("Information Architecture (TH/MT/FR/PR/TC/TL/ME/MO)", extraction.get("info_architecture")),
        section("Skills & Competencies (HS/SS/CG/DK + levels)", extraction.get("skills") or extraction.get("competencies")),
        section("Problem Types (DG/OP/TS/IN/PV)", extraction.get("problem_types")),
        section("Solution Approaches (AC/ST/TA/HE/AL)", extraction.get("solution_approaches")),
        section("Top Requirements", extraction.get("top_requirements")),
        "### Role Focus Summary",
        extraction.get("role_focus_summary", "(none)"),
        "",
    ]
    return "\n".join(lines)


# -----------------------------
# Main CLI
# -----------------------------
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract JD variables for resume optimization.")
    parser.add_argument("--job_title", required=True, help="Job title for metadata and file naming.")
    parser.add_argument("--company", required=True, help="Company name for metadata and file naming.")
    parser.add_argument("--description_text", help="Raw job description text.")
    parser.add_argument("--description_file", help="Path to a text/markdown file containing the job description.")
    parser.add_argument("--source_csv", help="Path to a CSV containing job descriptions.")
    parser.add_argument("--row", type=int, default=0, help="Row index to read from CSV (default: 0).")
    parser.add_argument("--description_column", help="Column name in CSV to read (falls back to common names).")
    parser.add_argument("--use_llm", action="store_true", help="Use OpenAI for extraction (requires OPENAI_API_KEY).")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"OpenAI model to use (default: {DEFAULT_MODEL}).")
    return parser.parse_args()


def main():
    args = parse_args()
    description = load_description(args)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    file_id = next_file_id(OUTPUT_DIR)
    date_str = datetime.now().strftime("%Y%m%d")
    filename = f"{file_id:03d}_{sanitize(args.company)}_{sanitize(args.job_title)}_{date_str}.md"
    out_path = OUTPUT_DIR / filename

    extraction = {}
    method_used = "keybert_fallback"

    if args.use_llm:
        try:
            extraction = extract_with_llm(description, args.job_title, args.company, model=args.model)
            method_used = "openai_llm"
        except Exception as e:
            print(f"[warn] LLM extraction failed ({e}); falling back to KeyBERT.")

    if not extraction:
        extraction = extract_with_keybert(description)

    md = render_markdown(
        job_title=args.job_title,
        company=args.company,
        description_source=args.description_file or args.source_csv or "provided text",
        extraction=extraction,
        run_method=method_used,
    )

    out_path.write_text(md, encoding="utf-8")
    print(f"Wrote variables to {out_path}")


if __name__ == "__main__":
    main()

```

```markdown
## Task 1
### Sub-Task: A
### Status: In Progress
### Approved: Yes
Extract job description variables for base resume optimization (located in the directory 'job_search/auto_application/resumes/base_resume'); the variables (as a starting point - this can be expanded where more labeling can be created) are located under 'job_search/auto_application/jd_variables_extraction_glossary.md'. This functionality should extract the variables that are to be used to optimize the resume in a folder where each job's outputs will be stored in a separate .md file with a starting ID of 1 (increment for each new file) alongside the company name and job title in the file name - ending with the date of extraction in the format YYYMMDD.

### Sub-Task: A
### Status: Not Started
### Approved: Yes
Extract job description variables for base resume optimization (located in the directory 'job_search/auto_application/resumes/base_resume'); the variables (as a starting point - this can be expanded where more labeling can be created) are located under 'job_search/auto_application/jd_variables_extraction_glossary.md'. This functionality should extract the variables that would be optimally utilized in optimizing the base resume. The approach to take can be flexible and dynamic where we can utilize both machine learning (ex. NLP) models and libraries and lean on LLM APIs (ex. OpenAI, Claude) to identify these. The output should be the variables that are to be used to optimize the resume in a folder where each job's outputs will be stored in a separate .md file with a starting ID of 1 (increment for each new file) alongside the company name and job title in the file name - ending with the date of extraction in the format YYYMMDD.

### Sub-Task: B
### Status: Not Started
### Approved: Yes
Update the base resume with the extracted variables for the job defined in Sub-Task A; create a file for the resume with the same file name but extended with _ro (resume optimized). Please utilize the best and most reliable approach for this task as it will be the resume that is utilized for the job application.

### Sub-Task: C
### Status: Not Started
### Approved: Yes
Add a CLI helper to batch-run JD variable extraction against a job_details CSV (pick rows by index or filter) and drop markdown outputs into the variables_extracted folder.

### Sub-Task: D
### Status: Not Started
### Approved: Yes
Add lightweight tests/fixtures for the extractor (LLM mocked) to keep schemas stable and prevent regressions.

---

## Task 2
### Status: Not Started
### Approved: Yes### Status: Not Started
### Approved: Yes
Make the search pipeline non-interactive by allowing CLI flags/env for salary range, job type, and geography (fall back to prompts).

---
## Task 3
### Status: Not Started
### Approved: Yes
Add resilience to LinkedIn auth: detect missing/expired cookies early and prompt/guide manual refresh; optionally support username/password + MFA token for automation.

---
## Task 4
### Status: Not Started
### Approved: Yes
Harden apply-link extraction: cap retries, add structured outputs for failure reasons, and unit-test selectors against saved HTML in debug_snapshots.

---
## Task 5
### Status: Not Started
### Approved: Yes
Streamline aggregation: consider writing master + salary-filtered JSON/CSV in one place and exposing a latest-artifacts pointer for downstream steps.

---
## Task 6
### Status: Not Started
### Approved: Yes
Auto-apply safety: add a dry-run flag that stops before form submission but captures field mappings; expand form fillers for Lever/Workday edge cases.

---
## Task 7
### Status: Not Started
### Approved: Yes
Observability: centralize logs (per run folders) and add a lightweight status dashboard summarizing counts, failures, and where to resume.

---
## Task 8
### Status: Not Started
### Approved: Yes
Create a validation screenshot capture function to take screenshots of the application process as it moves through the process of each job and store it in a folder for checking the status of each step.
```

```markdown
*** Begin Patch
*** Update File: job_search/auto_application/README.md
@@
 ## Usage
@@
 ### Basic Usage
@@
 ```
 python3 -m job_search.auto_application.main_apply --csv_file path/to/jobs.csv
 ```
+
+### Extract JD variables for resume optimization
+
+Use the extractor to pull structured variables from a job description (LLM if available, with KeyBERT fallback). Outputs markdown files with incremental IDs in `job_search/auto_application/variables_extracted`.
+
+```bash
+# From raw text file
+python3 -m job_search.auto_application.extract_jd_variables \
+  --job_title "Senior Data Analyst" \
+  --company "ExampleCo" \
+  --description_file /path/to/job_description.txt \
+  --use_llm  # optional, requires OPENAI_API_KEY
+
+# From a CSV (uses job_description/description column; row 0 by default)
+python3 -m job_search.auto_application.extract_jd_variables \
+  --job_title "Senior Data Analyst" \
+  --company "ExampleCo" \
+  --source_csv job_search/job_post_details/analytics/job_details/analytics_job_details_20251113_154244.csv \
+  --row 0
 ```
*** End Patch
```

```markdown
# Auto-Application System

This module provides automated job application functionality, similar to Simplify.jobs but integrated into your job search pipeline. It can automatically fill out job application forms on various job board platforms.

## Features

- **Multi-platform support**: Works with Greenhouse, Workday, Lever, and other ATS platforms
- **Intelligent form detection**: Automatically detects and fills common form fields
- **Application tracking**: Prevents duplicate applications and logs all attempts
- **Visible browser**: Uses visible browser (not headless) so you can review before submitting
- **Configurable**: Easy-to-use configuration file for your personal information

## Setup

### 1. Configure Your Information

First, you need to set up your personal information. The system will create a default configuration file on first run, or you can create it manually:

```bash
python3 -c "from job_search.auto_application.config import load_config; load_config()"
```

This creates `job_search/auto_application/user_config.json`. Edit this file with your information:

```json
{
  "personal_info": {
    "first_name": "Your First Name",
    "last_name": "Your Last Name",
    "email": "your.email@example.com",
    "phone": "+1234567890",
    "preferred_name": "Preferred Name (optional)",
    "zip_code": "12345",
    "linkedin_profile": "https://linkedin.com/in/yourprofile",
    "location": "City, State",
    "city": "City"
  },
  "application_info": {
    "resume_path": "/path/to/your/resume.pdf",
    "cover_letter_path": "/path/to/cover/letter.pdf",
    "how_did_you_hear": "LinkedIn",
    "legally_authorized_to_work": "Yes",
    "require_visa_sponsorship": "No",
    "metro_area": "San Francisco Bay Area"
  },
  "work_authorization": {
    "authorized_to_work": true,
    "requires_sponsorship": false
  },
  "custom_answers": {
    "PEO industry experience": "I have 3 years of experience in the PEO industry...",
    "years of experience": "5+ years",
    "why interested": "I'm interested because..."
  }
}
```

### 2. Prepare Your Resume

Make sure your resume is in PDF format and update the `resume_path` in the configuration file.

## Usage

### Basic Usage

To auto-apply to jobs from a CSV file:

```bash
python3 -m job_search.auto_application.main_apply --csv_file path/to/jobs.csv
```

### Extract JD variables for resume optimization

Use the extractor to pull structured variables from a job description (LLM if available, with KeyBERT fallback). Outputs markdown files with incremental IDs in `job_search/auto_application/variables_extracted`.

```bash
# From raw text file
python3 -m job_search.auto_application.extract_jd_variables \
  --job_title "Senior Data Analyst" \
  --company "ExampleCo" \
  --description_file /path/to/job_description.txt \
  --use_llm  # optional, requires OPENAI_API_KEY

# From a CSV (uses job_description/description column; row 0 by default)
python3 -m job_search.auto_application.extract_jd_variables \
  --job_title "Senior Data Analyst" \
  --company "ExampleCo" \
  --source_csv job_search/job_post_details/analytics/job_details/analytics_job_details_20251113_154244.csv \
  --row 0
```

### Options

- `--csv_file`: (Required) Path to CSV file with job listings (must have `job_url` column)
- `--limit`: (Optional) Maximum number of jobs to process
- `--delay_between`: (Optional) Delay between applications in seconds (default: 5.0)
- `--headless`: (Optional) Run browser in headless mode (default: visible browser)
- `--auto_submit`: (Optional) Automatically submit applications (use with caution!)

### Examples

Apply to first 10 jobs from a CSV:
```bash
python3 -m job_search.auto_application.main_apply \
  --csv_file job_search/job_post_details/analytics/job_details/analytics_job_details_20251113_154244.csv \
  --limit 10
```

Apply with 10 second delay between applications:
```bash
python3 -m job_search.auto_application.main_apply \
  --csv_file job_search/job_post_details/analytics/job_details/analytics_job_details_20251113_154244.csv \
  --delay_between 10
```

## How It Works

1. **Job Board Detection**: The system automatically detects the job board type (Greenhouse, Workday, etc.) from the URL
2. **Form Filling**: Uses platform-specific form fillers to intelligently fill out application forms
3. **Field Matching**: Matches form fields using multiple strategies (name, ID, placeholder text)
4. **Application Tracking**: Logs all applications to prevent duplicates

## Supported Platforms

- **Greenhouse**: Full support with custom field handling
- **Workday**: Basic support (may require manual review)
- **Lever**: Basic support
- **Generic**: Heuristic-based filling for unknown platforms

## Application Tracking

All applications are logged to `job_search/auto_application/application_logs/applications.csv` with:
- Timestamp
- Job ID, title, company
- Job URL
- Job board type
- Status (success/failed)
- Whether it was submitted
- Error messages (if any)

The system automatically skips jobs you've already applied to.

## Safety Features

- **No auto-submit by default**: Applications are filled but not automatically submitted (you can review first)
- **Visible browser**: Browser is visible so you can see what's happening
- **Duplicate prevention**: Automatically skips already-applied jobs
- **Error handling**: Gracefully handles errors and continues with next job

## Important Notes

⚠️ **Review Before Submitting**: By default, the system fills forms but does NOT submit them. You should review each application before manually clicking submit.

⚠️ **Test First**: Test with a single job first to ensure your configuration is correct.

⚠️ **Rate Limiting**: Be respectful of job board rate limits. The default delay is 5 seconds between applications.

⚠️ **Custom Questions**: Some applications have custom questions that may need manual answers. The system will attempt to fill them using your `custom_answers` configuration.

## Troubleshooting

### Browser doesn't open
- Make sure you're not using `--headless` flag
- Check that Chrome/Chromium is installed

### Forms not filling correctly
- Some job boards have unique form structures
- Check the application logs for error messages
- You may need to manually complete some fields

### Resume not uploading
- Ensure the resume path in config is correct and absolute
- Check that the file exists and is a PDF
- Some sites may require manual file selection

## Integration with Job Search Pipeline

This system is designed to work with your existing job search pipeline. After running your job search and getting job details, you can use the resulting CSV files as input:

```bash
# 1. Run job search (existing pipeline)
python3 main_get_jobs.py

# 2. Auto-apply to jobs from the latest CSV
python3 -m job_search.auto_application.main_apply \
  --csv_file job_search/job_post_details/[job_title]/job_details/[latest_file].csv \
  --limit 20
```

## Future Enhancements

- Support for more job board platforms
- AI-powered custom question answering
- Cover letter generation
- Application status tracking
- Email notifications



```

```markdown
## Task 1
### Sub-Task: A
### Status: In Progress
### Approved: Yes
Extract job description variables for base resume optimization (located in the directory 'job_search/auto_application/resumes/base_resume'); the variables (as a starting point - this can be expanded where more labeling can be created) are located under 'job_search/auto_application/jd_variables_extraction_glossary.md'. This functionality should extract the variables that are to be used to optimize the resume in a folder where each job's outputs will be stored in a separate .md file with a starting ID of 1 (increment for each new file) alongside the company name and job title in the file name - ending with the date of extraction in the format YYYMMDD.


### Sub-Task: B
### Status: Not Started
### Approved: Yes
Update the base resume with the extracted variables for the job defined in Sub-Task A; create a file for the resume with the same file name but extended with _ro (resume optimized). Please utilize the best and most reliable approach for this task as it will be the resume that is utilized for the job application.

### Sub-Task: C
### Status: Not Started
### Approved: Yes
Add a CLI helper to batch-run JD variable extraction against a job_details CSV (pick rows by index or filter) and drop markdown outputs into the variables_extracted folder.

### Sub-Task: D
### Status: Not Started
### Approved: Yes
Add lightweight tests/fixtures for the extractor (LLM mocked) to keep schemas stable and prevent regressions.

---

## Task 2
### Status: Not Started
### Approved: Yes### Status: Not Started
### Approved: Yes
Make the search pipeline non-interactive by allowing CLI flags/env for salary range, job type, and geography (fall back to prompts).

---
## Task 3
### Status: Not Started
### Approved: Yes
Add resilience to LinkedIn auth: detect missing/expired cookies early and prompt/guide manual refresh; optionally support username/password + MFA token for automation.

---
## Task 4
### Status: Not Started
### Approved: Yes
Harden apply-link extraction: cap retries, add structured outputs for failure reasons, and unit-test selectors against saved HTML in debug_snapshots.

---
## Task 5
### Status: Not Started
### Approved: Yes
Streamline aggregation: consider writing master + salary-filtered JSON/CSV in one place and exposing a latest-artifacts pointer for downstream steps.

---
## Task 6
### Status: Not Started
### Approved: Yes
Auto-apply safety: add a dry-run flag that stops before form submission but captures field mappings; expand form fillers for Lever/Workday edge cases.

---
## Task 7
### Status: Not Started
### Approved: Yes
Observability: centralize logs (per run folders) and add a lightweight status dashboard summarizing counts, failures, and where to resume.

---
## Task 8
### Status: Not Started
### Approved: Yes
Create a validation screenshot capture function to take screenshots of the application process as it moves through the process of each job and store it in a folder for checking the status of each step.
```

```markdown
## Task 1
### Sub-Task: A
### Status: In Progress
### Approved: Yes
Extract job description variables for base resume optimization (located in the directory 'job_search/auto_application/resumes/base_resume'); the variables (as a starting point - this can be expanded where more labeling can be created) are located under 'job_search/auto_application/jd_variables_extraction_glossary.md'. This functionality should extract the variables that are to be used to optimize the resume in a folder where each job's outputs will be stored in a separate .md file with a starting ID of 1 (increment for each new file) alongside the company name and job title in the file name - ending with the date of extraction in the format YYYMMDD.


### Sub-Task: B
### Status: Not Started
### Approved: Yes
Update the base resume with the extracted variables for the job defined in Sub-Task A; create a file for the resume with the same file name but extended with _ro (resume optimized). Please utilize the best and most reliable approach for this task as it will be the resume that is utilized for the job application.

### Sub-Task: C
### Status: Not Started
### Approved: Yes
Add a CLI helper to batch-run JD variable extraction against a job_details CSV (pick rows by index or filter) and drop markdown outputs into the variables_extracted folder.

### Sub-Task: D
### Status: Not Started
### Approved: Yes
Add lightweight tests/fixtures for the extractor (LLM mocked) to keep schemas stable and prevent regressions.

---

## Task 2
### Status: Not Started
### Approved: Yes
Make the search pipeline non-interactive by allowing CLI flags/env for salary range, job type, and geography (fall back to prompts).

---
## Task 3
### Status: Not Started
### Approved: Yes
Add resilience to LinkedIn auth: detect missing/expired cookies early and prompt/guide manual refresh; optionally support username/password + MFA token for automation.

---
## Task 4
### Status: Not Started
### Approved: Yes
Harden apply-link extraction: cap retries, add structured outputs for failure reasons, and unit-test selectors against saved HTML in debug_snapshots.

---
## Task 5
### Status: Not Started
### Approved: Yes
Streamline aggregation: consider writing master + salary-filtered JSON/CSV in one place and exposing a latest-artifacts pointer for downstream steps.

---
## Task 6
### Status: Not Started
### Approved: Yes
Auto-apply safety: add a dry-run flag that stops before form submission but captures field mappings; expand form fillers for Lever/Workday edge cases.

---
## Task 7
### Status: Not Started
### Approved: Yes
Observability: centralize logs (per run folders) and add a lightweight status dashboard summarizing counts, failures, and where to resume.

---
## Task 8
### Status: Not Started
### Approved: Yes
Create a validation screenshot capture function to take screenshots of the application process as it moves through the process of each job and store it in a folder for checking the status of each step.
```

Added a JD variable extractor CLI with LLM (OpenAI) + KeyBERT fallback, automatic IDed markdown outputs, CSV/text inputs, and schema-aware rendering for resume optimization. Updated README with usage and backlog with new subtasks and Task 1 status. No lints triggered.

Key additions
- New script `extract_jd_variables.py` handles input (text/file/CSV), optional OpenAI call, KeyBERT fallback, sanitized filenames with incremental IDs and YYYMMDD suffix, and markdown output grouped by your glossary labels.```8:236:job_search/auto_application/extract_jd_variables.py
"""Extract job-description variables to optimize the base resume.
...
if __name__ == "__main__":
    main()
``` 
- README documents how to run the extractor from text or CSV and where outputs land.```62:90:job_search/auto_application/README.md
### Extract JD variables for resume optimization
...
--row 0
``` 
- Backlog now marks Task 1A In Progress and adds subtasks C (batch CLI helper) and D (tests/fixtures).```1:21:backlog.md
### Sub-Task: A
### Status: In Progress
...
### Sub-Task: D
``` 

How to run
- Text file: `python3 -m job_search.auto_application.extract_jd_variables --job_title "Senior Data Analyst" --company "ExampleCo" --description_file /path/to/jd.txt --use_llm` (requires `OPENAI_API_KEY` for LLM).
- CSV row: `python3 -m job_search.auto_application.extract_jd_variables --job_title "Senior Data Analyst" --company "ExampleCo" --source_csv path/to/job_details.csv --row 0`.
- Outputs land in `job_search/auto_application/variables_extracted` as `NNN_company_jobtitle_YYYYMMDD.md`.

Next steps
- Provide a sample job description (or a job_details CSV + target row) so I can run the extractor once and validate the output format.
- If you want, I can wire Sub-Task C to batch over a CSV and add tests (Sub-Task D) to pin the schema.

```python
- README documents how to run the extractor from text or CSV and where outputs land.```62:90:job_search/auto_application/README.md
### Extract JD variables for resume optimization
...
--row 0
```

```plaintext
- README documents how to run the extractor from text or CSV and where outputs land.```62:90:job_search/auto_application/README.md
### Extract JD variables for resume optimization
...
--row 0
```

```plaintext

How to run
- Text file: `python3 -m job_search.auto_application.extract_jd_variables --job_title "Senior Data Analyst" --company "ExampleCo" --description_file /path/to/jd.txt --use_llm` (requires `OPENAI_API_KEY` for LLM).
- CSV row: `python3 -m job_search.auto_application.extract_jd_variables --job_title "Senior Data Analyst" --company "ExampleCo" --source_csv path/to/job_details.csv --row 0`.
- Outputs land in `job_search/auto_application/variables_extracted` as `NNN_company_jobtitle_YYYYMMDD.md`.

Next steps
- Provide a sample job description (or a job_details CSV + target row) so I can run the extractor once and validate the output format.
- If you want, I can wire Sub-Task C to batch over a CSV and add tests (Sub-Task D) to pin the schema.
```

```plaintext

How to run
- Text file: `python3 -m job_search.auto_application.extract_jd_variables --job_title "Senior Data Analyst" --company "ExampleCo" --description_file /path/to/jd.txt --use_llm` (requires `OPENAI_API_KEY` for LLM).
- CSV row: `python3 -m job_search.auto_application.extract_jd_variables --job_title "Senior Data Analyst" --company "ExampleCo" --source_csv path/to/job_details.csv --row 0`.
- Outputs land in `job_search/auto_application/variables_extracted` as `NNN_company_jobtitle_YYYYMMDD.md`.

Next steps
- Provide a sample job description (or a job_details CSV + target row) so I can run the extractor once and validate the output format.
- If you want, I can wire Sub-Task C to batch over a CSV and add tests (Sub-Task D) to pin the schema.
```

```plaintext
### Sub-Task: A
### Status: In Progress
...
### Sub-Task: D
```

