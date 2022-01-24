import streamlit as st
from plotnine import ggplot, aes, geom_point, scale_x_date, theme, labs
import pandas as pd

def generate(data):
    '''Generates a Cleveland dot plot with all schools and actions for schools.'''
    title_input = st.text_input("Choose a title", value="Application Cycle")
    melted = data.melt(id_vars=data.columns[0], value_vars=data.columns[1:], var_name='Actions', value_name='date')
    height = len(melted.columns[0]) * 1
    melted['date'] = pd.to_datetime(melted['date'])
    melted = melted[~melted["Actions"].str.contains("Unnamed")]
    p = (ggplot(melted, aes(x = 'date', y = melted.columns[0], color='Actions'))
         + geom_point()
         + theme(figure_size=(5, height))
         + labs(x="", y="", title=title_input)
         + scale_x_date(date_breaks = '1 months', date_labels = '%b')
         )

    st.pyplot(ggplot.draw(p))