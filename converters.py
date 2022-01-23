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
            try:
                data[column] = pd.to_datetime(data[column])
            except:
                print(f"Error: some of your dates are not formatted correctly in {column}")

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
    # Fill in missing data and drop unnamed columns
    cleaned_data = cleaned_data.ffill()
    cleaned_data = cleaned_data.loc[:, ~cleaned_data.columns.str.contains("Unnamed")]
    return cleaned_data

def convert_fancy_line(df):
    # Parsing the supplied df, dropping unnamed columns and melting to transpose data
    df = df.loc[:, ~df.columns.str.contains("Unnamed")]
    col1 = df.columns[0]
    df = df.melt(id_vars=col1, value_vars=df.columns[1:], var_name="Actions", value_name="Dates")
    try:
        df["Dates"] = pd.to_datetime(df["Dates"])
    except:
        print("Error: some of your dates are not formatted correctly - Please double check them.")

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
        df_temp1 = {col1: "Start", "Actions": group["Actions"].unique()[0], "Dates": min(df_sort1["Dates"]),
                    "tracker": 0}
        df_temp2 = {col1: "End", "Actions": group["Actions"].unique()[0], "Dates": max(df_sort1["Dates"]),
                    "tracker": np.max(group["tracker"])}
        group = group.append([df_temp1, df_temp2], ignore_index=True)
        group = group.sort_values(["Dates", "tracker"], ascending=True)
        df_sort_list2.append(group)
    df_sort2 = pd.concat(df_sort_list2, axis=0).reset_index(drop=True)
    return df_sort2