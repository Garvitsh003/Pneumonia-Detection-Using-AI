import subprocess
import json
import os
from pgmpy.models import BayesianNetwork
from pgmpy.factors.discrete import TabularCPD
from pgmpy.inference import VariableElimination
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk

# Define symptom probabilities with clinical accuracy
SYMPTOM_PROBS = {
    'cough': (0.90, 0.20),
    'fever': (0.85, 0.15),
    'shortness of breath': (0.80, 0.10),
    'chest pain': (0.70, 0.08),
    'fatigue': (0.70, 0.20),
    'rapid breathing': (0.60, 0.05),
    'nausea': (0.20, 0.15),
    'headache': (0.15, 0.12),
}

DEFAULT_SYMPTOM_PROB = (0.30, 0.15)

class PneumoniaDiagnosisSystem:
    def __init__(self):
        self.BASE_PNEUMONIA_PROB = 0.05
        self.XRAY_SENSITIVITY = 0.95
        self.XRAY_SPECIFICITY = 0.98

    def calculate_probability(self, symptoms, xray_positive, xray_probability):
        prob = self.BASE_PNEUMONIA_PROB
        
        if xray_positive and symptoms:  # Case 1
            prob = min(0.95, xray_probability * (1 + (len(symptoms) / 10)))
            
        elif xray_positive and not symptoms:  # Case 2
            prob = min(0.70, xray_probability * 0.8)
            
        elif not xray_positive and symptoms:  # Case 3
            symptom_weight = sum(SYMPTOM_PROBS.get(s, DEFAULT_SYMPTOM_PROB)[0] 
                               for s in symptoms) / len(symptoms)
            prob = min(0.30, symptom_weight * 0.4)
            
        else:  # Case 4
            prob = max(0.01, self.BASE_PNEUMONIA_PROB * 0.5)

        return prob * 100

    def create_bayesian_network(self, symptoms, xray_probability):
        model = BayesianNetwork([('Pneumonia', 'X-ray')] + 
                               [('Pneumonia', symptom) for symptom in symptoms])

        cpd_pneumonia = TabularCPD(variable='Pneumonia', variable_card=2,
                                  values=[[1 - self.BASE_PNEUMONIA_PROB], 
                                         [self.BASE_PNEUMONIA_PROB]])

        cpd_xray = TabularCPD(variable='X-ray', variable_card=2,
                             values=[[self.XRAY_SPECIFICITY, 1 - self.XRAY_SENSITIVITY],
                                    [1 - self.XRAY_SPECIFICITY, self.XRAY_SENSITIVITY]],
                             evidence=['Pneumonia'],
                             evidence_card=[2])

        model.add_cpds(cpd_pneumonia, cpd_xray)

        for symptom in symptoms:
            probs = SYMPTOM_PROBS.get(symptom, DEFAULT_SYMPTOM_PROB)
            cpd_symptom = TabularCPD(
                variable=symptom, variable_card=2,
                values=[[1 - probs[1], 1 - probs[0]],
                        [probs[1], probs[0]]],
                evidence=['Pneumonia'],
                evidence_card=[2])
            model.add_cpds(cpd_symptom)

        return model

def run_symptoms_script():
    result = subprocess.run(['python', 'symptoms.py'], capture_output=True, text=True)
    output = result.stdout.strip()
    
    symptoms = []
    report_image_path = None
    for line in output.split('\n'):
        if line.startswith("Extracted symptoms from image:"):
            symptoms_str = line.split(': ')[1]
            symptoms = eval(symptoms_str)
        elif line.startswith("Image path:"):
            report_image_path = line.split(': ')[1]
    
    return symptoms, report_image_path

def run_xray_script():
    result = subprocess.run(['python', 'xray.py'], capture_output=True, text=True)
    output = result.stdout.strip()
    
    prediction = None
    probability = None
    xray_image_path = None
    for line in output.split('\n'):
        if line.startswith("Predicted class:"):
            prediction = line.split(': ')[1]
        elif line.startswith("Predicted probability of Pneumonia:"):
            probability = float(line.split(': ')[1])
        elif line.startswith("Image path:"):
            xray_image_path = line.split(': ')[1]
    
    return prediction, probability, xray_image_path

