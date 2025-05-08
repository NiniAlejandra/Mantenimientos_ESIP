import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

# Read the CSV file
df = pd.read_csv('MMTO_ACUMULADO_ABRIL.CSV')

# Convert LATITUD and LONGITUD to numeric, replacing any errors with NaN
df['LATITUD'] = pd.to_numeric(df['LATITUD'], errors='coerce')
df['LONGITUD'] = pd.to_numeric(df['LONGITUD'], errors='coerce')

# Remove any rows where LATITUD or LONGITUD is NaN
df = df.dropna(subset=['LATITUD', 'LONGITUD'])

# Create color mapping for different actions
color_map = {
    'Podas': 'green',
    'Correctivo': 'orange',
    'Preventivo': 'purple'
}

# Initialize the Dash app
app = dash.Dash(__name__)
server = app.server

# Define the layout
app.layout = html.Div([
    html.H1("ESIP - Registro de Acciones Operativas 2025", style={'textAlign': 'center'}),
    
    # Filters container
    html.Div([
        # Tipo filter
        html.Div([
            html.Label("Filtrar por Tipo:"),
            dcc.Dropdown(
                id='tipo-filter',
                options=[{'label': tipo, 'value': tipo} for tipo in sorted(df['Tipo'].unique())],
                value=None,
                clearable=True,
                multi=True,  # Enable multiple selection
                style={'width': '100%'}
            )
        ], style={'width': '48%', 'display': 'inline-block', 'margin': '10px'}),
        
        # Mes filter
        html.Div([
            html.Label("Filtrar por Mes:"),
            dcc.Dropdown(
                id='mes-filter',
                options=[{'label': mes, 'value': mes} for mes in sorted(df['Mes'].unique())],
                value=None,
                clearable=True,
                multi=True,  # Enable multiple selection
                style={'width': '100%'}
            )
        ], style={'width': '48%', 'display': 'inline-block', 'margin': '10px'})
    ], style={'display': 'flex', 'justifyContent': 'space-between'}),
    
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
    [Input('tipo-filter', 'value'),
     Input('mes-filter', 'value')]
)
def update_map(selected_tipo, selected_mes):
    # Filter data based on selections
    filtered_df = df.copy()
    
    # Apply Tipo filter if any is selected
    if selected_tipo and len(selected_tipo) > 0:
        filtered_df = filtered_df[filtered_df['Tipo'].isin(selected_tipo)]
    
    # Apply Mes filter if any is selected
    if selected_mes and len(selected_mes) > 0:
        filtered_df = filtered_df[filtered_df['Mes'].isin(selected_mes)]
    
    # Calculate center of the map
    center_lat = filtered_df['LATITUD'].mean()
    center_lon = filtered_df['LONGITUD'].mean()
    
    # Create the map
    fig = px.scatter_mapbox(
        filtered_df,
        lat='LATITUD',
        lon='LONGITUD',
        color='Acción',
        color_discrete_map=color_map,
        hover_name='Sticker',
        hover_data={
            'Acción': False,
            'Tipo': False,
            'Mes': True,
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
                lat=center_lat,
                lon=center_lon
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