from flask import Flask, render_template, request, redirect, url_for
import json
import uuid
from datetime import datetime

app = Flask(__name__)
DATA_FILE = "exams.json"

DAYS = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato"]
MAX_HOURS_PER_DAY = 5

# -------------------------
# JSON helpers
# -------------------------
def load_exams():
    try:
        with open(DATA_FILE, "r") as f:
            exams = json.load(f)
        # Assicura campi minimi
        for exam in exams:
            exam.setdefault("id", str(uuid.uuid4()))
            exam.setdefault("cfu", 0)
            exam.setdefault("planned_hours", 0)
            exam.setdefault("hours_completed", 0)
            exam.setdefault("difficulty", 1)
            exam.setdefault("exam_date", str(datetime.today().date()))
            exam.setdefault("progress", 0)
        return exams
    except FileNotFoundError:
        return []

def save_exams(exams):
    with open(DATA_FILE, "w") as f:
        json.dump(exams, f, indent=4)

# -------------------------
# Processamento esami
# -------------------------
def process_exams(exams):
    today = datetime.today().date()
    for exam in exams:
        # Calcolo giorni mancanti
        try:
            exam_date = datetime.strptime(exam.get("exam_date", ""), "%Y-%m-%d").date()
        except:
            exam_date = today
        exam["days_left"] = max(0, (exam_date - today).days)
        
        # Ore pianificate
        exam["planned_hours"] = exam.get("cfu", 0) * 2.5
        
        # Ore completate
        exam["hours_completed"] = exam["planned_hours"] * (exam.get("progress", 0) / 100)
        
        # Progress calcolato
        exam["progress"] = int((exam["hours_completed"] / exam["planned_hours"]) * 100) if exam["planned_hours"] > 0 else 0
        
        # Esame imminente
        exam["imminent"] = exam["days_left"] <= 7
    return exams, {}  # stats opzionali

# -------------------------
# Piano settimanale
# -------------------------
def generate_weekly_plan(exams):
    plan = {day: [] for day in DAYS}
    remaining_hours = {exam["name"]: exam.get("planned_hours", 0) - exam.get("hours_completed", 0) for exam in exams}

    for day in DAYS:
        hours_left_today = MAX_HOURS_PER_DAY
        sorted_exams = sorted(
            exams,
            key=lambda e: ((remaining_hours[e["name"]] / max(e["days_left"], 1)) * e.get("difficulty", 1)),
            reverse=True
        )
        for exam in sorted_exams:
            if hours_left_today <= 0:
                break
            name = exam["name"]
            if remaining_hours[name] <= 0:
                continue
            max_daily_exam_hours = 3 if exam["imminent"] else 2
            study_hours = min(remaining_hours[name], max_daily_exam_hours, hours_left_today)
            if study_hours > 0:
                plan[day].append({"exam": name, "hours": study_hours})
                remaining_hours[name] -= study_hours
                hours_left_today -= study_hours
    return plan

# -------------------------
# ROUTES
# -------------------------

@app.route("/")
def home():
    return redirect(url_for("dashboard"))

# -------------------------
# DASHBOARD - solo welcome
# -------------------------
@app.route("/dashboard")
def dashboard():
    exams, _ = process_exams(load_exams())
    return render_template("dashboard.html", exams=exams)

# -------------------------
# ESAMI - lista con progress bar e form aggiornamento
# -------------------------
@app.route("/exams")
def exams_page():
    exams, _ = process_exams(load_exams())
    return render_template("exams.html", exams=exams)

# -------------------------
# AGGIUNGI ESAME
# -------------------------
@app.route("/add_exam", methods=["GET", "POST"])
def add_exam():
    if request.method == "POST":
        name = request.form.get("name")
        cfu = int(request.form.get("cfu"))
        difficulty = int(request.form.get("difficulty"))
        exam_date = request.form.get("exam_date")

        exam = {
            "id": str(uuid.uuid4()),
            "name": name,
            "cfu": cfu,
            "difficulty": difficulty,
            "exam_date": exam_date,
            "hours_completed": 0,
            "planned_hours": cfu * 2.5,
            "progress": 0
        }

        exams = load_exams()
        exams.append(exam)
        save_exams(exams)
        return redirect(url_for("exams_page"))

    return render_template("add_exam.html")

# -------------------------
# PIANO SETTIMANALE
# -------------------------
@app.route("/schedule")
def schedule_page():
    exams, _ = process_exams(load_exams())
    weekly_plan = generate_weekly_plan(exams)
    return render_template("schedule.html", weekly_plan=weekly_plan)

# -------------------------
# STATISTICHE
# -------------------------
@app.route("/stats")
def stats_page():
    exams, _ = process_exams(load_exams())
    return render_template("stats.html", exams=exams)

# -------------------------
# AGGIORNA PROGRESS
# -------------------------
@app.route("/update_progress", methods=["POST"])
def update_progress():
    exams = load_exams()
    exam_id = request.form.get("exam_id")
    added_hours = float(request.form.get("hours", 0))

    for exam in exams:
        if exam["id"] == exam_id:
            # aggiungo ore studiate
            exam["hours_completed"] += added_hours

            # limite: non superare le ore pianificate
            if exam["hours_completed"] > exam["planned_hours"]:
                exam["hours_completed"] = exam["planned_hours"]

            # ricalcolo progresso
            exam["progress"] = int(
                (exam["hours_completed"] / exam["planned_hours"]) * 100
            ) if exam["planned_hours"] > 0 else 0

            break

    save_exams(exams)
    return redirect(url_for("exams_page"))



# -------------------------
if __name__ == "__main__":
    app.run(debug=True)
