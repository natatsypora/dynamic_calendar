import streamlit as st
import pandas as pd
from datetime import  date,  timedelta, datetime as dt
import plotly.graph_objects as go
from plotly.subplots import make_subplots

#Define colors for the calendar
bg_bh='rgba(255, 100, 100, 0.3)'
bg_body='rgba(228, 222, 249, 0.4)'
bg_nan='rgba(228, 222, 249, 0.2)'
bg_head='rgb(174,190,228)' #'#C2D4FF'
f_color_head='rgba(0, 0, 0, 0.7)'
f_color_title='#536490'#'#769EFF'
line_color='#536490'

# Define the Google Drive file URL for 'bank_holidays.csv
url = 'https://drive.google.com/file/d/1m7Z6umeKpMj-rikz_wjvId7zIyUZ5yTF/view?usp=sharing'

# Define the function to get the file path and download the file
def get_path_from_url(url):
    path = url.split('/')[-2]
    file_path = 'https://drive.google.com/uc?export=download&id=' + path
    return file_path

# Define the function to read the csv
@st.cache_data
def read_csv_data(url, **kwargs):
    file_path = get_path_from_url(url)
    df = pd.read_csv(file_path)
    return df

#=========== Calendar  Functions ================================
#----------Get week of month-------------------------------------
def week_of_month(df_col_date):
    '''Returns the week of the month for the specified date.
        Sunday as first day of the week !
    '''
    first_day = df_col_date.replace(day=1)
    dom = df_col_date.day
    adjusted_dom = dom + (first_day.weekday() + 1) % 7
    return (adjusted_dom - 1) // 7 + 1

#----------Create Calendar Range---------------------------------
@st.cache_data
def create_calendar_range(start_date, end_date, custom_order):
    #create dataframe from range of dates   
    df = pd.DataFrame(pd.date_range(start_date,
                                    end_date,
                                    freq='d'))  
    #create columns of date, year, month, month_name, day, day_name, week_of_month  
    df['date'] = df[0].apply(lambda x: x.date())
    df['year'] = df[0].dt.year
    df['month'] = df[0].dt.month
    df['month_name'] = df[0].dt.strftime('%B')
    df['day'] = df[0].dt.day    
    df['day_name'] = df[0].dt.strftime('%a') # short form of weekday name 'Sun'...
    df['week_of_month'] = df[0].apply(week_of_month)
    # convert 'day_name' column to a categorical type using custom order
    df['day_name'] = pd.Categorical(df['day_name'],
                                    categories=custom_order,
                                    ordered=True)
    return df

#----------Make Calendar ----------------------------------------
@st.cache_data
def make_calendar(df, year, bh_date=[]):
    fig = make_subplots(
            rows=4, cols=3,
            subplot_titles=[f'<b>{el} {year}</b>' for el in df['month_name'].unique().tolist()],
            vertical_spacing=0.03,
            horizontal_spacing=0.03,
            specs=[[{"type": "table"}]*3,
                   [{"type": "table"}]*3,
                   [{"type": "table"}]*3,
                   [{"type": "table"}]*3])

    for i, m in enumerate(df['month_name'].unique()):
        df_m = df[df['month_name'] == m]
        df_crosstab = pd.crosstab(df_m['week_of_month'], df_m['day_name'],
                                  values=df_m[0], aggfunc='min')

        row = i // 3 + 1
        col = i % 3 + 1

        colors = [['red' if v.date() in bh_date else ('rgba(228, 222, 249, 0.0)' if pd.isna(v.date()) else 'black') for v in df_crosstab[r]]
                                             for r in df_crosstab.columns]
        fill_colors =  [[bg_bh if v.date() in bh_date or (r=='Sat' and not pd.isna(v.date()))
                          else (bg_nan if  pd.isna(v.date()) else bg_body) for v in df_crosstab[r]]
                                             for r in df_crosstab.columns]
        # Create table
        fig.add_trace(go.Table(
            header=dict(values=df_crosstab.columns.values,
                        fill_color=bg_head, line_color=line_color,
                        font_size=14, font_color=f_color_head,
                        height=30, align='center'),
            cells=dict(values=[df_crosstab[col].dt.day for col in df_crosstab.columns],
                       font_color = colors, height=30, font_size=14,       
                       fill_color = fill_colors, line_color=line_color,
                       align='center')), row=row, col=col)
    # Layout
    fig.update_layout(width=1000, height=1050, #paper_bgcolor='rgba(255,255,255,0)',
                      title=f'<b>Calendar With Holidays {year}<b>', title_x =0.35,
                      title_font_size=22, title_font_color=f_color_title,
                      margin=dict(l=10, r=10, b=10, t=100))

    return fig

