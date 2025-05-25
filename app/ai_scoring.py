# ai_scoring.py
import google.generativeai as genai
import json
import re

# name, Score, Feedback

genai.configure(api_key="AIzaSyAQf0XdTsBxAQAmEutisUelPgqFbQFRaks")  # Replace with your actual Gemini API key

def score_candidate(candidate):
    prompt = f"""
    You are an evaluator for a coding competition.

    Evaluate the candidate based on:
    1. Status (student, employed, etc.)
    2. Formation/Certifications
    3. Projects

    Return JSON:
    {{
    "Overall score": <score>,
    "Comment": "<brief reasoning>"
    }}

    Candidate:
    Name: {candidate['name']}
    Status: {candidate['status']}
    Certifications: {candidate['certifs']}
    Projects: {candidate['projects']}
    """

    model = genai.GenerativeModel("gemini-1.5-pro")
    response = model.generate_content(prompt)

    try:
        cleaned = re.sub(r"^```json|```$", "", response.text.strip(), flags=re.MULTILINE).strip()
        return json.loads(cleaned)
    except Exception as e:
        print("❌ Failed to parse Gemini response:", response.text)
        return {
            "Status": None,
            "Formation/Certification": None,
            "Projects": None,
            "Overall score": None,
            "Comment": "Gemini response could not be parsed."
        }
