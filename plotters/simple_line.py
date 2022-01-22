import converters
from matplotlib import pyplot as plt
from matplotlib import dates as mdates
import streamlit as st

def generate(data):
    '''Creates a simple line graph from the raw data frame.'''
    # Convert to proper sum format
    data = converters.convert_sums(data)
    title = st.text_input("Choose a title", value="Application Cycle")
    fig = plt.figure()
    plt.style.use('ggplot')
    ax = fig.add_subplot(1,1,1)
    for column in data.columns:
        ax.plot(data.index, data[column], label=column)
    ax.legend(bbox_to_anchor=(1.04,0.5), loc='center left', frameon=False)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
    ax.set_xlabel("Month")
    ax.set_ylabel("Count")
    ax.set_title(title)

    st.pyplot(fig)