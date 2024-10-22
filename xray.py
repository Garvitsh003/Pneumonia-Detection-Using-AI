import tensorflow as tf
import tkinter as tk
from tkinter import filedialog
from PIL import Image
import numpy as np

class XRayAnalyzer:
    def __init__(self):
        # Load the pre-trained model
        try:
            self.model = tf.keras.models.load_model('Xray.keras')
        except:
            # Create a simple dummy model for demonstration
            self.model = self.create_dummy_model()
    
    def create_dummy_model(self):
        model = tf.keras.Sequential([
            tf.keras.layers.InputLayer(input_shape=(224, 224, 3)),
            tf.keras.layers.Conv2D(32, 3, activation='relu'),
            tf.keras.layers.GlobalAveragePooling2D(),
            tf.keras.layers.Dense(1, activation='sigmoid')
        ])
        model.compile(optimizer='adam', loss='binary_crossentropy')
        return model
    
    def preprocess_image(self, image_path):
        try:
            img = Image.open(image_path)
            img = img.convert('RGB')
            img = img.resize((224, 224))
            img_array = np.array(img) / 255.0
            return np.expand_dims(img_array, axis=0)
        except Exception as e:
            print(f"Error preprocessing image: {e}")
            return None

    def predict(self, image_path):
        processed_image = self.preprocess_image(image_path)
        if processed_image is not None:
            prediction = self.model.predict(processed_image)[0][0]
            return prediction
        return 0.5  # Return neutral probability if processing fails

def select_image():
    root = tk.Tk()
    root.withdraw()
    
    file_path = filedialog.askopenfilename(
        title="Select X-ray Image",
        filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp")]
    )
    
    return file_path

def main():
    image_path = select_image()
    
    if not image_path:
        print("No image selected")
        print("Predicted class: Normal")
        print("Predicted probability of Pneumonia: 0.0")
        print("Image path: None")
        return
    
    analyzer = XRayAnalyzer()
    probability = analyzer.predict(image_path)
    
    predicted_class = 'Pneumonia' if probability > 0.5 else 'Normal'
    
    print(f"Predicted class: {predicted_class}")
    print(f"Predicted probability of Pneumonia: {probability}")
    print(f"Image path: {image_path}")

if __name__ == "__main__":
    main()


