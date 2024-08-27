import streamlit as st
import pandas as pd
from datetime import  date,  timedelta, datetime as dt
import time
from custom_functions import *
import pytz
import base64
from PIL import Image


# Define the custom page icon
p_icon = Image.open("image/page_icon.ico")

#----------Page config-------------------------------------------------
st.set_page_config(page_title="Calendar", page_icon=p_icon)

#=========== Using CSS Style =====================================
with open("style.css") as css:
    st.markdown(f'<style>{css.read()}</style>', unsafe_allow_html=True)

 # Define the function to get the base64 encoding of the image
@st.cache_data
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()
# Define the function to set the background image
def set_png_as_page_bg(png_file):
    bin_str = get_base64_of_bin_file(png_file)
    page_bg_img = '''
    <style>
    [data-testid="stSidebarUserContent"] {
    background-image: url("data:image/png;base64,%s");
    background-size: cover; 
    padding: 0.5rem;
    }
    </style>
    ''' % bin_str 

    return st.markdown(page_bg_img, unsafe_allow_html=True)

# Set the background image for the sidebar
set_png_as_page_bg('image/bg_img_03.png')

# Get the base64 encoding of the image for use in the plotly chart
encoded_string = get_base64_of_bin_file('image/bg_img_03.png')
encoded_image = "data:image/png;base64," + encoded_string

#----------Read data---------------------------------------------------
df_bh = read_csv_data(url)
if 'df_bh' not in st.session_state:    
    st.session_state['df_bh'] = df_bh

# Convert the 'תאריך' column to datetime format
df_bh['תאריך'] = df_bh['תאריך'].apply(lambda x : pd.to_datetime(x))
bh_date = [d.date() for d in df_bh['תאריך']]

# Define the start and end dates
start_date = date(2024, 1, 1)    
end_date = date(2033, 12, 31)  

# Define the custom order for the 'day_name' column
custom_week_order = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']

# Create a dataframe from the range of dates
df_range = create_calendar_range(start_date, end_date, custom_week_order)
st.session_state['df_range'] = df_range

#----------Sidebar config--------------------------------------------------
with st.sidebar:
    st.metric("Today", dt.now(pytz.timezone('Israel')).strftime("Today is %A"), label_visibility='hidden')
    st.metric("Date", dt.now(pytz.timezone('Israel')).strftime("%d %B %Y"), label_visibility='hidden')                                    
    st.metric("Time", dt.now(pytz.timezone('Israel')).strftime("Current Time : %H:%M %p"), label_visibility='hidden')
    tz = pytz.timezone('Israel')
    st.write("Timezone: ", tz)       
    
    st.divider()    # add a horizontal line  
    st.markdown("""
                <p style="text-align: center;">Made with 🤍 by Natalia</p>""" 
                , unsafe_allow_html=True)  
    
#----------Calendar tabs--------------------------------------------------

tab_c, tab_h = st.tabs(['Calendar', 'Holidays'])  

with tab_c:  
    col_y, col_m, col_chooce = st.columns(3)

    year = col_y.selectbox('Select year', df_range['year'].unique(), index=0)
    col_chooce.write('')
    chooce = col_chooce.toggle('Monthly calendar', help='Select to show monthly calendar')

    if chooce: 
        current_month = dt.now(pytz.timezone('Israel')).strftime("%B")
        month_names = df_range['month_name'].unique().tolist()   
        month = col_m.selectbox('Select month', month_names, index=month_names.index(current_month))
        # Filter the dataframe by year and month
        df_year_month = df_range[(df_range['year'] == year) & (df_range['month_name'] == month)] 
        # Create the monthly calendar 
        m_calendar = monthly_calendar(df_year_month, year, month, bh_date)
        st.plotly_chart(m_calendar)
        # Create the holidays table
        holidays = df_bh[(df_bh['שנה'] == year) & (df_bh['חודש'] == month)].iloc[:, [5, 1, 2, 3, 0]]
        if len(holidays) > 0:
            ht=holidays_table(holidays, year, month)
            st.plotly_chart(ht)
    else:
        # Filter the dataframe by year
        df_year = df_range[df_range['year'] == year]
        # Create the calendar plot
        calendar = make_calendar(df_year, year, bh_date)
         # Update the layout for the plotly chart
        calendar.update_layout(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            modebar_remove=['zoom', 'pan', 'zoomIn', 'zoomOut', 'autoScale', 'resetScale'],
            # Add image as background
            images=[dict(source= encoded_image,
                         xref= "x",
                         yref= "y",
                         x=-1,
                         y=4,
                         sizex=7.5,
                         sizey=7.5,
                         sizing="contain",
                         #opacity= 0.5,
                         layer= "below")])
        st.plotly_chart(calendar)

with tab_h:
    # Create the all holidays table
    all_bh = pd.crosstab(df_bh['מועד'], 
                         df_bh['שנה'],
                         values= df_bh['תאריך'], 
                         aggfunc='min').sort_values(by=2024)
    for col in all_bh.columns:
        all_bh[col] = all_bh[col].apply(lambda x : x.strftime('%d-%m'))
    all_bh = all_bh.reset_index()  
    # Display the table chart
    st.plotly_chart(all_holidays_table(all_bh))
    # Add link buttons 
    col_csv, col_source, col_drive = st.columns(3)
    col_csv.link_button('Download the file "Bank Holidays"', url=url, help='Click to download the csv file', use_container_width=True)
    col_source.link_button('Source of the Data', url='https://calendar.2net.co.il/annual-calendar.aspx', use_container_width=True)
    col_drive.link_button('Data preparation', url='https://colab.research.google.com/drive/1syHM-sgd_y-sNzh8UG5HuavDNBVvW8V1?usp=sharing', use_container_width=True)

