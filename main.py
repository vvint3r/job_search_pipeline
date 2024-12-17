
# 1. /home/wynt3r/JobSearch/job_search.py
# 2. /home/wynt3r/JobSearch/job_url_details.py
# 3. /home/wynt3r/JobSearch/job_details_preprocessing.py
# 4. /home/wynt3r/JobSearch/job_details_kwd_metrics.py

# 5. /home/wynt3r/JobSearch/job_details_keywords__openai.py
# 6. /home/wynt3r/JobSearch/job_details_keywords__tfidf.py
# 7. /home/wynt3r/JobSearch/job_details_keywords__kbert.py

# 8. /home/wynt3r/JobSearch/resume_optimization.py
# 9. /home/wynt3r/JobSearch/resume_kwd_compare.py



import sys
import subprocess


def run_script(script_path, job_title):
    """Run a Python script with a job title as an argument."""
    try:
        print(f"Running {script_path} with job_title: {job_title}...")
        subprocess.run(["python", script_path, job_title], check=True)
        print(f"Successfully executed {script_path}.")
    except subprocess.CalledProcessError as e:
        print(f"Error executing {script_path}: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Define job title and script paths
    job_title = "SEO Manager"

    # Define script paths
    scripts = {
        "job_search": "/home/wynt3r/JobSearch/job_search.py",
        "job_url_details": "/home/wynt3r/JobSearch/job_url_details.py"
    }

    # Run scripts sequentially
    print("PIPELINE 1: Running the JOB SEARCH pipeline:")
    run_script(scripts["job_search"], job_title)
    print("PIPELINE 2: Running the JOB DETAILS EXTRACTION pipeline:")
    run_script(scripts["job_url_details"], job_title)

    print("All scripts executed successfully.")
