import tkinter as tk
from tkinter import messagebox, ttk
from fpdf import FPDF
from sklearn.tree import DecisionTreeClassifier
import pandas as pd
import datetime
import os
import platform
import webbrowser

# --- Dataset for AI Model ---
data = {
    'fever': [1, 1, 0, 1, 1, 1, 1, 0],
    'cough': [1, 1, 0, 1, 0, 1, 1, 0],
    'headache': [1, 0, 1, 1, 1, 0, 1, 1],
    'fatigue': [1, 1, 0, 1, 1, 1, 1, 0],
    'nausea': [0, 0, 0, 0, 1, 0, 0, 1],
    'sore_throat': [1, 0, 0, 0, 0, 1, 1, 0],
    'runny_nose': [1, 1, 0, 0, 0, 0, 1, 0],
    'chest_pain': [0, 0, 0, 0, 0, 1, 0, 0],
    'shortness_of_breath': [0, 0, 0, 0, 0, 1, 0, 0],
    'stiff_neck': [0, 0, 0, 0, 0, 0, 0, 1],
    'chills': [0, 0, 0, 0, 1, 0, 0, 0],
    'rash': [0, 0, 0, 0, 0, 0, 1, 0],
    'loss_of_smell': [0, 0, 0, 0, 0, 0, 0, 0],
    'diagnosis': [
        'Flu', 'Cold', 'Migraine', 'Malaria',
        'Food Poisoning', 'Heart Attack', 'Dengue', 'Meningitis'
    ]
}

df = pd.DataFrame(data)
features = list(df.columns[:-1])
X = df[features]
y = df['diagnosis']
clf = DecisionTreeClassifier()
clf.fit(X, y)

# --- Rules, Remedies & Precautions ---
rules = {
    'Flu': {'fever', 'cough', 'fatigue'},
    'Cold': {'cough', 'fatigue', 'runny_nose'},
    'Migraine': {'headache'},
    'Malaria': {'fever', 'chills', 'fatigue'},
    'Food Poisoning': {'nausea', 'fatigue', 'headache'},
    'Heart Attack': {'chest_pain', 'shortness_of_breath'},
    'Meningitis': {'headache', 'stiff_neck'},
    'Dengue': {'rash', 'fever', 'fatigue'}
}

remedies = {
    'Flu': "Rest, fluids, paracetamol.",
    'Cold': "Rest, decongestants, fluids.",
    'Migraine': "Pain relievers, rest in dark room.",
    'Malaria': "Antimalarial medication.",
    'Food Poisoning': "Hydrate, avoid solid foods.",
    'Heart Attack': "Seek emergency help immediately.",
    'Meningitis': "Urgent medical attention required.",
    'Dengue': "Hydrate, avoid aspirin."
}

precautions = {
    'Flu': "Vaccinate yearly, wash hands.",
    'Cold': "Avoid crowds, sanitize hands.",
    'Migraine': "Manage stress, regular sleep.",
    'Malaria': "Use mosquito nets, avoid stagnant water.",
    'Food Poisoning': "Check food hygiene.",
    'Heart Attack': "Healthy diet, regular exercise.",
    'Meningitis': "Get vaccinated, hygiene.",
    'Dengue': "Prevent mosquito breeding."
}

# --- Core Functions ---
def rule_based_engine(symptoms):
    for disease, required_symptoms in rules.items():
        if required_symptoms.issubset(symptoms):
            return disease
    return "Unknown"

import re

def export_pdf(result_text):
    def remove_emojis(text):
        # Remove emojis and non-latin characters
        return re.sub(r'[^\x00-\x7F]+', '', text)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Medical Expert System Diagnosis Report", ln=True, align='C')
    pdf.ln(10)

    # Clean text
    clean_text = remove_emojis(result_text)

    for line in clean_text.strip().split('\n'):
        pdf.multi_cell(0, 10, line.strip())

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"diagnosis_{timestamp}.pdf"
    pdf.output(filename)

    try:
        if platform.system() == "Windows":
            os.startfile(filename)
        elif platform.system() == "Darwin":
            os.system(f"open '{filename}'")
        else:
            os.system(f"xdg-open '{filename}'")
    except:
        try:
            webbrowser.open_new(f"file://{os.path.abspath(filename)}")
        except:
            messagebox.showerror("Error", "PDF created but could not be opened automatically.")

    messagebox.showinfo("Exported", f"Diagnosis exported as:\n{filename}")


