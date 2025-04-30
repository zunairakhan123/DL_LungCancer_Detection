import streamlit as st
import joblib
import pandas as pd
import numpy as np

# Load saved models and preprocessors
model = joblib.load('best_credit_model.pkl')
scaler = joblib.load('scaler.pkl')
label_encoders = joblib.load('label_encoders.pkl')

# Streamlit UI Styling
st.set_page_config(page_title="Credit Scoring Prediction", layout="centered")
st.markdown(
    """
    <style>
    .main {
        background-color: #f5f7fa;
    }
    h1 {
        color: #2c3e50;
        text-align: center;
    }
    .stButton>button {
        background-color: #3498db;
        color: white;
        border-radius: 10px;
        font-size: 18px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("💳 Credit Scoring Prediction App")
st.write("🔍 Enter financial details below to predict your creditworthiness.")
st.markdown("---")

# Define input fields
def user_input_features():
    features = {}
    st.sidebar.header("User Input Parameters")
    
    # Example categorical features (modify as per dataset)
    categorical_inputs = ['Gender', 'Marital_Status', 'Employment_Type']
    for col in categorical_inputs:
        options = label_encoders[col].classes_
        features[col] = st.sidebar.selectbox(f"{col}", options)
    
    # Example numerical features (modify as per dataset)
    numerical_inputs = ['Annual_Income', 'Loan_Amount', 'Credit_History_Age']
    for col in numerical_inputs:
        features[col] = st.sidebar.number_input(f"{col}", min_value=0.0, format="%f")
    
    return features

input_data = user_input_features()

# Convert categorical inputs
for col in label_encoders:
    if col in input_data:
        input_data[col] = label_encoders[col].transform([input_data[col]])[0]

# Convert to DataFrame
input_df = pd.DataFrame([input_data])

# Standardize numerical features
input_df[numerical_inputs] = scaler.transform(input_df[numerical_inputs])

# Predict button
st.markdown("### Prediction Result")
if st.button("📊 Predict Creditworthiness"):
    prediction = model.predict(input_df)
    result = "✅ Good Credit Score" if prediction[0] == 1 else "❌ Bad Credit Score"
    st.success(f"**Prediction: {result}**")