def create_gui(report_image_path, xray_image_path, pneumonia_probability, symptoms, xray_positive):
    window = tk.Tk()
    window.title("Pneumonia Diagnosis Report")

    report_frame = tk.Frame(window)
    report_frame.pack(side=tk.LEFT, padx=10, pady=10)

    xray_frame = tk.Frame(window)
    xray_frame.pack(side=tk.LEFT, padx=10, pady=10)

    result_frame = tk.Frame(window)
    result_frame.pack(side=tk.LEFT, padx=10, pady=10)

    if report_image_path and os.path.exists(report_image_path):
        try:
            report_image = Image.open(report_image_path)
            report_image = report_image.resize((300, 300), Image.Resampling.LANCZOS)
            report_photo = ImageTk.PhotoImage(report_image)
            report_label = tk.Label(report_frame, image=report_photo)
            report_label.image = report_photo
            report_label.pack()
            tk.Label(report_frame, text="Report Image").pack()
        except Exception as e:
            tk.Label(report_frame, text="Error loading report image").pack()

    if xray_image_path and os.path.exists(xray_image_path):
        try:
            xray_image = Image.open(xray_image_path)
            xray_image = xray_image.resize((300, 300), Image.Resampling.LANCZOS)
            xray_photo = ImageTk.PhotoImage(xray_image)
            xray_label = tk.Label(xray_frame, image=xray_photo)
            xray_label.image = xray_photo
            xray_label.pack()
            tk.Label(xray_frame, text="X-ray Image").pack()
        except Exception as e:
            tk.Label(xray_frame, text="Error loading X-ray image").pack()

    case_number = (2 if xray_positive and not symptoms else
                  1 if xray_positive and symptoms else
                  3 if not xray_positive and symptoms else 4)
    
    risk_level = ("HIGH" if pneumonia_probability >= 70 else
                 "MODERATE" if pneumonia_probability >= 30 else "LOW")
    
    case_descriptions = {
        1: "X-ray Positive with Symptoms",
        2: "X-ray Positive without Symptoms",
        3: "X-ray Negative with Symptoms",
        4: "X-ray Negative without Symptoms"
    }

    tk.Label(result_frame, text="Pneumonia Risk Assessment",
             font=("Arial", 16, "bold")).pack(pady=5)
    tk.Label(result_frame, text=f"{case_descriptions[case_number]}",
             font=("Arial", 12, "bold")).pack(pady=5)
    tk.Label(result_frame, text=f"Risk Level: {risk_level}",
             font=("Arial", 14)).pack(pady=5)
    tk.Label(result_frame, text=f"Probability: {pneumonia_probability:.1f}%",
             font=("Arial", 14)).pack(pady=5)

    if symptoms:
        tk.Label(result_frame, text="Symptoms Present:",
                 font=("Arial", 12)).pack(pady=5)
        for symptom in symptoms:
            tk.Label(result_frame, text=f"• {symptom}",
                     font=("Arial", 10)).pack(pady=1)

    window.mainloop()

def main():
    diagnosis_system = PneumoniaDiagnosisSystem()
    
    symptoms, report_image_path = run_symptoms_script()
    xray_prediction, xray_probability, xray_image_path = run_xray_script()
    
    print(f"Symptoms detected: {symptoms}")
    print(f"X-ray prediction: {xray_prediction}")
    print(f"X-ray probability: {xray_probability:.4f}")

    xray_positive = xray_prediction == 'Pneumonia'
    
    pneumonia_probability = diagnosis_system.calculate_probability(
        symptoms, xray_positive, xray_probability)

    print(f"Final Pneumonia Probability: {pneumonia_probability:.2f}%")
    
    create_gui(report_image_path, xray_image_path, pneumonia_probability,
              symptoms, xray_positive)

if __name__ == "__main__":
    main()