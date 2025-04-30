import streamlit as st
import requests
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from PIL import Image

# Constants for the FastAPI backend
API_URL = "http://127.0.0.1:8000"  

# Function to register a new user
def register_user(username, password):
    try:
        response = requests.post(f"{API_URL}/register/", json={"username": username, "password": password})
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to register: {e}")
        return None

# Function to log in a user and get the access token
def login_user(username, password):
    try:
        response = requests.post(f"{API_URL}/login", data={"username": username, "password": password})
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to log in: {e}")
        return None

def save_prediction(access_token, prediction_data):
    headers = {"Authorization": f"Bearer {access_token}"}
    try:
        response = requests.post(f"{API_URL}/predictions/", json=prediction_data, headers=headers)
        if response.status_code != 200:
            st.error(f"Failed to save prediction. Status code: {response.status_code}, Response: {response.text}")
            return None
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error saving prediction: {e}")
        return None

# Streamlit UI configuration
st.set_page_config(page_title="Lung Cancer Prediction 🌟", page_icon="🩺")
st.title("Lung Cancer Detection System 🩺")
st.sidebar.title("User Authentication 🔑")

# Sidebar Menu
menu = ["Register ✍️", "Login 🔓", "Make Prediction 🔍"]
choice = st.sidebar.selectbox("Menu", menu)

# User registration
if choice == "Register ✍️":
    st.subheader("Register 👤")
    username = st.text_input("Username", max_chars=30)
    password = st.text_input("Password", type='password')
    if st.button("Register 📋"):
        if username and password:
            response = register_user(username, password)
            if response and response.get("username"):
                st.success("User registered successfully! 🎉")
            else:
                st.error("Registration failed. 😞")

# User login
elif choice == "Login 🔓":
    st.subheader("Login 🔑")
    login_username = st.text_input("Login Username", max_chars=30)
    login_password = st.text_input("Login Password", type='password', key="login_password")
    if st.button("Login 🔐"):
        if login_username and login_password:
            response = login_user(login_username, login_password)
            if response and 'access_token' in response:
                st.session_state.token = response['access_token']
                st.session_state.username = login_username  # Store username for prediction
                st.success("Logged in successfully! 🎉")
            else:
                st.error("Login failed. 😞")

