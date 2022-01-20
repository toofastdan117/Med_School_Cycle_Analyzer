### Medical School Cycle Analzyer

# Importing the required packages
import streamlit as st
from PIL import Image
import pandas as pd
import numpy as np
import datetime as datetime
import plotly.express as px
import base64
from io import StringIO, BytesIO
from bs4 import BeautifulSoup
import requests

### Defining some functions for downloading excel docs and html plotly graphs

def generate_excel_download_link(example_df):
    """Generates a download link for an excel file"""
    # Credit Excel: https://discuss.streamlit.io/t/how-to-add-a-download-excel-csv-function-to-a-button/4474/5
    towrite = BytesIO()
    example_df.to_excel(towrite, encoding="utf-8", index=False, header=True)  # write to BytesIO buffer
    towrite.seek(0)  # reset pointer
    b64 = base64.b64encode(towrite.read()).decode()
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="Medical School Cycle Analyzer Template.xlsx">Download Example Excel Template</a>'
    return st.markdown(href, unsafe_allow_html=True)

def generate_html_download_link(fig2):
    """Generates a download link for the html plotly graphs"""
    # Credit Plotly: https://discuss.streamlit.io/t/download-plotly-plot-as-html/4426/2
    towrite = StringIO()
    fig2.write_html(towrite, include_plotlyjs="cdn")
    towrite = BytesIO(towrite.getvalue().encode())
    b64 = base64.b64encode(towrite.read()).decode()
    href = f'<a href="data:text/html;charset=utf-8;base64, {b64}" download="cycle_line_plot.html">Download Application Cycle Plot</a>'
    return st.markdown(href, unsafe_allow_html=True)

def parse_google_sheets(link):
    '''Returns a DataFrame that contains cycle data from google sheets. Requires that the sheet is in published mode.'''
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

### Setting the page title using streamlit
st.set_page_config(page_title="Medical School Application Plotter")
st.title("Medical School Application Plotter")  #🥼🩺📈
st.markdown("#### Created by [TooFastDan](https://github.com/toofastdan117)")
no_sankey = Image.open("images/BanSankey.png")
st.image(no_sankey)
st.markdown("This is a tool for visualizing your application cycle using a line plot. We believe that line plots provide "
            "more useful data for future applicants than typical Sankey diagrams. The github repository for this "
            "project is located [here](https://github.com/toofastdan117/Med_School_Cycle_Analyzer).")
st.markdown("---")

### User imput start date of AMCAS submission and current date
st.subheader("Enter in the Start and End Dates of your Application Cycle:")
start_date = st.date_input("When did you submit your AMCAS primary application?")
start_date = pd.to_datetime(start_date)
end_date = st.date_input("What is the current date or the date of the end of your application cycle?")
end_date = pd.to_datetime(end_date)
st.markdown("---")

### Choose option for input data
st.subheader("Select a Method:")
data_choice = st.selectbox('Would you like to upload an excel document, or link a google sheet?', ('Excel', 'Google Sheets'))
st.markdown("---")

data_input = False
### Excel choice
if data_choice == 'Excel':
    # Download template excel file
    st.subheader("Upload a formatted Excel file:")
    example_df = pd.read_excel("example_excel_files/Example Excel Template.xlsx", engine="openpyxl")
    generate_excel_download_link(example_df)

    # Example expander with instructions and a picture of an example excel upload
    with st.expander("Click Here for Instructions"):
        # Instructions
        st.write("1.  Make a new excel file or download the template above.")
        st.write("2.  Create a 'Schools' column with your school names (could be dummy names if you want to keep them anonymous). Make sure to name this column 'Schools'.")
        st.write("3.  Create other columns for all other application events. You can name these whatever you want.")
        st.write("4.  Enter dates for all recorded events. For schools that have ignored you, or events that you haven't heard of yet, leave these blank.")
        st.write("5.  Save the file and make sure that it is in '.xlsx' format. Once this is done, it is ready to upload!")

        # Display image of an example excel file
        image = Image.open("images/example_excel_doc_dark.png")
        st.image(image, caption="Example of a formatted excel doc")

    # Request to upload an excel file
    uploaded_file = st.file_uploader("Upload an xlsx file:", type=("xlsx", "csv"))

    if uploaded_file:
        data_input = True

        # Pandas to read the uploaded excel/csv file and display it
        st.markdown("---")
        if uploaded_file.name.endswith("xlsx"):
            df = pd.read_excel(uploaded_file, engine="openpyxl")
        elif uploaded_file.name.endswith("csv"):
            df = pd.read_csv(uploaded_file)
        st.subheader("Uploaded excel file:")
        st.dataframe(df)
        st.markdown("---")

### Google sheets choice
elif data_choice == 'Google Sheets':
    st.subheader("Upload data from Google Sheets:")
    st.markdown('[Link to Sample Google Sheet](https://docs.google.com/spreadsheets/d/1m-pWOmML_MeEa71G2e2FLCWyQzNZdW4s9L1y7Ap5vEY/edit?usp=sharing)')
    # Instructions
    with st.expander("Click Here for Instructions"):
        # Instructions
        st.write("1.  Create a google sheet with your data. Feel free to make a copy of the provided template. The first column "
                 "must contain schools. Other columns can be any dates of choice (e.g. secondaries, interviews, "
                 "acceptances, etc.")
        st.write("2.  Publish your google sheet by clicking the following: File -> Share -> Publish to Web.")
        st.write("3.  Copy the generated link into the text box provided.")
    link = st.text_input('Insert the link to your published google sheet in this box.')

    # Parsing the provided google sheets link
    if len(link) > 0 and link.endswith('pubhtml'):
        df = parse_google_sheets(link)
        data_input = True
        st.dataframe(df)
    elif len(link) > 0 and not link.endswith('pubhtml'):
        st.write('The entered link is not correct. Please make sure you published the google sheet to the web and copied the link correctly.')

### If a user uploaded an xlsx file or provided a published google sheets doc, display the df and generate a plotly line graph
if data_input:
    # Processing the dataframe by getting the columns (actions) and melting
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
        df_temp2 = {"schools": "End", "Actions": group["Actions"].unique()[0], "Dates": end_date, "tracker": np.max(group["tracker"])}
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
    fig.update_layout(title={'text': "Application Cycle Plot", 'y': 0.90, 'x': 0.44, 'xanchor': 'center', 'yanchor': 'top'})
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
    fig2.update_layout(title={'text': "Application Cycle Plot", 'y': 0.98, 'x': 0.44, 'xanchor': 'center', 'yanchor': 'top'})

    # Displaying the download section
    st.markdown("---")
    st.subheader("Downloads:")
    generate_html_download_link(fig2)