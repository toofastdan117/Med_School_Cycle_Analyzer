import streamlit as st
import pandas as pd
import collectors
from plotters import line_graph, dot_graph, dan_line

# Page Settings
import converters

st.set_page_config(page_title="CycleVis", page_icon="images/BanSankey.png")

# Welcome
st.title("Hi! Welcome to CycleVis.")
st.markdown("A medical school application cycle visualization tool by [TooFastDan](https://github.com/toofastdan117) and"
            " [RunningMSN](https://github.com/RunningMSN). To see how this works, visit the "
            "[github repository](https://github.com/toofastdan117/Med_School_Cycle_Analyzer).")

# Data Collection
st.subheader("Getting Started")
st.write("To start visualizing your cycle, you will need to supply your application cycle data. Currently, this tool supports "
             "uploaded tables or links from google docs.")
upload_format = st.selectbox("Choose an upload format", ("Excel", "Google Sheets"))
# Collection formats
if upload_format == "Excel":
    data_raw = collectors.collect_excel()
elif upload_format == "Google Sheets":
    data_raw = collectors.collect_google()
else:
    st.write("Sorry this option is coming soon.")
    data_raw = pd.DataFrame()

# Perform visualizations on data
if not data_raw.empty:
    # Show Data
    st.subheader("Awesome. Here's your data!")
    st.markdown("If this looks right, let's keep going. If not, go back and reupload the corrected data.")
    st.dataframe(data_raw)

    # Choose Visualizations
    st.subheader("Pick a Visualization")
    graph_choice = st.selectbox("Choose a visualization. You can always come back and switch to another one later.",
                                ("","Fancy Line","Simple Line","Dot"))
    if graph_choice == "Fancy Line":
        dan_line.generate(data_raw)
    elif graph_choice == "Simple Line":
        line_graph.generate(data_raw)
    elif graph_choice == "Dot":
        dot_graph.generate(data_raw)