# Prediction section (only if logged in)
elif choice == "Make Prediction 🔍":
    if 'token' in st.session_state:
        # Load the models
        Dense_model = load_model('DenseNet121_lung.h5')
        inceptionv3_model = load_model('InceptionV3_lung.h5')
        Xception_model = load_model('Xception_lung.h5')
        

        # Define image size expected by both models
        IMG_SIZE = (256, 256)

        # Class labels
        class_names = ['lung_aca', 'lung_n', 'lung_scc']

        # Function to preprocess image
        def preprocess_image(uploaded_image):
            img = Image.open(uploaded_image)
            img = img.resize(IMG_SIZE)
            img_array = image.img_to_array(img)
            img_array = np.expand_dims(img_array, axis=0) / 255.0  # Normalize image
            return img_array

        # Function to get prediction
        def predict_image(model, img_array):
            prediction = model.predict(img_array)
            return prediction

        st.markdown("""
            <style>
                .main {
                    background-color: black;  /* Set background color to black */
                    padding: 20px;
                    border-radius: 15px;
                    color: white;  /* Set the default text color to white */
                }
                .stFileUploader > div {
                    background-color: #333;  /* Dark gray background for file uploader */
                    padding: 15px;
                    border-radius: 10px;
                    color: white;  /* Text color for file uploader */
                }
                h1 {
                    color: #1e88e5;  /* Bright blue color for the title */
                    font-weight: bold;
                    text-align: center;
                }
                h3 {
                    color: white;  /* Set header color to white */
                }
                .predict-button {
                    background-color: #42a5f5;  /* Light blue button color */
                    color: black;  /* Text color for button */
                    padding: 12px 20px;
                    font-size: 18px;
                    border-radius: 10px;
                    cursor: pointer;
                    transition: 0.3s;
                }
                .predict-button:hover {
                    background-color: #1e88e5;  /* Darker blue on hover */
                }
                .result-card {
                    background-color: #444;  /* Darker gray for result card */
                    padding: 20px;
                    border-radius: 10px;
                    text-align: center;
                    font-size: 22px;
                    font-weight: bold;
                    color: #76ff03;  /* Bright green color for predicted class */
                }
            </style>
        """, unsafe_allow_html=True)
                # Sidebar Card with Enhanced Styles
        st.sidebar.markdown("""
            <style>
                .sidebar-card {
                    background: linear-gradient(135deg, #222222, #42a5f5);  /* Gradient background */
                    padding: 20px;
                    border-radius: 15px;
                    color: black;  /* Text color for sidebar card */
                    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);  /* Stronger shadow effect */
                    transition: transform 0.4s;  /* Animation effect */
                }
                .sidebar-card:hover {
                    transform: scale(1.02);  /* Scale effect on hover */
                }
                .sidebar-card h3 {
                    color: black;  /* Bright black color for title */
                    text-align: center;
                    margin-bottom: 10px;
                }
                .sidebar-card p {
                    font-size: 14px;
                    text-align: justify;
                    line-height: 1.5;  /* Increased line height for better readability */
                }
                .icon {
                    font-size: 24px;  /* Icon size */
                    margin-right: 8px;  /* Spacing between icon and text */
                }
            </style>
        """, unsafe_allow_html=True)

        # Create the card content with icons
        st.sidebar.markdown("""
            <div class="sidebar-card">
                <h3><span class="icon"></span>🌟Welcome to Lung Cancer Detection🌟</h3>
                <p><span class="icon">🔍</span> Upload a histopathological image to analyze lung cancer types. 
                Our models classify samples into Adenocarcinoma, Squamous Cell Carcinoma, 
                or Normal lung tissue. Use our tools to assist in diagnosis!</p>
            </div>
        """, unsafe_allow_html=True)

        
        st.markdown("""
            <h3>Upload a histopathological image to detect lung cancer using deep learning models 🌟</h3>
            <p style="color: white; font-size: 16px;">
            Choose a file and the prediction model to see if the sample is predicted as Adenocarcinoma, Squamous Cell Carcinoma, or Normal lung tissue. 🤔
            </p>
        """, unsafe_allow_html=True)

        # Image uploader with a neat UI style
        uploaded_image = st.file_uploader("Upload Image (.jpg, .jpeg, .png): 📸", type=["jpg", "jpeg", "png"])

        if uploaded_image is not None:
            st.image(uploaded_image, caption='Uploaded Image 🖼️', use_column_width=True)

            # Preprocess the uploaded image
            img_array = preprocess_image(uploaded_image)

            # # Allow users to select the true class
            # true_class = st.selectbox("True Class (if known):", options=["Unknown 🤷‍♂️", "lung_aca", "lung_n", "lung_scc"])

            # Model selection and prediction button with attractive styling
            model_option = st.selectbox("Choose a prediction model:", ("DenseNet121 🧠", "InceptionV3 🌈","Xception 🌟"))

            if st.button("Predict 🔮", key="predict", use_container_width=True):
                st.markdown('<div class="predict-button">Predicting...</div>', unsafe_allow_html=True)

                # Choose the appropriate model
                if model_option == "DenseNet121 🧠":
                    model = Dense_model  
                elif model_option == "Xception 🌟":
                    model = Xception_model
                else:
                    model = inceptionv3_model  

                # Get the prediction
                prediction = predict_image(model, img_array)  

                # Map the prediction to the corresponding class
                predicted_class = class_names[np.argmax(prediction)]

                # Assuming you want to record the confidence of the prediction
                confidence = float(np.max(prediction))  # Get the maximum confidence score

                # Prepare prediction data to send to FastAPI
                prediction_data = {
                    "username": st.session_state.username,  # Assuming this is a string
                    "predicted_class": predicted_class,  # Should match expected class string
                    # "true_class": true_class if true_class != "Unknown 🤷‍♂️" else None,  # Should be a string or None
                    "model_name": model_option,  # String representing the model name
                    "confidence": confidence  # Float value representing the confidence
                }


                # Save the prediction result
                save_response = save_prediction(st.session_state.token, prediction_data)
                
                # Display the predicted class with a styled card
                st.markdown(f'<div class="result-card">Predicted Class: {predicted_class} 🎉</div>', unsafe_allow_html=True)

                if save_response is not None:
                    st.success("Prediction has been saved in the database successfully! 🎉")

        else:
            st.info("Please upload an image for prediction. 📥")

    else:
        st.info("Please log in to make predictions. 🔒")

# Logout option
if 'token' in st.session_state:
    if st.button("Logout 🚪"):
        del st.session_state.token
        del st.session_state.username  # Clear username on logout
        st.success("Logged out successfully! 👋")
