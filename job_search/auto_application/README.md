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


