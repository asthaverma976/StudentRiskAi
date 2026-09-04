# 🎓 StudentRiskAI — Early Academic Risk Detection & Support Platform

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30%2B-FF4B4B?style=for-the-badge&logo=streamlit)
![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-Machine%20Learning-F7931E?style=for-the-badge&logo=scikit-learn)
![Status](https://img.shields.io/badge/Status-Active-success?style=for-the-badge)

**StudentRiskAI** is an institutional-grade, AI-driven academic monitoring and early intervention platform designed to identify students at risk of academic failure or dropout and provide actionable faculty mentorship.

---

## ✨ Key Features

### 👤 Student Workspace
- **Real-Time Risk Analysis**: Multi-factor machine learning evaluation (Attendance, Internals, Assignments, CGPA, Backlogs, Study Hours).
- **Competency Radar Chart**: Visual breakdown of continuous assessment metrics and academic balance.
- **Smart Personalized Recommendations**: Actionable guidance categorized by urgency (Attendance boost, Study schedule, Exam prep).
- **🔮 What-If Simulator**: Interactive parameter tweaking with real-time before/after risk score recalculation.
- **Intervention Tracker**: Live updates on assigned faculty mentor meetings and support plans.

### ⚡ Executive Admin Command Center
- **Executive Overview**: Campus-wide metrics, overall risk distribution pie charts, and risk trend metrics.
- **Student Monitoring**: Real-time filtering, search, and dynamic student risk table.
- **ML Analytics & Model Performance**: ROC Curves, Confusion Matrix, and Feature Importance benchmarks.
- **🚨 Intervention Center**: Generate auto-interventions and assign cases to faculty mentors.
- **Export & Reporting**: Instant CSV exports and summary report generation.

### 👨‍🏫 Faculty Mentor Workspace
- **Assigned Queue**: Direct visibility into students needing support with priority tags.
- **Follow-up Notes Log**: Update meeting logs, action items, and student progress status in real-time.
- **Mentor Playbook**: Guidelines and best practices for academic counseling.

---

## 🚀 Quick Setup & Installation

### 1. Clone the Repository
```bash
git clone https://github.com/asthaverma976/StudentRiskAi.git
cd StudentRiskAi
```

### 2. Create and Activate Virtual Environment
```bash
python -m venv venv

# Windows
.\venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Streamlit Application
```bash
streamlit run app.py
```

The app will be accessible at `http://localhost:8501`.

---

## 🎯 Default Demo Credentials

| Role | Campus ID | Password | Access Level |
|---|---|---|---|
| **Student** | `STU0001` | `Student@123` | Student Dashboard & Simulator |
| **Faculty Mentor** | `MENTOR001` | `Mentor@123` | Mentor Workspace & Follow-ups |
| **Administrator** | `ADMIN001` | `Admin@123` | Full Institutional Command Center |

*(New Students and Mentors can also register directly via the "Create New Account" tab).*

---

## 🛠️ Tech Stack & Architecture
- **Frontend / UI**: Streamlit, Custom Responsive CSS Design System, Google Fonts (`Outfit` & `Plus Jakarta Sans`), Plotly Interactive Charts.
- **Machine Learning**: Random Forest Classifier & Gradient Boosting trained with Scikit-learn.
- **Backend / Database**: SQLite with connection pooling, `@st.cache_data`, and `@st.cache_resource` for optimized responsiveness.

---

## 📄 License
This project is open source and available under the [MIT License](LICENSE).
