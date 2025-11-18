<style>
    * {
        font-family: 'Nunito';
        max-width: 800px;
        font-weight: 300;
        letter-spacing: 0.4px;
        color: white;
    }
    .logo {
        margin-left: 5px; letter-spacing: 0.12em; display: block; color: white; font-weight: 800;font-size: 3.8em; clear: both; position: relative; width: fit-content; margin-bottom: 10px;
    }
    .head1 {
        margin-left: 5px; letter-spacing: 0.12em; display: block; color: white; font-weight: 800;font-size: 32px; clear: both; position: relative; width: fit-content; margin-bottom: 5px; padding-top: 65px;
    }

    .head2 {
        letter-spacing: 0.1em; display: block; margin-bottom: 10px;color: white; background-color: transparent; border-color: white; border-width: 2px; border-style: solid; border-radius: 5px;padding: 8px 15px; font-weight: bold;font-size: 1.4em; clear: both; position: relative; width: fit-content;
    }
    .head3 {
        letter-spacing: 0.1em; display: block; margin-bottom: 10px; color: white; background-color: transparent; padding: 8px 15px; font-weight: bold; font-size: 21px; clear: both; position: relative; width: fit-content; padding-left: 0px; padding-right: 0px;
    }
    .head3ol {
        letter-spacing: 0.1em; font-weight: 600; display: inline-block; font-size: 18px; padding-bottom: 8px; clear: both; position: relative; top: 10px;
    }
    .head3::after {
        width: 100%; height: 2px; border: 1px solid white; border-style: dashed; background-color: transparent; border-radius: 20px; display: block; margin-top: 0px; margin-bottom: 50px; position: relative; top: 10px; content: "";
    }
    .head4 {
        letter-spacing: 0.1em; display: block; margin-bottom: 10px;color: white; background-color: transparent;border-radius: 5px;padding: 2px 2px 8px 0px; font-weight: bold; font-size: 18px; clear: both; position: relative; width: fit-content;
    }
    .head4ol {
        letter-spacing: 0.1em; display: block; margin-bottom: 0px; color: white; background-color: transparent;font-weight: 500; font-size: 15px; clear: both; position: relative; width: fit-content; padding-top: 10px; padding-bottom: 0px;
    }
    .thick_line {
        width: 100%; height: 2px; border: 3px solid white; background-color: white; border-radius: 20px; display: block; margin-top: 20px; margin-bottom: 50px; position: relative; top: 10px;
    }
    .thick_line_heading {
        width: 100%; height: 2px; border: 2px solid white; background-color: white; border-radius: 20px; display: block; margin-top: 0px; margin-bottom: 50px; position: relative; top: 10px;
    }
    

</style>


<div class="logo" style="font-size: 3.8em;">job<span style="letter-spacing: 0.12em; color: white; font-weight: 400;">styr</span></div>

<div style="font-size: 18px; margin-bottom: 20px !important; padding-bottom: 20px; padding-left: 0; margin-left: 0;">Jobstyr is a tool that helps you focus on preparing for your next job instead of doing tedious tasks such as searching for jobs, applying to jobs, and optimizing your resume.</div>




<span class="head2">PRELIMINARY SETUP</span>

LINUX:
- sudo apt update
- sudo apt install python3-venv

---


<div class="head1">JOB PROCESSING, ANALYSIS, & RESUME OPTIMIZATION PIPELINE</div>
<span class="thick_line_heading"></span>






<span class="head3ol">PHASE 2</span>
<span class="head3">JOB SEARCH & EXTRACTION</span>



<div class="head4ol">PHASE 2.1</div>
<div class="head4">Job Collections</div>
    - Entry point script
    - Activates virtual environment
    - Sets PYTHONPATH
    - Calls main_get_jobs.py

2. main_get_jobs.py
    - Orchestrates the initial job collection process
    - Manages three main pipelines:
        - Job search
        - URL details collection
        - Job details merging
    - Uses JobMetricsTracker to record metrics throughout

3. job_search/job_extraction/job_search.py
    - Handles LinkedIn job search
    - Gets search parameters from user (salary, job type, etc.)
    - Uses Selenium to scrape job listings
    - Saves initial results to job_search/job_search_results/<job_title>/
    - Records metrics via JobMetricsTracker

