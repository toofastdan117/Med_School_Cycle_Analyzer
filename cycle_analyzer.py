### Cycle Analzyer

# Importing the required packages
import streamlit as st
from PIL import Image
import pandas as pd
import numpy as np
import datetime as datetime
import plotly.express as px
import base64
from io import StringIO, BytesIO

# Defining some functions for downloading html plotly charts
def generate_html_download_link(fig2):
    # Credit Plotly: https://discuss.streamlit.io/t/download-plotly-plot-as-html/4426/2
    towrite = StringIO()
    fig2.write_html(towrite, include_plotlyjs="cdn")
    towrite = BytesIO(towrite.getvalue().encode())
    b64 = base64.b64encode(towrite.read()).decode()
    href = f'<a href="data:text/html;charset=utf-8;base64, {b64}" download="cycle_line_plot.html">Download Plot</a>'
    return st.markdown(href, unsafe_allow_html=True)

# Setting the page title using streamlit
st.set_page_config(page_title="Medical School Application Plotter")
st.title("Medical School Application Plotter 🥼🩺📈")
st.markdown("---")

# User imput start date of AMCAS submission and current date
st.subheader("Enter in the Start and End Dates of your Application Cycle:")
start_date = st.date_input("When did you submit your AMCAS primary application?")
start_date = pd.to_datetime(start_date)
end_date = st.date_input("What is the current date or the date of the end of your application cycle?")
end_date = pd.to_datetime(end_date)
st.markdown("---")

# Uploading an excel file containing schools, application actions, and dates
st.subheader("Upload a formatted Excel file:")
with st.expander("Click Here for Instructions"):
    st.write("1.  Make a new excel file.")
    st.write("2.  Create a 'Schools' column with your school names (could be dummy names if you want to keep them anonymous). Make sure to name this column 'Schools'.")
    st.write("3.  Create other columns for all other application events. You can name these whatever you want.")
    st.write("4.  Enter dates for all recorded events. For schools that have ignored you, or events that you haven't heard of yet, leave these blank.")
    st.write("5.  Save the file and make sure that it is in '.xlsx' format. Once this is done, it is ready to upload!")
    image = Image.open("images/example_excel_doc_dark.png")
    st.image(image, caption="Example of a formatted excel doc")
uploaded_file = st.file_uploader("Upload an xlsx file:", type="xlsx")

# If a user uploaded an xlsx file, display it and display a plotly line graph
if uploaded_file:
    # Separating line
    st.markdown("---")

    ### Pandas to read the uploaded excel file and display it
    df = pd.read_excel(uploaded_file, engine="openpyxl")
    st.subheader("Uploaded excel file:")
    st.dataframe(df)
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
                n = n
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
        group = group.sort_values("Dates", ascending=True)
        df_sort_list2.append(group)
    df_sort2 = pd.concat(df_sort_list2, axis=0).reset_index(drop=True)

    #### Dropdown menu for light mode or dark mode for the plotly line graph
    response = st.selectbox("Would you like the graph in light-mode or dark-mode?",
                            ("light-mode", "dark-mode"))
    st.write("You selected:", response)
    response_dict = {"light-mode": "simple_white", "dark-mode": "plotly_dark"}
    response_answer = response_dict[response]

    #### Selecting colors for the plotly line graph
    action_color_dict = {}
    for action in sorted(column_names):
        hex_color = st.color_picker(f"Pick a color to represent {action}:")
        action_color_dict[action] = hex_color

    #### Plotting the Application Cycle as a Line Graph
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
    st.subheader("Application Cycle Line Graph:")
    st.plotly_chart(fig)

    ### Download section
    st.markdown("---")
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
    st.subheader("Downloads:")
    generate_html_download_link(fig2)