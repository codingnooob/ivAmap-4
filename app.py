import pandas as pd
import plotly.graph_objects as go
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc

# Load the CSV file
df = pd.read_csv('iphone-market-share-by-country-2024.csv')

# Create the 'Dominant_Platform' column
df['Dominant_Platform'] = df.apply(lambda row: 'iOS' if row['iOS_Percentage'] > 50 else 'Android', axis=1)

# Create the map figure
fig = go.Figure()

# Add the choropleth map trace
fig.add_trace(go.Choropleth(
    locations=df['Country'],
    z=df['Dominant_Platform'].map({'iOS': 1, 'Android': 0}),
    text=df['Country'],
    colorscale=['#A4C639', '#999999', '#5BC236'],  # Android green, Neutral grey, iOS green
    autocolorscale=False,
    marker_line_color='darkgray',
    marker_line_width=0.5,
))

# Customize the layout
fig.update_layout(
    title_text='Dominant Mobile Platform by Country',
    geo=dict(
        showframe=False,
        showcoastlines=True,
        projection_type='equirectangular'
    ),
)

# Initialize the Dash app
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Add meta tags to prevent zooming
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
        <style>
                body, html {
                overflow: hidden;
                    width: 100%;
                    height: 100%;
                margin: 0;
                padding: 0;
            }
                #map-container {
                width: 100%;
                height: 100vh;
                position: fixed;
                top: 0;
                left: 0;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

app.layout = html.Div([
    html.Div([
        dcc.Graph(
            id='map',
            figure=fig,
            config={
                'displayModeBar': True,
                'modeBarButtonsToRemove': ['select', 'lasso2d', 'autoScale2d'],
                'displaylogo': False,
                'scrollZoom': True,
            },
            style={'width': '100%', 'height': '100%'}
        )
    ], id='map-container'),
    html.Script('''
        document.addEventListener('touchmove', function(e) {
            e.preventDefault();
        }, { passive: false });
    ''')
], id='main-container')

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
