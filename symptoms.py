import pytesseract
from PIL import Image
import tkinter as tk
from tkinter import filedialog
import re

def extract_symptoms_from_text(text):
    # List of symptoms to look for
    symptoms_list = [
        'cough', 'fever', 'shortness of breath', 'chest pain',
        'fatigue', 'rapid breathing', 'nausea', 'headache'
    ]
    
    # Convert text to lowercase for case-insensitive matching
    text = text.lower()
    
    # Find all symptoms in the text
    found_symptoms = [symptom for symptom in symptoms_list if symptom in text]
    
    return found_symptoms

def select_image():
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    
    file_path = filedialog.askopenfilename(
        title="Select Report Image",
        filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp")]
    )
    
    return file_path

def main():
    # Let user select image
    image_path = select_image()
    
    if not image_path:
        print("No image selected")
        print("Extracted symptoms from image: []")
        print("Image path: None")
        return
    
    try:
        # Open and process the image
        image = Image.open(image_path)
        
        # Extract text from image
        text = pytesseract.image_to_string(image)
        
        # Extract symptoms from text
        symptoms = extract_symptoms_from_text(text)
        
        print(f"Extracted symptoms from image: {symptoms}")
        print(f"Image path: {image_path}")
        
    except Exception as e:
        print(f"Error processing image: {e}")
        print("Extracted symptoms from image: []")
        print(f"Image path: {image_path}")

if __name__ == "__main__":
    main()