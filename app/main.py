from flask import Flask, request, render_template
from pathlib import Path
import pandas as pd
from ai_scoring import score_candidate  # Make sure this returns scores correctly

app = Flask(__name__)

# Function to check if the candidate is old based on their name from the excel file (oldSubmissions.xlsx)
def isOld(name):
    old_excel_file = Path("oldSubmissions.xlsx")
    if not old_excel_file.exists():
        return False

    df = pd.read_excel(old_excel_file)
    
    if "Name" in df.columns:
        return name in df["Name"].values
    return False

@app.route('/')
def form():
    return render_template('form.html')

@app.route('/admin')
def admin():
    excel_file = Path("submissions.xlsx")
    data = []

    if excel_file.exists():
        df = pd.read_excel(excel_file)

        # Ensure the column exists and sort by "Overall score" descending
        if "Overall score" in df.columns:
            df = df.sort_values(by="Overall score", ascending=False)
        data = df.to_dict(orient='records')
    return render_template("admin.html", data=data)

@app.route('/accept', methods=['POST'])
def accept_participants():
    num = int(request.form['num_participants'])
    excel_file = Path("submissions.xlsx")

    if excel_file.exists():
        df = pd.read_excel(excel_file)
        if "Overall score" in df.columns:
            df = df.sort_values(by="Overall score", ascending=False)

        accepted = df.head(num)
        # Or render in a new template
        data = accepted.to_dict(orient='records')
        return render_template("accepted.html", data=data, num=num)

    return "No data available", 400

@app.route('/submit', methods=['POST'])
def submit():
    candidate = {
        "email": request.form.get("email"),
        "name": request.form.get("name"),
        "github": request.form.get("github"),
        "linkedin": request.form.get("linkedin"),
        "projects": request.form.get("projects"),
        "certifs": request.form.get("certifs"),
        "past_participation": request.form.get("past_participation"),
        "ai_stack": request.form.get("ai_stack"),
        "project": request.form.get("project"),
        "status": request.form.get("status")
    }

    # if (not isOld(candidate["name"])):
    #     row = {
    #         "Name": candidate["name"],
    #         # "Status score": scores.get("Status"),
    #         # "Formation score": scores.get("Formation/Certification"),
    #         # "Projects score": scores.get("Projects"),
    #         "Overall score": 0,
    #         "Status": candidate["status"],
    #         "Comment": "Already participated in a previous hackathon, so no score is given."
    #     }
    # else:
    scores = score_candidate(candidate)
    row = {
        "Name": candidate["name"],
        # "Status score": scores.get("Status"),
        # "Formation score": scores.get("Formation/Certification"),
        # "Projects score": scores.get("Projects"),
        "Overall score": scores.get("Overall score"),
        "Status": candidate["status"],
        "Comment": scores.get("Comment")
    }


    # Excel path
    excel_file = Path("submissions.xlsx")

    # Load or initialize DataFrame
    if excel_file.exists():
        df = pd.read_excel(excel_file)
        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    else:
        df = pd.DataFrame([row])

    # Save to Excel
    df.to_excel(excel_file, index=False)

    return render_template("thank_you.html", name=candidate['name'])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