def get_prediction_with_info():
    name = name_entry.get().strip()
    gender = gender_var.get()

    if not name or gender == "Select":
        messagebox.showwarning("Missing Info", "Please enter patient's name and select gender.")
        return

    input_symptoms = {feat: vars_dict[feat].get() for feat in features}
    symptom_set = {k for k, v in input_symptoms.items() if v == 1}
    severity = severity_var.get()

    input_list = [[input_symptoms[feat] for feat in features]]
    ai_pred = clf.predict(input_list)[0]
    rule_based = rule_based_engine(symptom_set)

    result_text = f"""
Patient Name: {name}
Gender: {gender}
Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Selected Symptoms: {', '.join(symptom_set) if symptom_set else 'None'}
Severity: {severity}

🔍 AI Prediction: {ai_pred}
Remedy: {remedies.get(ai_pred, 'N/A')}
Precaution: {precautions.get(ai_pred, 'N/A')}

🧠 Rule-Based Diagnosis: {rule_based}
Remedy: {remedies.get(rule_based, 'N/A')}
Precaution: {precautions.get(rule_based, 'N/A')}

⚠️ Note: Always consult a medical professional for confirmation.
"""

    result_window = tk.Toplevel(root)
    result_window.title("Diagnosis Result")
    result_window.configure(bg="#f4faff")

    tk.Label(result_window, text="Diagnosis Summary", font=("Helvetica", 14, "bold"), bg="#f4faff", fg="#2e4053").pack(pady=10)
    tk.Label(result_window, text=result_text, justify="left", bg="#f4faff", font=("Helvetica", 11)).pack(padx=20, pady=10)
    tk.Button(result_window, text="Export to PDF", command=lambda: export_pdf(result_text), bg="#4CAF50", fg="white").pack(pady=10)

def reset_all():
    for var in vars_dict.values():
        var.set(0)
    name_entry.delete(0, tk.END)
    gender_var.set("Select")
    severity_var.set("Mild")

# --- GUI ---
root = tk.Tk()
root.title("Advanced Medical Expert System")
root.geometry("400x750")
root.configure(bg="#e6f2ff")

# Patient Info
tk.Label(root, text="Patient Details", font=("Helvetica", 16, "bold"), bg="#e6f2ff").pack(pady=10)

tk.Label(root, text="Name:", bg="#e6f2ff", font=("Helvetica", 12)).pack(pady=(5, 0))
name_entry = tk.Entry(root, font=("Helvetica", 11))
name_entry.pack(pady=(0, 5))

tk.Label(root, text="Gender:", bg="#e6f2ff", font=("Helvetica", 12)).pack()
gender_var = tk.StringVar(value="Select")
gender_menu = ttk.Combobox(root, textvariable=gender_var, values=["Male", "Female", "Other"])
gender_menu.pack(pady=(0, 10))

# Symptoms Section
tk.Label(root, text="Select Your Symptoms", font=("Helvetica", 16, "bold"), bg="#e6f2ff").pack(pady=10)

vars_dict = {feat: tk.IntVar() for feat in features}
for feat in features:
    text = feat.replace("_", " ").capitalize()
    tk.Checkbutton(root, text=text, variable=vars_dict[feat], bg="#e6f2ff", font=("Helvetica", 11)).pack(anchor='w', padx=30)

# Severity
tk.Label(root, text="Select Severity Level", bg="#e6f2ff", font=("Helvetica", 12, "bold")).pack(pady=10)
severity_var = tk.StringVar(value="Mild")
ttk.Combobox(root, textvariable=severity_var, values=["Mild", "Moderate", "Severe"]).pack()

# Buttons
tk.Button(root, text="Get Diagnosis", command=get_prediction_with_info, bg="#007acc", fg="white", font=("Helvetica", 12, "bold")).pack(pady=20)
tk.Button(root, text="Reset All", command=reset_all, bg="#e74c3c", fg="white", font=("Helvetica", 11)).pack(pady=5)

root.mainloop()
