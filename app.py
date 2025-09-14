
import pandas as pd
import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc

calendar_df = pd.read_excel("Events Dashboard.xlsx", sheet_name="EGC Calendar", engine="openpyxl")
calendar_df['Date'] = pd.to_datetime(calendar_df['Date'], errors='coerce', dayfirst=True)
calendar_df = calendar_df.dropna(subset=['Date'])
calendar_df['Month'] = calendar_df['Date'].dt.strftime('%B')
calendar_df['MonthNum'] = calendar_df['Date'].dt.month
calendar_df.sort_values('MonthNum', inplace=True)

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container([
    html.H2("Golf Events Dashboard", className="text-center my-4"),
    dbc.Row([
        dbc.Col([
            html.H4("Event Details"),
            html.Div(id='event-details', style={'border': '1px solid #ccc', 'padding': '10px'})
        ], width=6),
        dbc.Col([
            html.H4("Select Month"),
            dbc.ButtonGroup([
                dbc.Button(month, id={'type': 'month-button', 'index': month}, n_clicks=0)
                for month in calendar_df['Month'].unique()
            ], className="mb-3"),
            html.H5("Events in Selected Month"),
            html.Ul(id='event-list', style={'listStyleType': 'none', 'paddingLeft': '0'})
        ], width=6)
    ])
], fluid=True)

@app.callback(
    Output('event-list', 'children'),
    Input({'type': 'month-button', 'index': dash.dependencies.ALL}, 'n_clicks')
)
def update_event_list(n_clicks):
    ctx = dash.callback_context
    if not ctx.triggered:
        return []
    month_clicked = ctx.triggered[0]['prop_id'].split('.')[0]
    month = eval(month_clicked)['index']
    filtered_df = calendar_df[calendar_df['Month'] == month]
    return [html.Li(html.Button(event, id={'type': 'event-button', 'index': i}, n_clicks=0,
                                style={'width': '100%', 'textAlign': 'left', 'marginBottom': '5px'}))
            for i, event in filtered_df['Event Name'].items()]

@app.callback(
    Output('event-details', 'children'),
    Input({'type': 'event-button', 'index': dash.dependencies.ALL}, 'n_clicks')
)
def display_event_details(n_clicks):
    ctx = dash.callback_context
    if not ctx.triggered:
        return "Select an event to see details."
    event_index = eval(ctx.triggered[0]['prop_id'].split('.')[0])['index']
    event_data = calendar_df.iloc[event_index]
    return html.Div([
        html.P(f"{col}: {event_data[col]}") for col in calendar_df.columns if pd.notna(event_data[col])
    ])

if __name__ == '__main__':
    app.run_server(debug=True)