4. job_search/job_extraction/job_url_details.py
    - Takes job URLs from previous step
    - Scrapes detailed job information from each listing
    - Extracts: job title, company, description, date posted, location, salary, remote status
    - Saves individual job details to job_search/job_post_details/<job_title>/job_details/

5. job_search/job_extraction/merge_job_details.py
    - Combines all individual job detail files
    - Removes duplicates based on job URL
    - Creates aggregated file in job_details/aggregated/
    - Saves both CSV and JSON versions with metadata

---

6. run_job_analysis.sh
    - Sets up Python environments for different models
    - Installs required packages and models
    - Manages the job analysis pipeline
    - Calls main_analyze_jobs.py

7. main_analyze_jobs.py
    - Orchestrates the text analysis pipeline
    - Manages both individual and aggregated analysis tracks
    - Calls various analysis modules in sequence

8. job_text_analysis/job_processor.py
    - Core analysis class handling both individual and aggregated analysis
    - Individual analysis:
        - Processes each job separately
        - Extracts keywords and skills
        - Saves to individual analysis files
    - Aggregated analysis:
        - Combines all job descriptions
        - Performs comprehensive analysis
        - Saves aggregated results

9. job_text_analysis/text_preproc/text_cleaning.py
    - Handles text preprocessing
    - Removes stop words
    - Normalizes text
    - Prepares text for analysis

10. text_insights_models/key_terms/keyword_extraction.py
    - Implements three keyword extraction models:
        - KeyBERT
        - YAKE
        - spaCy
    - Combines results from all models
    - Saves to nostop_keywords_processed/

11. text_insights_models/key_terms/word_clustering.py
    - Clusters similar keywords using DBSCAN
    - Uses sentence transformers for semantic similarity
    - Saves clustered results

12. text_insights_models/key_terms/keyword_classification.py
    - Uses OpenAI to classify keywords into categories
    - Categories include technical skills, soft skills, domain knowledge, etc.
    - Saves classified results

13. text_insights_models/key_terms/phrase_extraction.py
    - Extracts meaningful phrases using multiple methods:
        - KeyBERT
        - spaCy
        - OpenAI ChatGPT
    - Combines and deduplicates phrases
    - Saves final phrase list

14. job_search/job_metrics_tracker.py
    - Tracks metrics throughout the entire process
    - Maintains two types of records:
            - Job run metrics (search statistics)
        - Individual jobs aggregation
    - Saves to job_search/metrics/

Supporting Files:
config.py: Contains search parameters configuration
utils.py: Contains utility functions like cookie loading
directory_paths.py: Manages directory structure and paths





<span style="width: 100%; height: 2px; border: 3px solid white; background-color: white; border-radius: 20px; display: block; margin-top: 20px; margin-bottom: 50px; position: relative; top: 10px;"></span>























<span style="width: 100%; height: 2px; border: 3px solid white; background-color: white; border-radius: 20px; display: block; margin-top: 20px; margin-bottom: 50px; position: relative; top: 10px;"></span>




### USAGE
*Install the dependencies:*
```
pip install -r requirements.txt
```

<span class="thick_line"></span>





---

### 2:
## COMPANY INDEX




---

### 3:
## JOB DETAILS ANALYSIS & INSIGHTS

#### INPUTS
1. Preprocess job details text (alt version); *remove stop words, punctuation, etc.*
2. Utilize as input job details from */job_post_details* for relative job (==user input==)

#### ANALYSIS
3. Analyze each job description individually through text insights models (*ex. kBert, GPT-4o, etc.*):
    ==*Extract Key*==
    a: Terms (DONE)
    b: Phrases
    c: Technology
    d: Skills; *soft skills, hard skills, etc.*
    e: Concepts; *profession specific*

#### OUTPUTS
3. Job titles index (*cols: company_name, job_title*), job title term frequency index (*cols: term, count*)
4. Frequency Analysis:
    - *Term* frequency index (*cols: term, count, jobs_count, avg_count*)
    - *Technology* frequency index (*cols: technology, count, jobs_count, avg_count*)
    - *Skills* frequency index (*cols: skill, skill_type, count, jobs_count, avg_count*)