#----------Monthly Calendar -------------------------------------
@st.cache_data
def monthly_calendar(df_month, year, month, bh_date):
    df_crosstab = pd.crosstab(df_month['week_of_month'], df_month['day_name'],
                                   values=df_month[0], aggfunc='min')
    colors = [['red' if v.date() in bh_date else ('rgba(0, 0, 0, 0.0)' if pd.isna(v.date()) else 'black') for v in df_crosstab[r]]
                                             for r in df_crosstab.columns]
    fill_colors =  [[bg_bh if v.date() in bh_date or (r=='Sat' and not pd.isna(v.date()))
                            else (bg_nan if  pd.isna(v.date()) else bg_body) for v in df_crosstab[r]]
                                                for r in df_crosstab.columns]
    header_colors = [bg_bh if h=='Sat' else bg_head for h in df_crosstab.columns]
                                                                                            
    fig=go.Figure(go.Table(
            header=dict(values=[f'<b>{h}<b>' for h in df_crosstab.columns.values],
                        fill_color=header_colors,  font_color='rgba(0, 0, 0, 0.7)',
                        height=40, align='center'),
            cells=dict(values=[df_crosstab[col].dt.day for col in df_crosstab.columns],
                       fill_color=fill_colors, font_color = colors, height=35, 
                       align='center')))
    # Layout with scroll
    fig.update_layout(title=f'<b>{month} {year}<b>', title_x =0.35, 
                     title_font_size=22, font_size=18, title_font_color=f_color_title,
                     width=800, height=350,  
                     margin=dict(l=10, r=10, b=10, t=70),)
    return fig

#----------Holidays Table --------------------------------------
@st.cache_data
def holidays_table(df_bh_monthly, year, month):   
    fig = go.Figure(data=[go.Table(
    columnwidth = [50]*4+ [150],
    header = dict(
        values=[f'<b>{h}<b>' for h in df_bh_monthly.columns],        
        fill_color=bg_head,
        font_size=16, font_color='rgba(0, 0, 0, 0.7)',
        height=40),
    cells=dict(
        values=df_bh_monthly.T.values,        
        fill=dict(color=[bg_body]*4+[bg_head]),
        font_size=16,
        height=35))
            ])
    fig.update_layout(title=f'Holidays {month} {year}', title_x=0.35, title_font_size=20,
                      font_size=18, title_font_color='rgba(255, 100, 100, 0.8)', 
                      width=800, height=df_bh_monthly.shape[0]*35+150, 
                      margin=dict(l=10, r=10, b=10, t=70))
    return fig

#----------All Holidays Table --------------------------------------
@st.cache_data
def all_holidays_table(all_bh):   
        fig = go.Figure(data=[go.Table(
        columnwidth = [150]+[50]*10,
        header = dict(
            values = [f'<b>{h}<b>' for h in all_bh.columns],            
            fill_color=bg_head,
            font_size=16, font_color='rgba(0, 0, 0, 0.7)',
            height=40),
        cells=dict(
            values=all_bh.T.values,            
            fill_color=[bg_head]+[bg_body]*10,
            font_size=16,
            height=35))
        ])
        fig.update_layout(title=f'Bank Holidays 2024-2033', title_x=0.4, 
                          title_font_size=20, title_font_color=f_color_title, 
                          width=1000, height=all_bh.shape[0]*35+150, 
                          margin=dict(l=10, r=10, b=10, t=70))
        return fig
