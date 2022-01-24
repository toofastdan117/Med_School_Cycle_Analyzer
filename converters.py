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

    # Adding the start and end date of the cycle and sorting
    df_filt = df_sort1[df_sort1["Dates"].notna()]
    start_date = min(df_filt["Dates"])
    end_date = max(df_filt["Dates"])
    df_gb2 = df_sort1.groupby("Actions")
    df_sort_list2 = []
    for name, group in df_gb2:
        df_temp1 = {col1: "Start", "Actions": group["Actions"].unique()[0], "Dates": start_date, "tracker": 0}
        df_temp2 = {col1: "End", "Actions": group["Actions"].unique()[0], "Dates": end_date,
                    "tracker": np.max(group["tracker"])}
        group = group.append([df_temp1, df_temp2], ignore_index=True)
        group = group.sort_values(["Dates", "tracker"], ascending=True)
        df_sort_list2.append(group)
    df_sort2 = pd.concat(df_sort_list2, axis=0).reset_index(drop=True)
    return df_sort2

def convert_bar(data):
    # Label the data to obtain priorities
    st.subheader("I need some help labeling your data...")
    labels = {"" : 999, "Primary Submitted" : 8, "Secondary Received" : 7, "Secondary Submitted" : 6, "Application Complete" : 5,
              "Interview Received" : 4, "Interview Day" : 3, "Rejection" : 2, "Waitlist" : 1, "Acceptance" : 0, "Withdrawn" : -1,
              "None of the Above" : 999}
    assigned_labels = {}
    for column in data.columns[1:]:
        assigned_label = st.selectbox(f"Assign a label for the column: {column}", labels.keys())
        if len(assigned_label) > 0:
            assigned_labels[column] = labels[assigned_label]
    # Continue after assignments made
    if len(assigned_labels) == len(data.columns[1:]):
        # Sort assigned labels
        assigned_labels = dict(sorted(assigned_labels.items(), key=lambda item: item[1]))

        # Obtain a list of all dates between min and max
        input_dates = []
        for col in data.columns[1:]:
            for date in data[col]:
                input_dates.append(date)
        input_dates = pd.to_datetime(input_dates).dropna()
        all_dates = pd.date_range(start=min(input_dates), end=max(input_dates))

        # Convert raw data into datetime
        for column in data.columns[1:]:
            data[column] = pd.to_datetime(data[column])

        # For each date, check each school and assign it its highest status
        output = []
        for date in all_dates:
            for index, row in data.iterrows():
                for key, value in assigned_labels.items():
                    if not pd.isnull(row[key]) and date >= row[key] and value !=999:
                        output.append([date, key])
                        break
        return pd.DataFrame(output, columns=['Date', 'Action'])
    else:
        return pd.DataFrame()