import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup
import requests

def collect_excel():
    '''This method collects data from an .xlsx or .xsv file and returns a data frame of the input.'''
    # Instructions
    with st.expander("Instructions"):
        st.markdown("1. Make a new excel file or download [this template]().\n"
                    "2. Create a 'Schools' column with your school names (could be dummy names if you want to keep them "
                    "anonymous). Make sure to name this column 'Schools'.\n"
                    "3. Create other columns for all other application events. You can name these whatever you want.\n"
                    "4. Enter dates for all recorded events. For schools that have ignored you, or events that you "
                    "haven't heard of yet, leave these blank.\n"
                    "5. Save the file and make sure that it is in '.xlsx' format. Once this is done, it is ready to "
                    "upload!")
        st.image('images/example_excel_doc_dark.png')

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
        st.markdown("1. Create a google sheet with your data. Feel free to make a copy of the [sample template]"
                    "(https://docs.google.com/spreadsheets/d/1m-pWOmML_MeEa71G2e2FLCWyQzNZdW4s9L1y7Ap5vEY/edit?usp=sharing). "
                    "The first column must contain schools. Other columns can be any dates of choice (e.g. secondaries,"
                    " interviews, acceptances, etc.\n"
                    "2. Publish your google sheet by clicking the following: File -> Share -> Publish to Web.\n"
                    "3. Copy the generated link into the text box provided.")
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