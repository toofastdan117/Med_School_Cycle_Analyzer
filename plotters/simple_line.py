import converters
from plotnine import ggplot, aes, geom_line, scale_x_date, labs, theme
import streamlit as st

def generate(data):
    '''Creates a simple line graph from the raw data frame.'''
    # Convert to proper sum format
    data = converters.convert_sums(data)

    # Melt for plotting
    data['date'] = data.index
    melted = data.melt(id_vars='date', value_vars=data.columns[0:len(data.columns)-1], var_name="Actions",
                               value_name="Count")

    input_title = st.text_input("Choose a title", value="Application Cycle")
    # Plot
    plot = (
            ggplot(melted, aes(x='date', y='Count', color='Actions'))
            + geom_line()
            + scale_x_date(date_breaks = '1 months', date_labels='%b')
            + labs(x="", y="Count", title = input_title)
            + theme(figure_size=(5,3))
    )
    st.pyplot(plot.draw())