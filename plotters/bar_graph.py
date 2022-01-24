import converters
from plotnine import ggplot, aes, scale_x_date, geom_bar, labs
import streamlit as st

def generate(data):
   data = converters.convert_bar(data)
   if not data.empty:
      # Grab title
      title_label = st.text_input("Choose a title", value="Application Cycle")

      plot = (ggplot(data, aes(x='Date', fill='Best Outcome', color='Best Outcome'))
              + geom_bar()
              + scale_x_date(date_breaks = '1 months', date_labels = '%b')
              + labs(x="", y="Count", title = title_label))

      st.pyplot(plot.draw())