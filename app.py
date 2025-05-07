import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

# Read the CSV file
df = pd.read_csv('MMTO_ABRIL.csv')

# Create color mapping for different actions
color_map = {
    'Podas': 'green',
    'Correctivo': 'orange',
    'Preventivo': 'purple',
}

# Initialize the Dash app
app = dash.Dash(__name__)
server = app.server

# Define the layout
app.layout = html.Div([
    html.H1("ESIP - Registro de Acciones Abril 2024", style={'textAlign': 'center'}),
    
    # Filter dropdown
    html.Div([
        html.Label("Filtrar por Tipo:"),
        dcc.Dropdown(
            id='tipo-filter',
            options=[{'label': tipo, 'value': tipo} for tipo in sorted(df['Tipo'].unique())],
            value=None,
            clearable=True,
            style={'width': '50%'}
        )
    ], style={'margin': '20px'}),
    
    # Map
    dcc.Graph(
        id='map-graph',
        style={'height': '80vh'},
        config={'scrollZoom': True}
    )
])

# Callback to update the map based on filters
@app.callback(
    Output('map-graph', 'figure'),
    [Input('tipo-filter', 'value')]
)
def update_map(selected_tipo):
    # Filter data if tipo is selected
    filtered_df = df if selected_tipo is None else df[df['Tipo'] == selected_tipo]
    
    # Create the map
    fig = px.scatter_mapbox(
        filtered_df,
        lat='LATITUD',
        lon='LONGITUD',
        color='Acción',
        color_discrete_map=color_map,
        hover_name='Sticker',
        hover_data={
            'Acción': True,
            'Tipo': True,
            'Descripción': True,
            'Estado': True,
            'LATITUD': False,
            'LONGITUD': False
        },
        zoom=12,
        mapbox_style="carto-positron",
        size=[0.6] * len(filtered_df)
    )
    
    # Update layout with mapbox configuration
    fig.update_layout(
        mapbox=dict(
            style="carto-positron",
            center=dict(
                lat=filtered_df['LATITUD'].mean(),
                lon=filtered_df['LONGITUD'].mean()
            ),
            zoom=12
        ),
        margin={"r":0,"t":0,"l":0,"b":0},
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        )
    )
    
    return fig

if __name__ == '__main__':
    app.run(debug=True) 