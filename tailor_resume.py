import os
import time
from google import genai
from google.genai import errors

def tailor_resume():
    # Initialize the Gemini Client
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    
    # Read your files
    try:
        with open("resume.tex", "r") as f:
            resume_content = f.read()
        with open("job_description.txt", "r") as f:
            job_description = f.read()
    except FileNotFoundError as e:
        print(f"Error: Required file missing - {e}")
        return

    # The Prompt
    prompt = f"""
    You are an expert resume writer. Below is a LaTeX resume template and a Job Description.
    Tailor the 'Skills' and 'Experience' sections of the resume to match the Job Description.
    
    STRICT RULES:
    1. Output ONLY the raw LaTeX code. 
    2. Do NOT change the LaTeX preamble or formatting commands.
    3. Ensure all LaTeX tags (like \\item, \\section, \\textbf) remain intact.
    
    RESUME TEMPLATE:
    {resume_content}
    
    JOB DESCRIPTION:
    {job_description}
    """

    max_tries = 10
    retry_delay = 30  # seconds

    for attempt in range(1, max_tries + 1):
        try:
            print(f"--- Attempt {attempt}/{max_tries}: Generating tailored resume ---")
            
            # Using the 2026 workhorse model
            response = client.models.generate_content(
                model="gemini-2.5-flash", 
                contents=prompt
            )

            # Save the new LaTeX file if successful
            with open("tailored_resume.tex", "w") as f:
                f.write(response.text.strip())
            
            print("✅ Success! Resume tailored and saved to tailored_resume.tex")
            return  # Exit the function on success

        except errors.APIError as e:
            # Retryable errors: 429 (Quota), 500, 502, 503, 504 (Server Overload)
            if e.code in [429, 500, 502, 503, 504]:
                if attempt < max_tries:
                    print(f"⚠️ Service busy or limit reached (Error {e.code}). Retrying in {retry_delay}s...")
                    time.sleep(retry_delay)
                else:
                    print("❌ Max retries reached. Service is still unavailable.")
                    raise e
            else:
                # Non-retryable errors (e.g., 400 Bad Request, 401 Unauthorized)
                print(f"🛑 Permanent Error encountered ({e.code}): {e.message}")
                raise e

if __name__ == "__main__":
    tailor_resume()