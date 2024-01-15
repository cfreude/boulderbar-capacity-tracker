from dash import Dash, html, dcc, callback, Output, Input
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
from datetime import datetime
from pytz import timezone  

from logger import BoulderbarCapacityLogger
#df = BoulderbarCapacityLogger.data_frame()

import requests
response = requests.get('https://welcomed-thrush-sacred.ngrok-free.app/')
df = pd.read_json(response.json())

import flask
server = flask.Flask(__name__)

app = Dash(__name__, external_stylesheets=[dbc.themes.MINTY], server=server, routes_pathname_prefix="/")

app.layout = html.Div([
    html.H1(children='Boulderbar Dashboard', style={'textAlign':'center'}),
    html.Div([
        html.A("https://boulderbar.net/", href='https://boulderbar.net/', target="_blank"),
        html.H6(children='Overview of current, recorded and statistical occupancy rate data of the Boulderbars.', style={'textAlign':'center', 'margin': '10px'})],
        style={'textAlign':'center'}),
    dcc.Checklist(
        df.columns,
        ['Hannovergasse', 'Wienerberg', 'Hauptbahnhof', 'Seestadt'],
        inline=True,
        style={'textAlign':'center'}, 
        inputStyle={"margin": "20px", "marginRight": "5px", "marginLeft": "15px"},
        id='selection'
        ),
    dcc.Graph(id='current'),
    dcc.Graph(id='timeline'),
    dcc.Graph(id='daily-avg'),    
    dcc.Graph(id='weekday-avg'),     
    dcc.Graph(id='hourly-avg'),        
    dcc.Graph(id='weekday-hourly-avg'),
], style={"margin": "20px"},)

@callback(
    Output('current', 'figure'),
    Input('selection', 'value')
)
def update_current(value):
    vienna = timezone('Africa/Johannesburg')
    vienna_time = datetime.now(vienna)
    time_str = vienna_time.strftime('%d.%m.%Y, %H:%M:%S')

    current = BoulderbarCapacityLogger.fetch_capacities_df()
    current = current[current.index.isin(value)]  

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
    return fig

@callback(
    Output('timeline', 'figure'),
    Input('selection', 'value')
)
def update_timeline(value):
    return px.line(
        df,
        x=df.index,
        y=value,
        title="Timeline",
        labels={
                     "Date": "Date",
                     "value": "Occupancy Rate (%)",
                     "variable": "Location"
                 },)

@callback(
    Output('daily-avg', 'figure'),
    Input('selection', 'value')
)
def update_daily_avg(value):    
    # mask the hours we want
    hours = df.index.hour
    mask = (hours >= 9) & (hours <= 23)
    odh = df[mask]
    daily_avg = odh[odh.columns].resample('D').mean()
    return px.line(
        daily_avg,
        x=daily_avg.index,
        y=value,
        title="Daily Average",
        labels={
                     "Day": "Date",
                     "value": "Occupancy Rate (%)",
                     "variable": "Location"
                 },)

@callback(
    Output('weekday-avg', 'figure'),
    Input('selection', 'value')
)
def update_weekday_avg(value):    
    # mask the hours we want
    hours = df.index.hour
    mask = (hours >= 9) & (hours <= 23)
    odh = df[mask]
    daily_avg = odh[odh.columns].resample('D').mean()
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
    return px.line(
        weekday_mean,
        x=weekday_mean.index,
        y=value,
        title="Weekday Average",
        labels={
                     "Date": "Weekday",
                     "value": "Occupancy Rate (%)",
                     "variable": "Location"
                 },)

@callback(
    Output('hourly-avg', 'figure'),
    Input('selection', 'value')
)
def update_hourly_avg(value):    
    # mask the hours we want
    hours = df.index.hour
    mask = (hours >= 8) & (hours <= 24)
    odh = df[mask]
    hours_avg = odh.groupby(odh.index.hour)[odh.columns].mean()      
    hours_avg.index = hours_avg.index.map(lambda x: f"{x}:00")  
    '''
    weekday_hours.index = weekday_hours.index.map(
        {
            0: 'Monday',
            1: 'Tuesday',
            2: 'Wednesday',            
            3: 'Thursday',
            4: 'Friday',            
            5: 'Saturday',
            6: 'Sunday',
        })
    '''
    return px.line(
        hours_avg,
        x=hours_avg.index,
        y=value,
        title="Hourly Average",
        labels={
                     "Date": "Hour",
                     "value": "Occupancy Rate (%)",
                     "variable": "Location"
                 },)


@callback(
    Output('weekday-hourly-avg', 'figure'),
    Input('selection', 'value')
)
def update_weekday_hourly_avg(value): 
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
    return px.line(
        weekday_hours_avg,
        x=weekday_hours_avg.index,
        y=value,
        title="Weekdays Hourly Average",
        labels={
                     "index": "Weekday-Hour",
                     "value": "Occupancy Rate (%)",
                     "variable": "Location"
                 },)

if __name__ == '__main__':
    app.run(debug=True)