import streamlit as st

def main():
    st.title("iCadet Assignment Interface")

    st.header("Please enter your details:")
    lat = st.number_input("Enter your Latitude", format="%.6f")
    lon = st.number_input("Enter your Longitude", format="%.6f")
    major_code = st.text_input("Enter your Major Code")

    submit_button = st.button("Submit")

    if submit_button:
        st.write(f"Latitude: {lat}, Longitude: {lon}, Major Code: {major_code}")

if __name__ == "__main__":
    main()