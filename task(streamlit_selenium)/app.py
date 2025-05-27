import streamlit as st
import pandas as pd
from pathlib import Path
import sys
import os


BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

try:
    import backend_script as backend
except ImportError as e:
    st.error(f"Failed to import backend module: {str(e)}. Ensure backend_script.py is in {BASE_DIR}.")
    st.stop()

st.title("Company Details")


image_path = BASE_DIR / "ci.png"
if image_path.exists():
    st.image(str(image_path), width=650)
else:
    st.warning("Image 'ci.png' not found in the app directory.")

query = st.text_input("Enter the search term", "company")

data_path = BASE_DIR / "company_data.csv"
if data_path.exists():
    try:
        data = pd.read_csv(data_path)
        if data.empty:
            st.warning("Existing company_data.csv is empty.")
        else:
            st.subheader("Current Data")
            st.dataframe(data)
    except Exception as e:
        st.error(f"Error reading company_data.csv: {str(e)}")
else:
    st.info("No existing company_data.csv found. Click 'Start Search' to fetch data.")

if st.button("Start Search"):
    if not query.strip():
        st.error("Please enter a valid search term.")
    else:
        with st.spinner("Fetching data..."):
            try:
                data = backend.call(query)
                df = pd.DataFrame(data)
                if df.empty:
                    st.warning(f"No data retrieved for query '{query}'. Try a different search term (e.g., 'restaurant').")
                else:
                    df.to_csv(data_path, index=False)
                    st.success("Data retrieved and saved successfully!")
                    st.subheader("Search Results")
                    st.dataframe(df)
            except Exception as e:
                st.error(f"Error fetching data: {str(e)}")
                if "WebDriver" in str(e):
                    st.error("WebDriver issue detected. Ensure Microsoft Edge is installed and try running the app as administrator. Alternatively, download the Edge WebDriver manually and place it in the project directory.")