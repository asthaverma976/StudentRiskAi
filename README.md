# AI-Based Student Feedback & Complaint Analysis System

A Python + AI/ML college project that automatically analyzes student feedback and
complaints — detecting **sentiment**, **category**, and **priority** — and presents
the results through an admin dashboard.

Built with: **Python, scikit-learn (NLP/ML), NLTK, SQLite, Streamlit, Plotly.**

---

## ✨ Features

- Student feedback/complaint submission form (web UI)
- AI sentiment analysis — Positive / Negative / Neutral
- AI category classification — Faculty / Hostel / Library / Canteen / Examination / Infrastructure
- Rule-assisted priority detection — Low / Medium / High
- SQLite storage of all submissions and results
- Role-protected Admin/Head dashboard with private assigned-feedback views
- Super-admin-managed creation and deletion of Admin/Head accounts
- Optional routing of anonymous student feedback to a selected Admin or Head
- Private no-login complaint tracking with a random receipt code
- Complaint status management — Pending / In Progress / Resolved

---

## 📁 Project Structure

```
student-feedback-ai/
├── app.py                     # Streamlit entry point (home page)
├── database.py                # SQLite table + CRUD helpers
├── preprocessing.py           # Text cleaning / tokenization / stopword removal
├── priority.py                # Rule-assisted priority detection
├── train_model.py             # Trains & saves the sentiment/category models
├── predict.py                 # Loads models, runs the full analysis pipeline
├── build_dataset.py           # Generates the sample labeled training dataset
├── requirements.txt
├── models/
│   ├── sentiment_model.pkl
│   └── category_model.pkl
├── data/
│   └── feedback_dataset.csv
├── pages/
│   ├── student_feedback.py    # Student submission page
│   └── admin_dashboard.py     # Admin analytics/management page
└── README.md
```

---

## 🚀 Setup & Run

1. **Install dependencies** (Python 3.9+ recommended):
   ```bash
   pip install -r requirements.txt
   ```

2. **(Optional) Regenerate the dataset:**
   ```bash
   python build_dataset.py
   ```

3. **Train the ML models** (creates `models/sentiment_model.pkl` and `models/category_model.pkl`):
   ```bash
   python train_model.py
   ```
   This prints accuracy, precision, recall and F1-score for both models.

4. **Run the web app:**
   ```bash
   streamlit run app.py
   ```
   Streamlit will open the app in your browser (default: `http://localhost:8501`).
   Students can use **Student Feedback** without signing in. The **Admin Dashboard**
   requires administrator credentials before any complaint data is loaded or changed.

> The SQLite database file (`feedback.db`) is created automatically on first run.

### Configure admin access

Set the initial super-admin username and password before using the dashboard. Do not
commit these credentials. The configured account is the sole account allowed to
create or delete Admin/Head accounts. For local development, set
environment variables:

```powershell
$env:ADMIN_USERNAME = "your-admin-username"
$env:ADMIN_PASSWORD = "use-a-long-unique-password"
streamlit run app.py
```

For Streamlit deployments, store the same values as `ADMIN_USERNAME` and
`ADMIN_PASSWORD` in the deployment's secrets/environment configuration. The local
`.streamlit/secrets.toml` file is ignored by Git. If neither is configured, the
dashboard fails closed and no feedback data is displayed.

Students do not need an account. They may send feedback to the general office or
select a listed Admin/Head. An Admin can view and update only feedback addressed to
them. Only the configured super-admin (`asthaverma976@gmail.com`) can create or
delete Admin and Head accounts; no other Admin or Head has account-management access.

After submitting feedback, students receive a random `CMP-...` tracking code and
downloadable receipt. Entering that code in **Track an existing complaint** shows
only the submission date, category, priority, and current status.

---

## 🧠 How It Works (Pipeline)

```
Student → Feedback Form → Text Preprocessing → ML/NLP Models →
Sentiment + Category + Priority → Save to Database → Admin Dashboard →
Review/Filter → Update Status → Analytics
```

1. **Preprocessing** (`preprocessing.py`) — lowercases text, strips URLs/punctuation/numbers, tokenizes, and removes stopwords.
2. **Sentiment & Category models** (`train_model.py` / `predict.py`) — TF-IDF vectorization + Logistic Regression (simple, explainable models, as scoped in the PRD).
3. **Priority** (`priority.py`) — combines the predicted sentiment, category, and urgency keywords in the raw text using transparent rules (e.g., a Negative + "exam"/"urgent"/"broken" complaint is flagged High).
4. **Database** (`database.py`) — stores every submission with its analysis + status in SQLite.
5. **Admin Dashboard** (`pages/admin_dashboard.py`) — charts, filters and status updates over the stored data.

---

## 📊 Example

**Input:** *"The computer lab has several non-working computers and our practical exam is next week."*

| Field | Value |
|---|---|
| Sentiment | Negative |
| Category | Infrastructure |
| Priority | High |
| Status | Pending |

---

## 🔮 Future Scope

- Email/notification alerts for high-priority complaints
- Hindi/English multilingual feedback support
- AI-generated short summaries of long complaints
- Duplicate complaint detection
- Trend prediction for recurring college issues
- Additional roles for students and faculty (student feedback is intentionally anonymous today)

---

## 📝 Notes on the Dataset

`data/feedback_dataset.csv` is a small, synthetic (but realistic) labeled dataset
built specifically for this project, covering all 6 categories and 3 sentiments.
For a stronger production model, replace/extend it with real (anonymized) feedback
from your own college and re-run `train_model.py`.
