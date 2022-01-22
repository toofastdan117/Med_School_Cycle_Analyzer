import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import base64
from io import StringIO, BytesIO
import converters


def generate_html_download_link(fig2):
    """Generates a download link for the html plotly graphs"""
    # Credit Plotly: https://discuss.streamlit.io/t/download-plotly-plot-as-html/4426/2
    towrite = StringIO()
    fig2.write_html(towrite, include_plotlyjs="cdn")
    towrite = BytesIO(towrite.getvalue().encode())
    b64 = base64.b64encode(towrite.read()).decode()
    href = f'<a href="data:text/html;charset=utf-8;base64, {b64}" download="cycle_line_plot.html">Download Application Cycle Plot</a>'
    return st.markdown(href, unsafe_allow_html=True)

def generate(df):
    """Generates a fancy plotly graph that is interactive and downloadable"""
    ### Processing the dataframe from the converters file
    df = converters.convert_dan_line(df)
    actions = df["Actions"].unique()

    ### Selecting colors for the plotly line graph
    st.subheader("Customization Section - Pick Colors")
    action_color_dict = {}
    for action in actions:
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
    title = st.text_input("Type a title for your graph", value="Application Cycle")
    fig = px.line(df, x="Dates", y="tracker", color="Actions", color_discrete_map=action_color_dict,
                  hover_data=["schools", "Actions", "Dates"], markers=True, line_shape="hv",
                  labels={
                      "Dates": "Dates",
                      "tracker": "Number of Events",
                      "Actions": "Application Events"
                  },
                  title=title,
                  template=response_answer)
    fig.update_layout(
        title={'text': title, 'y': 0.90, 'x': 0.44, 'xanchor': 'center', 'yanchor': 'top'})
    st.plotly_chart(fig)

    ### Download section
    # Plotting the a second, updated figure for downloading
    st.markdown("---")
    st.subheader("Downloads:")
    w = st.number_input("Optional: Input the width (in pixels) of your downloadable graph", value=1200, max_value=10000)
    h = st.number_input("Optional: Input the height (in pixels) of your downloadable graph", value=700, max_value=10000)
    fig2 = px.line(df, x="Dates", y="tracker", color="Actions",
                   hover_data=["schools", "Actions", "Dates"], markers=True, line_shape="hv",
                   color_discrete_map=action_color_dict,
                   template=response_answer, width=w, height=h)

    # Updating the figure with title + axes + legend labels, font sizes for the title + x, y ticks + legend size, and x, y axes labels.  Then centering the title.
    fig2.update_layout(title=title,
                       xaxis_title="Number of Events",
                       yaxis_title="Dates",
                       legend_title="Application Events",
                       font=dict(size=24))
    fig2.update_layout(yaxis=dict(tickfont=dict(size=14)), xaxis=dict(tickfont=dict(size=14)))
    fig2.update_layout(legend=dict(font=dict(size=16)))
    fig2.update_xaxes(title_font=dict(size=20))
    fig2.update_yaxes(title_font=dict(size=20))
    fig2.update_layout(
        title={'text': title, 'y': 0.98, 'x': 0.44, 'xanchor': 'center', 'yanchor': 'top'})

    # Displaying the download section
    generate_html_download_link(fig2)
