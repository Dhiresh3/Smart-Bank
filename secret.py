import streamlit as st

if "loop_count" not in st.session_state:
    st.session_state.loop_count = 0
if "show_extra_options" not in st.session_state:
    st.session_state.show_extra_options = False
if "hide_final" not in st.session_state:   
    st.session_state.hide_final = False

st.title("User Interaction Example")
st.header("Make a Choice")

response = st.selectbox("Do you want to proceed?", ["Yes", "No"])

if response == "Yes":
    st.success("Great choice! I am Glad!!!!!.")
    st.session_state.loop_count = 0 
    st.stop()  

elif response == "No":
    st.session_state.loop_count += 1
    st.warning(f"Are you sure about it! (Attempt {st.session_state.loop_count}/10)")

if st.session_state.loop_count < 10 and response == "No":
    new_choice = st.selectbox("Why not?  Select Yes(again) Pls!", ["Yes", "No", "Maybe Yes"])
    st.write(f"You selected: {new_choice}")

    if new_choice in ["Yes", "Maybe Yes"]:
        st.success("Happy moment!")
        st.session_state.loop_count = 0 
        st.stop()

    elif new_choice == "No":
        st.warning("Still refusing?   why? ")
        st.info(" You must be the sun, because every time you appear, the whole world feels warmer")
        st.error(" pls choose yes!")

if st.session_state.loop_count >= 10:
    final_choice = st.selectbox("You've reached the final decision stage. Proceed now?", ["Yes"])
    if final_choice == "Yes":
        st.success("Glad you finally made the decision!")
        st.session_state.loop_count = 0  

N1 = st.selectbox("Would you like to try again?", ["Yes", "Maybe", "No"])
st.write(f"You selected: {N1}")

if N1 in ["Yes", "Maybe"]:
    st.success("Glad to hear that!")

elif N1 == "No":
    st.session_state.show_extra_options = True
    st.error("Alright,  maybe let's have an another try!")
    st.info("Chaand bhi tumse roshni maangta hai, kyunki tumhari chamak sabse alag hai!! abb toh maan ja pls!")

if st.session_state.show_extra_options:
    yot = st.selectbox("Why not?  When you came, I remembered… the moon appeared in the street!", ["Yes", "No"])
    st.write(f"You selected: {yot}")

    if yot == "Yes":
        st.success("Let's reconsider!")
    elif yot == "No":
        st.error("No worries!")
        st.info(" Like the first snowflakes dancing in the wind, you bring a sense of wonder wherever you go!")
        st.warning("pls give positive response!")
        st.session_state.show_extra_options = True

N3 = st.selectbox("are you sure to try again?", ["Change decision (Yes)", "Confirmed No!"])
st.write(f"You selected: {N3}")

if N3 == "Change decision (Yes)":
    final_yes = st.selectbox("Final confirmation—are you ready and now why did you selected yes ?", ["Yes, finally!", "Yes, absolutely!"])
    st.success("Thank God! Finally!")

elif N3 == "Confirmed No!":
    st.session_state.hide_final = True  
    user_comment = st.text_area("Please share your comments before exiting:")
    if user_comment:
        st.write("Thank you for your opinion!")
        st.session_state.loop_count = 0  