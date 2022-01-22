import pandas as pd
import datetime as dt
import numpy as np
import streamlit as st

def convert_sums(data):
    '''Converts raw input into sums of actions for every date.'''
    # Store numbers of each action on each date
    dicts = []
    # Collect the dates and numbers of actions
    for column in data.columns:
        if column != data.columns[0]:
            # Convert to date time
            data[column] = pd.to_datetime(data[column])

            # Gather number of actions at each date for every type of action
            temp_dict = {}
            for date in data[column]:
                # Get number of actions per date
                if not pd.isnull(date):
                    temp_dict[date] = sum(data[column] <= date)
            dicts.append(temp_dict)

    # Get column names based on number user supplied
    column_names = {}
    for i in range(0, len(data.columns[1:])):
        column_names[i] = data.columns[1:][i]

    # Generate data frame
    cleaned_data = pd.DataFrame(dicts).T
    cleaned_data = cleaned_data.rename(column_names, axis=1)
    # Add starting point
    cleaned_data.loc[min(cleaned_data.index) - dt.timedelta(1)] = [0 for i in range(0, len(column_names))]
    cleaned_data = cleaned_data.sort_index()
    # Fill in any missing days
    cleaned_data = cleaned_data.reindex(pd.date_range(start=min(cleaned_data.index), end=max(cleaned_data.index)))
    # Fill in missing data
    cleaned_data = cleaned_data.ffill()
    return cleaned_data

def convert_dan_line(df):
    # Asking users for a start an end date from a calendar input
    st.subheader("Enter in the Start and End Dates of your Application Cycle:")
    start_date = st.date_input("When did you submit your AMCAS primary application?")
    start_date = pd.to_datetime(start_date)
    end_date = st.date_input("What is the current date or the date of the end of your application cycle?")
    end_date = pd.to_datetime(end_date)
    st.markdown("---")

    # Parsing the supplied df, dropping unnamed columns and melting to transpose data
    df = df.loc[:, ~df.columns.str.contains("Unnamed")]
    column_names = list(df.columns)
    col1 = column_names[0]
    column_names = column_names[1:]
    df = df.melt(id_vars=col1, value_vars=column_names, var_name="Actions", value_name="Dates")
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
                numbers.append(n)
            else:
                n = n + 1
                numbers.append(n)
    df_sort1["tracker"] = numbers

    # Adding the start date of the cycle and the current date and sorting
    df_gb2 = df_sort1.groupby("Actions")
    df_sort_list2 = []
    for name, group in df_gb2:
        df_temp1 = {"schools": "Start", "Actions": group["Actions"].unique()[0], "Dates": start_date, "tracker": 0}
        df_temp2 = {"schools": "End", "Actions": group["Actions"].unique()[0], "Dates": end_date,
                    "tracker": np.max(group["tracker"])}
        group = group.append([df_temp1, df_temp2], ignore_index=True)
        group = group.sort_values(["Dates", "tracker"], ascending=True)
        df_sort_list2.append(group)
    df_sort2 = pd.concat(df_sort_list2, axis=0).reset_index(drop=True)
    return df_sort2