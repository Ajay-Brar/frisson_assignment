import streamlit as st
import pandas as pd



st.title("Company Details")
st.image("ci.png",width = 650)
st.sidebar.button("Home")

data = pd.read_csv("C:\\Users\\Ajay Brar\\Desktop\\Selenium\\backend\\company_data.csv")
if st.checkbox("Company data"):
    st.table(data.head(21))

st.button("submit")