import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
import csv
import os
import requests
import mysql.connector

# Database connection function
def get_db_connection():
    conn = mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME')
    )
    print(f"🔗 Connected to database: {conn.database}")
    return conn

# Function to fetch Glassdoor jobs from the API
def fetch_glassdoor_jobs(role, location):
    print(f"\n🔍 Fetching Glassdoor jobs for '{role}' in '{location}'\n")

    headers = {
    "X-RapidAPI-Key": os.getenv('RAPIDAPI_KEY'),
    "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
}

    url = "https://jsearch.p.rapidapi.com/search"
    querystring = {"query": f"{role} in {location}", "page": "1", "num_pages": "2"}
    
    try:
        response = requests.get(url, headers=headers, params=querystring)
        
        if response.status_code != 200:
            print(f"❌ Failed to fetch jobs (status {response.status_code})")
            return []

        data = response.json().get("data", [])
        jobs = []

        for job in data:
            # Extract location with better formatting
            city = job.get("job_city")
            state = job.get("job_state")
            country = job.get("job_country")
            is_remote = job.get("job_is_remote", False)
            
            # Build location string
            location_parts = []
            if city:
                location_parts.append(city)
            if state:
                location_parts.append(state)
            if country and country != "IN":  # Only show country if not India (since we're searching in India)
                location_parts.append(country)
            
            if is_remote:
                location_str = "Remote - " + ", ".join(location_parts) if location_parts else "Remote"
            elif location_parts:
                location_str = ", ".join(location_parts)
            else:
                location_str = "India (Location not specified)"
            
            # Extract salary with multiple attempts
            salary_str = "Not Disclosed"
            if job.get("job_min_salary") and job.get("job_max_salary"):
                currency = job.get("job_salary_currency", "USD")
                min_sal = job.get("job_min_salary")
                max_sal = job.get("job_max_salary")
                salary_str = f"{currency} {min_sal:,} - {max_sal:,}"
            elif job.get("job_salary"):
                salary_str = str(job.get("job_salary"))
            
            jobs.append({
                "source": "Glassdoor",
                "title": job.get("job_title", "N/A"),
                "company": job.get("employer_name", "N/A"),
                "location": location_str,
                "job_type": job.get("job_employment_type", "Full-time"),
                "salary": salary_str,
                "posted": job.get("job_posted_at_datetime_utc", "N/A"),
                "summary": job.get("job_description", "No description available")[:400],
                "benefits": str(job.get("job_highlights", {}).get("Benefits", ["N/A"])),
                "link": job.get("job_apply_link") or job.get("job_google_link", "N/A")
            })
        
        print(f"✅ Fetched {len(jobs)} jobs from API")
        return jobs
    except Exception as e:
        print(f"❌ Error fetching jobs: {str(e)}")
        return []


# Function to save scraped jobs into both database and CSV
def save_jobs_to_db_and_csv(jobs):
    if not jobs:
        print("⚠️ No jobs to save!")
        return
    
    # Create output directory if it doesn't exist
    os.makedirs("output", exist_ok=True)
    
    csv_file = "output/jobs_data.csv"
    
    # Save to CSV
    with open(csv_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([
            "Source", "Job Title", "Company", "Location", "Job Type",
            "Salary", "Posted", "Job Summary", "Benefits", "Job Link"
        ])
        
        for job in jobs:
            writer.writerow([
                job["source"], job["title"], job["company"], job["location"],
                job["job_type"], job["salary"], job["posted"], job["summary"],
                job["benefits"], job["link"]
            ])
    
    # Save to database
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        inserted_count = 0
        for job in jobs:
            try:
                cursor.execute("""
                    INSERT INTO jobs (Source, Job_Title, Company, Location, Job_Type, Salary, Posted, Job_Summary, Benefits, Job_Link)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    job["source"], job["title"], job["company"], job["location"],
                    job["job_type"], job["salary"], job["posted"], job["summary"],
                    job["benefits"], job["link"]
                ))
                inserted_count += 1
            except Exception as e:
                print(f"❌ Error inserting job '{job.get('title', 'Unknown')}': {str(e)}")
        
        conn.commit()
        cursor.close()
        conn.close()
        print(f"\n✅ Successfully inserted {inserted_count} jobs into database")
        print(f"✅ Saved to {csv_file}")
    except Exception as e:
        print(f"❌ Database connection error: {str(e)}")


# Main scraping function called by Flask app
def scrape_jobs(role, location):
    print(f"🔍 Fetching jobs for '{role}' in '{location}' ...")
    jobs = fetch_glassdoor_jobs(role, location)
    
    if jobs:
        save_jobs_to_db_and_csv(jobs)
    else:
        print("⚠️ No jobs found!")


# For standalone execution
if __name__ == "__main__":
    print("=== Tech Job Portal API Scraper ===")
    role = input("Enter job role: ").strip()
    location = input("Enter job location: ").strip()

    scrape_jobs(role, location)