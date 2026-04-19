import streamlit as st
import math

st.title("Maths (Areas)")

opt = st.radio("Choose any one!", ["Area of Square", "Area of Rectangle", "Area of Circle", "Area of Sphere"])

if opt == "Area of Square":
    side = st.number_input("Enter The Side:", value=0.0)
    if st.button("Calculate"):
        st.success(f"Area of Square is: {side ** 2}")
        with st.expander("See Explanation"):
            st.info("Area of Square is A = side²")

elif opt == "Area of Rectangle":
    length = st.number_input("Enter length:", value=0.0)
    width = st.number_input("Enter width:", value=0.0)
    if st.button("Calculate"):
        st.success(f"The area of the rectangle is {length * width}")
        with st.expander("See Explanation"):
            st.info("Area of a rectangle formula is: length × width")

elif opt == "Area of Circle":
    radius = st.number_input("Enter The Radius:", value=0.0)
    if st.button("Calculate"):
        st.success(f"Area of Circle is: {math.pi * radius ** 2}")
        with st.expander("See Explanation"):
            st.info("Area of a Circle is calculated using the formula: π × Radius²")

elif opt == "Area of Sphere":
    radius = st.number_input("Enter The Radius:", value=0.0)
    if st.button("Calculate"):
        st.success(f"Area of Sphere is: {4 * math.pi * radius ** 2}")
        with st.expander("See Explanation"):
            st.info("Area of Sphere formula is A = 4π × Radius²")

st.caption("Built with 💡 by Dhiresh using Streamlit")