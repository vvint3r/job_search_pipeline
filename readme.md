# **Jobstyr**

==Jobstyr is a tool that helps you find job listings and apply to them.==

**PRELIMINARY SETUP**

- sudo apt update
- sudo apt install python3-venv

---

### 1:
## **JOB SEARCH & EXTRACTION**

### USAGE
*Install the dependencies:*
```
pip install -r requirements.txt
```

1. Run `./xxx.sh` to run the job search pipeline.




---

### 2:
## **COMPANY INDEXING**

### **APOLLO.IO**
**Filtering parameters:**
- Employee Count > 100
- Industries: *
- Geography: United States

*ENV VARS*
- export UNDETECTED_CHROMEDRIVER_DELAY_STARTUP=5
- export UNDETECTED_CHROMEDRIVER_PAGE_LOAD_TIMEOUT=30

### **APOLLO EXTRACTIONS**
1: Login to Apollo
2: Navigate to Companies from the left menu
3: Collect the 25 companies from the first page
4: For each company, collect the following data:
    *- Company Name
    - Company URL
    - Company LinkedIn
    - Company Industries
    - Company Employees*
5: Click the next page button if available
6: Repeat steps 3-5 until all pages are processed
7: Write the data to a CSV file


# DNB (Backup Resource)

Source URL:([DNB Business Directory](https://www.dnb.com/business-directory.html#BusinessDirectoryPageNumber=1&ContactDirectoryPageNumber=1&MarketplacePageNumber=1&SiteContentPageNumber=1&tab=Business%20Directory))


---

### 3:
## **JOB DETAILS ANALYSIS & INSIGHTS**

#### INPUTS
1. **Preprocess job details** text (alt version); *remove stop words, punctuation, etc.*
2. **Utilize** as input **job details** from */job_post_details* for relative job (==user input==)

#### ANALYSIS
3. **Analyze** each **job description** individually through text insights models (*ex. kBert, GPT-4o, etc.*):
    ==*Extract Key*==
    a: Terms (DONE)
    b: Phrases
    c: Technology
    d: Skills; *soft skills, hard skills, etc.*
    e: Concepts; *profession specific*

#### OUTPUTS
3. Job **titles index** (*cols: company_name, job_title*), **job title term** frequency index (*cols: term, count*)
4. **Frequency** Analysis:
    - *Term* frequency index (*cols: term, count, jobs_count, avg_count*)
    - *Technology* frequency index (*cols: technology, count, jobs_count, avg_count*)
    - *Skills* frequency index (*cols: skill, skill_type, count, jobs_count, avg_count*)
5. **Concepts** index (*cols: concept, company_name, job_title, approx_counts*)
6. **Phrase** index (*cols: phrase, company_name, job_title, approx_counts*)

---

### 4:
## **RESUME DETAILS ANALYSIS & INSIGHTS**

#### INPUTS
1. User input with the following:
    a: **Job Information** (==user input==)
        - *Job Title*
        - *Company Name*
        - *Company Public Status*
        - *Company Employee Count*
        - *Management Role*
        - *Qualitative Accomplishment* x 1
        - *Quantitative Accomplishment* x 2||3
    b: **Skills Information** (==user input==)
        - Skill Segment --> Skill Type --> *Skill Name*
    c: **Technologies Information** (==user input==)
        - Technology Segment --> Technology Type --> *Technology Name*
2. **Extracted insights** include:
    a: *Avg. Employment Duration*
    b: *Education Level*

### 5.
## **RESUME OPTIMIZATION & GENERATION**
1. **Optimize** the resume for the job:
    a: *Job Title* modifications required
    b: *Qualitative Accomplishment* modifications required
        - Sourced from term, concepts, phrase, and skills (soft) frequency index
    c: *Quantitative Accomplishment* modifications required
        - Sourced from term, concepts, phrase, technology, and skills (hard) frequency index
    d: *Skills* modifications required (sourced from skills frequency index)
    e: *Technologies* modifications required (sourced from technology frequency index)
2. **Generate** the resume:
    a: 
