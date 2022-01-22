import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

def generate(df):
    st.subheader("Enter in the Start and End Dates of your Application Cycle:")
    start_date = st.date_input("When did you submit your AMCAS primary application?")
    start_date = pd.to_datetime(start_date)
    end_date = st.date_input("What is the current date or the date of the end of your application cycle?")
    end_date = pd.to_datetime(end_date)
    st.markdown("---")

    # Processing the dataframe by getting the columns (actions) and melting
    column_names = list(df.columns)
    column_names = [s.lower() for s in column_names]
    df.columns = column_names
    column_names.remove("schools")
    df = df.melt(id_vars="schools", value_vars=column_names, var_name="Actions", value_name="Dates")
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

    ### Selecting colors for the plotly line graph
    st.subheader("Customization Section - Pick Colors")
    action_color_dict = {}
    for action in sorted(column_names):
        hex_color = st.color_picker(f"Pick a color to represent {action}:")
        action_color_dict[action] = hex_color

    ### Dropdown menu for light mode or dark mode for the plotly line graph
    response = st.selectbox("Would you like the graph in light-mode or dark-mode?",
                            ("light-mode", "dark-mode"))
    st.write("You selected:", response)
    response_dict = {"light-mode": "simple_white", "dark-mode": "plotly_dark"}
    response_answer = response_dict[response]
    st.markdown("---")

    ### Plotting the Application Cycle as a Line Graph
    st.subheader("Application Cycle Line Graph")
    fig = px.line(df_sort2, x="Dates", y="tracker", color="Actions", color_discrete_map=action_color_dict,
                  hover_data=["schools", "Actions", "Dates"], markers=True, line_shape="hv",
                  labels={
                      "Dates": "Dates",
                      "tracker": "Number of Events",
                      "Actions": "Application Events"
                  },
                  title="Application Cycle Plot",
                  template=response_answer)
    fig.update_layout(
        title={'text': "Application Cycle Plot", 'y': 0.90, 'x': 0.44, 'xanchor': 'center', 'yanchor': 'top'})
    st.plotly_chart(fig)

    ### Download section
    # Plotting the a second, updated figure for downloading
    fig2 = px.line(df_sort2, x="Dates", y="tracker", color="Actions",
                   hover_data=["schools", "Actions", "Dates"], markers=True, line_shape="hv",
                   color_discrete_map=action_color_dict,
                   template=response_answer, width=1200, height=700)

    # Updating the figure with title + axes + legend labels, font sizes for the title + x, y ticks + legend size, and x, y axes labels.  Then centering the title.
    fig2.update_layout(title="Application Cycle Plot",
                       xaxis_title="Number of Events",
                       yaxis_title="Dates",
                       legend_title="Application Events",
                       font=dict(size=24))
    fig2.update_layout(yaxis=dict(tickfont=dict(size=14)), xaxis=dict(tickfont=dict(size=14)))
    fig2.update_layout(legend=dict(font=dict(size=16)))
    fig2.update_xaxes(title_font=dict(size=20))
    fig2.update_yaxes(title_font=dict(size=20))
    fig2.update_layout(
        title={'text': "Application Cycle Plot", 'y': 0.98, 'x': 0.44, 'xanchor': 'center', 'yanchor': 'top'})