5. Concepts index (*cols: concept, company_name, job_title, approx_counts*)
6. Phrase index (*cols: phrase, company_name, job_title, approx_counts*)

---

### 4:
## RESUME DETAILS ANALYSIS & INSIGHTS

#### INPUTS
1. User input with the following:
    a: Job Information (==user input==)
        - *Job Title*
        - *Company Name*
        - *Company Public Status*
        - *Company Employee Count*
        - *Management Role*
        - *Qualitative Accomplishment* x 1
        - *Quantitative Accomplishment* x 2||3
    b: Skills Information (==user input==)
        - Skill Segment --> Skill Type --> *Skill Name*
    c: Technologies Information (==user input==)
        - Technology Segment --> Technology Type --> *Technology Name*
2. Extracted insights include:
    a: *Avg. Employment Duration*
    b: *Education Level*

### 5.
## RESUME OPTIMIZATION & GENERATION
1. Optimize the resume for the job:
    a: *Job Title* modifications required
    b: *Qualitative Accomplishment* modifications required
        - Sourced from term, concepts, phrase, and skills (soft) frequency index
    c: *Quantitative Accomplishment* modifications required
        - Sourced from term, concepts, phrase, technology, and skills (hard) frequency index
    d: *Skills* modifications required (sourced from skills frequency index)
    e: *Technologies* modifications required (sourced from technology frequency index)
2. Generate the resume:
    a: 


<span style="width: 100%; height: 2px; border: 3px solid white; background-color: white; border-radius: 20px; display: block; margin-top: 20px; margin-bottom: 50px; position: relative; top: 10px;"></span>

<span style="letter-spacing: 0.1em; display: block; margin-bottom: 10px;color: white; background-color: darkblue;border-radius: 5px;padding: 8px 15px; font-weight: bold;font-size: 1.4em; clear: both; position: relative; width: fit-content;">LINKEDIN INTEGRATION DETAILS</span>

<div style="padding-left: 15px;">
Search Filtering Options (LinkedIn)
Job Title:
    Exact Match (*Using Quotes*)
- Remote:
    - Remote
    - On-site
    - Hybrid
- Salary (Min):
    - $40,000
    - $60,000
    - $80,000
    - $100,000
    - $125,000
    - $150,000
    - $175,000
    - $200,000
- Job Type:
    - Full-time
    - Part-time
    - Contract
    - Internship
- Date Posted: *(Feature Coming Soon)*
    - Anytime
    - Past week
    - Past month
    - Past 24 hours

Search Filtering Options (Jobstyr) Extended: *(Feature Coming Soon)*
...


#### Job URL Samples (LinkedIn)
[Search Input: *"marketing" + "analytics" & Filters == Remote: Remote, Salary: $140,000+* = 1,598 results](https://www.linkedin.com/jobs/search/?currentJobId=4082014434&f_SB2=6&f_WT=2&geoId=103644278&keywords=marketing%20analytics&origin=JOB_SEARCH_PAGE_SEARCH_BUTTON&refresh=true)

[Search Input: *"marketing analytics" & Filters == Remote: Remote, Salary: $140,000+* = 12 results](https://www.linkedin.com/jobs/search/?currentJobId=4082607486&f_SB2=6&f_WT=2&geoId=103644278&keywords=%22Marketing%22%20%2B%20%22Analytics%22&origin=JOB_SEARCH_PAGE_JOB_FILTER&refresh=true&sortBy=R)

[Search Input: *"marketing" + "analytics" & Filters == Remote: Remote, Salary: $140,000+* = 21 results (Feature Coming Soon)](https://www.linkedin.com/jobs/search/?currentJobId=4082607486&f_SB2=6&f_WT=2&geoId=103644278&keywords=%22Marketing%22%20%2B%20%22Analytics%22&origin=JOB_SEARCH_PAGE_JOB_FILTER&refresh=true&sortBy=R)

[Search Input: * marketin ganalytics & Filters == Job Type: Full-time + Contract + Internship* = 26,000 results (Feature Coming Soon)](https://www.linkedin.com/jobs/search/?currentJobId=4087451166&f_JT=F%2CC%2CI&geoId=103644278&keywords=marketing%20analytics&origin=JOB_SEARCH_PAGE_JOB_FILTER&refresh=true&sortBy=R)
</div>