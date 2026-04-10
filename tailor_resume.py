import os
import time
import re
from google import genai
from google.genai import errors

def clean_latex(text):
    text = re.sub(r"```latex", "", text, flags=re.IGNORECASE)
    text = re.sub(r"```", "", text)
    return text.strip()

def tailor_resume():
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    
    try:
        with open("resume.tex", "r") as f:
            resume_content = f.read()
        with open("job_description.txt", "r") as f:
            job_description = f.read()
        # NEW: Read user-specific instructions
        with open("user_instructions.txt", "r") as f:
            user_instructions = f.read()
    except FileNotFoundError as e:
        print(f"❌ Error: Required file missing - {e}")
        return

    # THE ENHANCED "HUMAN-LIKE" PROMPT
    prompt = f"""
    You are an elite Career Coach and LaTeX Expert. Your goal is to tailor a resume so it passes ATS 
    but looks 100% human-written. Avoid AI-generated cliches like "passionate professional," 
    "leveraged," or "synergy." Use strong action verbs and metrics.

    STRICT CONSTRAINTS:
    1. LENGTH: The final resume MUST fit on exactly ONE PAGE. Be concise.
    2. BULLET POINTS: Every Project and Internship section MUST have EXACTLY 3 bullet points. No more, no less.
    3. WRITING STYLE: Use the STAR method (Situation, Task, Action, Result). Use technical data and numbers.
    4. USER INSTRUCTIONS: {user_instructions} (Prioritize these instructions over the template).
    5. NO MARKDOWN: Output ONLY raw LaTeX. Start with \\documentclass.

    INPUT DATA:
    - JOB DESCRIPTION: {job_description}
    - RESUME TEMPLATE: {resume_content}

    TASK:
    - Update 'Skills' to include keywords from the JD.
    - Rewrite 'Experience' and 'Projects' to match the JD requirements.
    - If the User Instructions ask to swap/add projects, perform that change within the LaTeX structure.
    - Ensure all LaTeX syntax (\\item, \\section) is perfectly preserved.
    """

    max_tries = 10
    retry_delay = 30

    for attempt in range(1, max_tries + 1):
        try:
            print(f"--- Attempt {attempt}: Generating Human-Like Resume ---")
            response = client.models.generate_content(
                model="gemini-2.5-flash", 
                contents=prompt
            )

            final_latex = clean_latex(response.text)
            with open("tailored_resume.tex", "w") as f:
                f.write(final_latex)
            
            print("✅ Success! Human-like LaTeX saved.")
            return

        except errors.APIError as e:
            if e.code in [429, 500, 502, 503, 504]:
                time.sleep(retry_delay)
            else:
                raise e

if __name__ == "__main__":
    tailor_resume()