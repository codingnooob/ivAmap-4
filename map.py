import pandas as pd
import plotly.graph_objects as go
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import base64
import io

# Initialize the Dash app
app = dash.Dash(__name__)
server = app.server  # For deployment if needed

# App layout
app.layout = html.Div([
    html.H1('iOS vs Android Market Share Map'),
    html.H3('Upload a CSV file with your data'),
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select CSV File')
        ]),
        style={
            'width': '60%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '2px',
            'borderStyle': 'dashed',
            'borderRadius': '10px',
            'textAlign': 'center',
            'margin': '20px auto'
        },
        multiple=False
    ),
    html.Div(id='output-map')
])

@app.callback(
    Output('output-map', 'children'),
    Input('upload-data', 'contents'),
    State('upload-data', 'filename')
)
def update_output(content, filename):
    if content is not None:
        # Parse the uploaded file
        content_type, content_string = content.split(',')
        decoded = base64.b64decode(content_string)
        try:
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        except Exception as e:
            return html.Div([f'Error processing the file: {str(e)}'])

        # Validate required columns
        required_columns = {'Country', 'iOS_Percentage', 'Android_Percentage'}
        if not required_columns.issubset(df.columns):
            return html.Div([f'Missing required columns. Please ensure your CSV file contains: {", ".join(required_columns)}'])

        # Process the data
        df['iOS_Percentage'] = pd.to_numeric(df['iOS_Percentage'], errors='coerce')
        df['Android_Percentage'] = pd.to_numeric(df['Android_Percentage'], errors='coerce')
        df['Dominant_Platform'] = df.apply(lambda row: 'iOS' if row['iOS_Percentage'] > 50 else 'Android', axis=1)

        # Create the map
        fig = go.Figure()

        # Add the choropleth map trace
        fig.add_trace(go.Choropleth(
            locations = df['Country'],
            locationmode = 'country names',
            showlegend = False,
            z = df['Dominant_Platform'].map({'iOS': 1, 'Android': 0}),
            text = df['Country'],
            colorscale = [[0, '#2ca02c'], [1, '#1f77b4']],
            showscale = False,
            hoverinfo = "text"
        ))

        # Update layout
        fig.update_geos(
            showcoastlines = True,
            coastlinecolor = "RebeccaPurple",
            showland = True,
            landcolor = "LightGrey",
            showocean = True,
            oceancolor = "LightBlue",
            showlakes = False,
            showrivers = False,
            showcountries = True,
            countrycolor = "white",
            countrywidth = 0.5,
            projection_type = "natural earth"
        )

        fig.update_layout(
            title_text = 'iOS vs Android Market Share by Country',
            geo = dict(
                showframe = False,
            ),
            margin={"r":0,"t":40,"l":0,"b":0},
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )

        # Add hover information
        hover_text = [
            f"{country}<br>iOS: {ios}%<br>Android: {android}%" 
            for country, ios, android in zip(df['Country'], df['iOS_Percentage'], df['Android_Percentage'])
        ]
        fig.update_traces(hovertext=hover_text)

        # Add custom legend
        fig.add_trace(go.Scattergeo(
            lon=[None], lat=[None], mode='markers',
            marker=dict(size=10, color='#1f77b4'),  # Blue for iOS
            name='iOS'
        ))
        fig.add_trace(go.Scattergeo(
            lon=[None], lat=[None], mode='markers',
            marker=dict(size=10, color='#2ca02c'),  # Green for Android
            name='Android'
        ))

        # Update legend layout
        fig.update_layout(
            legend_title_text='Dominant Platform',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )

        return dcc.Graph(
            figure=fig,
            config={
                'displayModeBar': True,
                'modeBarButtonsToRemove': ['select', 'lasso2d', 'autoScale2d'],
                'displaylogo': False,
                'scrollZoom': True,
            },
            style={'width': '100%', 'height': '80vh'}
        )

    return html.Div(['Please upload a CSV file to display the map.'])

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)