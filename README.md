# 🎓 Hackathon-1337AI: Intelligent Pre-Selection AI Agent for Hackathon Candidate Screening

An intelligent web-based system to streamline the process of receiving applications, ranking candidates using AI, and selecting the top submissions.

---

## 🔍 Project Overview

This AI-driven system helps HR departments, universities, and event organizers manage large volumes of candidate submissions quickly and efficiently.

### It includes:
- ✅ A **Submission Form** to collect candidate details  
  ![Form Preview](app/images/form_preview.png)

- 📊 An **Admin Panel** to view and rank all candidates  
  ![Admin Panel](app/images/admin_preview.png)

- 🏆 A **Selection Interface** to display top applicants based on scores  
  ![Selection Interface](app/images/accepted_preview.png)

---

## 🎥 Demo Video

[![Watch the Demo Video](https://img.youtube.com/vi/your_video_id_here/0.jpg)](https://www.youtube.com/watch?v=your_video_id_here)

---

## 📦 Project Structure

![Project Tree](app/images/project_tree.png)

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
