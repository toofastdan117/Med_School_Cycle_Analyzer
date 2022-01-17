### Cycle Analzyer

# Importing the required packages
import streamlit as st
import pandas as pd
import numpy as np
import datetime as datetime
import plotly.express as px

# Setting the page title using streamlit
st.set_page_config(page_title="Medical School Application Plotter")
st.title("Medical School Application Plotter 📈")
st.subheader("Upload a formatted Excel file (file type = '.xlsx')")

# Uploading an excel file containing schools, application actions, and dates
uploaded_file = st.file_uploader("Upload an xlsx file:", type="xlsx")

# If a user uploaded an xlsx file, display it and display a plotly line graph
if uploaded_file:
    # Separating line
    st.markdown("---")

    # Pandas to read the uploaded excel file and display it
    df = pd.read_excel(uploaded_file, engine="openpyxl")
    st.subheader("Uploaded excel file:")
    st.dataframe(df)
    st.markdown("---")

    # Processing the dataframe by getting the columns (actions) and melting
    column_names = list(df.columns)
    column_names.remove("Schools")
    df = df.melt(id_vars="Schools", value_vars=column_names, var_name="Actions", value_name="Dates")
    df["Dates"] = pd.to_datetime(df["Dates"])

    # Grouping the application actions and sorting by date
    df_gb1 = df.groupby("Actions")
    df_sort_list1 = []
    for name, group in df_gb1:
        group = group.sort_values("Dates", ascending=True)
        df_sort_list1.append(group)
    df_sort1 = pd.concat(df_sort_list1, axis=0).reset_index(drop=True)

    # Ranking the events by date, ignoring dates that are not present (NaT)
    numbers = []
    for action in df_sort1["Actions"].unique():
        n = 0
        df_temp = df_sort1[df_sort1["Actions"] == action]
        for d in df_temp["Dates"]:
            if pd.isnull(d):
                n = n
                numbers.append(n)
            else:
                n = n + 1
                numbers.append(n)
    df_sort1["tracker"] = numbers

    # Adding the start date of the cycle and the current date and sorting
    start = datetime.datetime(2021, 5, 28)  # AMCAS primary submission date
    start = pd.to_datetime(start)
    now = datetime.datetime.now()  # current date
    now = now.strftime("%m/%d/%Y %H:%M:%S")
    now = pd.to_datetime(now)
    df_gb2 = df_sort1.groupby("Actions")
    df_sort_list2 = []
    for name, group in df_gb2:
        df_temp1 = {"Schools": "Start", "Actions": group["Actions"].unique()[0], "Dates": start, "tracker": 0}
        df_temp2 = {"Schools": "End", "Actions": group["Actions"].unique()[0], "Dates": now,
               "tracker": np.max(group["tracker"])}
        group = group.append([df_temp1, df_temp2], ignore_index=True)
        group = group.sort_values("Dates", ascending=True)
        df_sort_list2.append(group)
    df_sort2 = pd.concat(df_sort_list2, axis=0).reset_index(drop=True)

    # Displaying the formatted dataframe after processing
    #st.subheader("Processed excel file:")
    #st.dataframe(df_sort2)
    #st.markdown("---")

    # Plotting the Application Cycle as a Line Graph
    fig = px.line(df_sort2, x="Dates", y="tracker", color="Actions",
                  hover_data=["Schools", "Actions", "Dates"], markers=True, line_shape="hv",
                  labels={
                      "Dates": "Dates",
                      "tracker": "Number of Events",
                      "Actions": "Application Events"
                  },
                  title="Application Cycle Plot",
                  template="plotly_dark")
    st.subheader("Application Cycle Line Graph:")
    st.plotly_chart(fig)

    # Download section
    st.markdown("---")
    st.subheader("Downloads:")