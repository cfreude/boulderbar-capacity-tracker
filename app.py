import streamlit as st
import pandas as pd

from datetime import datetime, timedelta
from pytz import timezone  
import plotly.express as px

from capacity import BoulderbarCapacity

df_loaded = False

import requests
try:
    response = requests.get('https://welcomed-thrush-sacred.ngrok-free.app/')
    df = pd.read_json(response.json())
    df_loaded = True
except:
    df_loaded = False

st.title('Boulderbar-Chart')

st.write("https://boulderbar.net/")
st.write('Overview of current, recorded and statistical occupancy rate data of the Boulderbars.')

location = df.columns.values if df_loaded else ['Hannovergasse', 'Wienerberg', 'Hauptbahnhof', 'Seestadt', 'Linz', 'Salzburg']

options = st.multiselect(
    'Locations:',
    location,
    location[:4])

vienna = timezone('Africa/Johannesburg')
vienna_time = datetime.now(vienna)
time_str = vienna_time.strftime('%d.%m.%Y, %H:%M:%S')

current = BoulderbarCapacity.fetch_capacities_df()
current = current[current.index.isin(options)]  

fig = px.bar(
    current,
    x='Occupancy Rate (%)',
    y=current.index,
    color=current.index,
    orientation='h',
    title=f"Current Occupancy Rate | {time_str}",
    labels={
        "index": "Location",
        "value": "Occupancy Rate (%)",
        "variable": "Location"
    },
)
fig.update_yaxes(type='category', categoryorder='trace', autorange="reversed")
fig.update_xaxes(range=[0, 100])

st.plotly_chart(fig, use_container_width=True)

if not df_loaded:
    st.write("Error: No statistics shown since loading of recorded data failed.")
    st.stop()

df = df[options]

timedelta_map = {
    'Last Hour': timedelta(hours=1),
    'Last Day': timedelta(days=1),
    'Last Week': timedelta(weeks=1),
    'Last Month': timedelta(weeks=4),
    'Last Year': timedelta(weeks=52),
    'All': None,
}

with st.expander("Timeline"):

    option = st.selectbox(
        'Timespan:',
        ('Last Hour', 'Last Day', 'Last Week', 'Last Month', 'Last Year', 'All'),
        index=1, label_visibility='hidden', key='timeline')
    
    td = timedelta_map[option]

    if td is None:
        timeline = df
    else:
        from_date = datetime.now()
        last_date = datetime.now() - td

        mask = (df.index >= last_date) & (df.index <= from_date)
        index = df.index[mask]    
        timeline = df[df.index.isin(index)]

    fig = px.line(
            timeline,
            x=timeline.index,
            y=options,
            #title="Timeline",
            labels={
                        "index": "Date",
                        "value": "Occupancy Rate (%)",
                        "variable": "Location"
                    },)


    st.plotly_chart(fig, use_container_width=True)

# mask the hours we want
hours = df.index.hour
mask = (hours >= 9) & (hours <= 23)
odh = df[mask]

with st.expander("Daily Average"):

    option = st.selectbox(
        'Timespan:',
        ('Last Week', 'Last Month', 'Last Year', 'All'),
        index=0, label_visibility='hidden', key='Daily Average',)
    
    daily_avg = odh

    td = timedelta_map[option]

    if td is not None:
        from_date = datetime.now()
        last_date = datetime.now() - td

        mask = (daily_avg.index >= last_date) & (daily_avg.index <= from_date)
        index = daily_avg.index[mask]    
        daily_avg = daily_avg[daily_avg.index.isin(index)]

    daily_avg = daily_avg[daily_avg.columns].resample('D').mean()

    fig = px.line(
        daily_avg,
        x=daily_avg.index,
        y=options,
        #title="Daily Average",
        labels={
                        "index": "Date",
                        "value": "Occupancy Rate (%)",
                        "variable": "Location"
                    },)

    st.plotly_chart(fig, use_container_width=True)

weekday_mean = daily_avg.groupby(daily_avg.index.dayofweek)[daily_avg.columns].mean()
weekday_mean.index = weekday_mean.index.map(
    {
        0: 'Monday',
        1: 'Tuesday',
        2: 'Wednesday',            
        3: 'Thursday',
        4: 'Friday',            
        5: 'Saturday',
        6: 'Sunday',
    })

fig = px.line(
    weekday_mean,
    x=weekday_mean.index,
    y=options,
    #title="Weekday Average",
    labels={
                    "Date": "Weekday",
                    "value": "Occupancy Rate (%)",
                    "variable": "Location"
                },)

with st.expander("Weekday Average"):
    st.plotly_chart(fig, use_container_width=True)

hours_avg = odh.groupby(odh.index.hour)[odh.columns].mean()      
hours_avg.index = hours_avg.index.map(lambda x: f"{x}:00")
fig = px.line(
    hours_avg,
    x=hours_avg.index,
    y=options,
    #title="Hourly Average",
    labels={
        "Date": "Hour",
        "value": "Occupancy Rate (%)",
        "variable": "Location"
    },)


with st.expander("Hourly Average"):
    st.plotly_chart(fig, use_container_width=True)

weekday_hours_avg = df.groupby([df.index.weekday, df.index.hour])[df.columns].mean()  
weekday_map = {
        0: 'Monday',
        1: 'Tuesday',
        2: 'Wednesday',            
        3: 'Thursday',
        4: 'Friday',            
        5: 'Saturday',
        6: 'Sunday',
    }
fmt = lambda x: f"{weekday_map[x[0]]} {x[1]}:00" 
weekday_hours_avg.index = weekday_hours_avg.index.map(mapper=fmt)
fig = px.line(
    weekday_hours_avg,
    x=weekday_hours_avg.index,
    y=options,
    #title="Weekdays Hourly Average",
    labels={
                    "index": "Weekday-Hour",
                    "value": "Occupancy Rate (%)",
                    "variable": "Location"
                },)

with st.expander("Weekdays Hourly Average"):
    st.plotly_chart(fig, use_container_width=True)