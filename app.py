import pickle
import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
from utils.fertilizer import fertilizer_dict
import os
import cv2
from PIL import Image
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model


# loading the saved models

classifier = load_model('Trained_model.h5')

crop_recommendation_model = pickle.load(open('Crop_Recommendation.pkl', 'rb'))


def fert_recommend(crop_name,N_filled,P_filled,K_filled):

    df = pd.read_csv('Data/Crop_NPK.csv')

    N_desired = df[df['Crop'] == crop_name]['N'].iloc[0]
    P_desired = df[df['Crop'] == crop_name]['P'].iloc[0]
    K_desired = df[df['Crop'] == crop_name]['K'].iloc[0]

    n = N_desired- N_filled
    p = P_desired - P_filled
    k = K_desired - K_filled

    if n < 0:
        key1 = "NHigh"
    elif n > 0:
        key1 = "Nlow"
    else:
        key1 = "NNo"

    if p < 0:
        key2 = "PHigh"
    elif p > 0:
        key2 = "Plow"
    else:
        key2 = "PNo"

    if k < 0:
        key3 = "KHigh"
    elif k > 0:
        key3 = "Klow"
    else:
        key3 = "KNo"

    abs_n = abs(n)
    abs_p = abs(p)
    abs_k = abs(k)

    response1 = str(fertilizer_dict[key1])
    response2 = str(fertilizer_dict[key2])
    response3 = str(fertilizer_dict[key3])

    result = response1 + "\n" + response2 + "\n" + response3

    return result


# Define the pest classes
pest_classes = ['aphids', 'armyworm', 'beetle', 'bollworm', 'earthworm', 'grasshopper', 'mites', 'mosquito', 'sawfly', 'stem borer']

# Function to preprocess image for model prediction
def preprocess_image(image):
    resized_image = cv2.resize(image, (64, 64))
    img_array = np.array(resized_image)
    img_array_expanded = np.expand_dims(img_array, axis=0)
    img_array_normalized = img_array_expanded / 255.0
    return img_array_normalized

# Function to run the webcam capture
def run_webcam():
    video_capture = cv2.VideoCapture(0)

    if st.button('Capture Image'):
        _, frame = video_capture.read()
        st.image(frame, channels="BGR", caption="Captured Image", use_column_width=True)

        # Preprocess the captured image
        processed_image = preprocess_image(frame)

        # Display the Predict button
        if st.button('Predict'):
            # Make predictions using the model
            predictions = classifier.predict(processed_image)

            # Display the results
            display_results(predictions)

# Function to run the image upload
def run_upload():
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_column_width=True)

        # Preprocess the uploaded image
        img_array = np.array(image)
        processed_image = preprocess_image(img_array)

        # Display the Predict button
        if st.button('Predict'):
            # Make predictions using the model
            predictions = classifier.predict(processed_image)

            # Display the results
            display_results(predictions)


# Function to display the model predictions
def display_results(predictions):
    st.header("Model Predictions")
    
    max_prob_index = np.argmax(predictions)
    predicted_class = pest_classes[max_prob_index]
    st.write(f"Predicted Class: '{predicted_class}' with {predictions[0][max_prob_index] * 100:.2f}% Probability")

# sidebar for navigation
with st.sidebar:
    
    selected = option_menu('Digital Farmhand',
                          
                          ['Crop Recommendation',
                           'Fertilizer Recommendation',
                           'Pest Prediction'],
                          default_index=0)
    
    
# Crop recommendation Page
if (selected == 'Crop Recommendation'):
    
    # page title
    st.title('Crop Recommendation')
    
    
    # getting the input data from the user
    col1, col2, col3 = st.columns(3)
    
    with col1:
        N = st.text_input('Nitrogen')
        
    with col2:
        P = st.text_input('Phosphorous')
    
    with col3:
        K = st.text_input('Potassium')
    
    with col1:
        ph = st.text_input('pH')
    
    with col2:
        rainfall = st.text_input('Rainfall')
    
    with col3:
        temperature = st.text_input('Temperature')
    
    with col2:
        humidity = st.text_input('Humidity')
    
    
    # code for Prediction
    crop_recommend = ''
    
    # creating a button for Prediction
    
    if st.button('Recommended Crop'):

        input_data_crop = [[N, P, K, temperature, humidity, ph, rainfall]]
        input_data_crop = [[float(val) for val in row] for row in input_data_crop]
        print(input_data_crop)

        crop_recommendation = crop_recommendation_model.predict(input_data_crop)
        result = crop_recommendation[0]

        crop_recommend = 'You should grow '+ result + ' in your farm.'
        
    st.success(crop_recommend)




# Fertilization prediction
if (selected == 'Fertilizer Recommendation'):
    
    # page title
    st.title('Fertilizer Recommendation')
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        crop_name_input = st.text_input('Crop name')
        
    with col2:
        N_input = st.text_input('Nitrogen')
        
    with col3:
        P_input = st.text_input('Phosphorous')
        
    with col4:
        K_input = st.text_input('Potassium')

    crop_name = str(crop_name_input)

    if N_input:
        try:
            N_filled = int(N_input)
        except ValueError:
            st.warning("Please enter a valid integer for Nitrogen.") 


    if P_input:
        try:
            P_filled = int(P_input)
        except ValueError:
            st.warning("Please enter a valid integer for Phosphorous.")


    if K_input:
        try:
            K_filled = int(K_input)
        except ValueError:
            st.warning("Please enter a valid integer for Potassium.")     
     
    # code for Prediction
    fertilizer_recommend = ''
    
    # creating a button for Prediction
    
    if st.button('Recommend Fertilizers'):

        fertilizer_recommend = fert_recommend(crop_name, N_filled, P_filled, K_filled)
        
    st.markdown(fertilizer_recommend)
        
    
    

# Pest Prediction Page
if (selected == "Pest Prediction"):
    
    # page title
    st.title("Pest Prediction")

    # Choose input method: Webcam or Upload
    input_method = st.radio("Select input method:", ('Upload', 'Webcam'))

    if input_method == 'Upload':
        run_upload()

    elif input_method == 'Webcam':
        run_webcam()
    
