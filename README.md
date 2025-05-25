# Hackathon-1337AI: 🎓 Intelligent Pre-Selection AI Agent for Hackathon Candidate Screening

An intelligent web-based system to streamline the process of receiving applications, ranking candidates using AI, and selecting the top submissions.

---

## 🔍 Project Overview

This AI-driven system helps HR departments, universities, and event organizers manage a large number of candidate submissions quickly and efficiently.

It includes:
- ✅ A submission **form**
[submission form](app/images/img1.png)
- 📊 An **admin panel** to view and rank all candidates
[admin panel](app/images/img2.png)
- 🏆 A **selection interface** to pick top applicants based on their scores
[election interface](app/images/img3.png)

---

## 📦 Project Structure (Visual Tree)
```bash
project_root/
├── app/
│   ├── style.css
│   ├── images/
│   │   ├── form_preview.png
│   │   ├── admin_preview.png
│   │   ├── accepted_preview.png
│   │   └── project_tree.png
│   ├── templates/
│   │   ├── form.html
│   │   ├── admin.html
│   │   └── accepted.html
│   ├── submissions.xlsx
│   ├── main.py
│   ├── ai_scoring.py
│   ├── githubsearch.py
│   └── ocr.py
├── docker-compose.yml
├── Dockerfile
└── README.md
