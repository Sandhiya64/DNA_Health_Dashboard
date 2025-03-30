import pandas as pd
import joblib

# Load the trained model
model = joblib.load('dna_model.pkl')

# Test on sample data
sample_data = pd.DataFrame({
    'GeneX': [0.5],  # Replace with realistic values
    'GeneY': [1.2],  
    'GeneZ': [0.8]
})

# Make a prediction
prediction = model.predict(sample_data)
print("Predicted Health Risk:", prediction)