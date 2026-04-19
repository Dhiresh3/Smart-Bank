import streamlit as st
import pandas as pd
import pickle
import numpy as np
import os

# Load dataset
df = pd.read_csv("C:/Users/dhire/OneDrive/Desktop/Coding1/laptop_price.csv", encoding="ISO-8859-1")

# Check if model file exists
if not os.path.exists('pipe.pkl'):
    st.error("🚫 Model file 'pipe.pkl' not found. Please train and save the model first.")
    st.stop()

# Load trained pipeline
with open('pipe.pkl', 'rb') as f:
    pipe = pickle.load(f)

# App title
st.title("💻 Laptop Price Predictor")

# User inputs
company = st.selectbox("Brand", df['Company'].unique(), index=4)
type = st.selectbox("Type", df['TypeName'].unique(), index=1)
ram = st.selectbox("Ram (GB)", [2, 4, 6, 8, 12, 16, 32, 64, 128], index=3)
cpu = st.selectbox("Processor", df['Cpu'].unique())
gpu = st.selectbox("GPU", df['Gpu'].unique())
os = st.selectbox("Operating System", df['OpSys'].unique(), index=2)
weight = st.number_input("Laptop Weight (KG)", min_value=1.0, max_value=4.8, value=2.0, step=0.2)
touchscreen = st.selectbox("Touchscreen", ['Yes', 'No'])
ips = st.selectbox("IPS Display", ['Yes', 'No'])
screen_size = st.number_input("Screen Size (in Inches, diagonal):", min_value=10.0, value=15.6, step=0.15)
resolution = st.selectbox("Screen Resolution", [
    "2500x1600", "1440x900", "1920x1080", "2880x1800", "1366x768",
    "2304x1440", "3200x1800", "1920x1200", "2256x1504", "1600x900", "2736x1824"
], index=2)

# Prediction trigger
if st.button("Predict Price"):
    try:
        # Calculate PPI
        x_res = int(resolution.split('x')[0])
        y_res = int(resolution.split('x')[1])
        ppi = ((x_res**2 + y_res**2) ** 0.5) / screen_size

        # Flags
        touchscreen_flag = 1 if touchscreen == 'Yes' else 0
        ips_flag = 1 if ips == 'Yes' else 0

        # Create input DataFrame
        query = pd.DataFrame([[company, type, ram, cpu, gpu, os, weight, touchscreen_flag, ips_flag, ppi]],
                             columns=['Company', 'TypeName', 'Ram', 'Cpu', 'Gpu', 'OpSys', 'Weight',
                                      'Touchscreen', 'Ips', 'PPI'])

        # Predict and display
        prediction = np.exp(pipe.predict(query))[0]
        st.balloons()
        st.success(f"💰 Estimated Laptop Price: ₹{round(prediction):,}")
        st.caption("Created with passion by Dhiresh 💡")

    except Exception as e:
        st.error(f"⚠️ Something went wrong: {e}")