import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup
import requests

def collect_excel():
    # Instructions
    with st.expander("Instructions"):
        st.markdown("Coming soon...")

    # Request to upload an excel file
    file = st.file_uploader("Select your file", type=("xlsx", "csv"))
    if file:
        if file.name.endswith("xlsx"):
            return pd.read_excel(file, engine="openpyxl")
        elif file.name.endswith("csv"):
            return pd.read_csv(file)
    else:
        return pd.DataFrame()

def collect_google():
    # Instructions
    with st.expander("Instructions"):
        st.markdown("Coming soon...")
    # Link collection
    link = st.text_input("Enter a link")
    # Collect actual data
    if len(link) > 0 and link.endswith("pubhtml"):
        page = requests.get(link).text
        soup = BeautifulSoup(page, "html.parser")
        # List that holds each row as a list
        input_data = []
        for row in soup.find_all('tr'):
            # List of elements in the row
            row_data = []
            for element in row.find_all('td'):
                row_data.append(element.get_text())
            input_data.append(row_data)
        column_names = [str(name) for name in input_data[1]]
        # Convert list to DataFrame and return
        return pd.DataFrame(input_data[2:], columns=column_names)
    elif len(link) >0 and not link.endswith("pubhtml"):
        st.write("Please make sure your google sheets link is in the published format. See instructions if you need help.")
        return pd.DataFrame()
    else:
        return pd.DataFrame()