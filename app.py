import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go

from scipy.stats import zscore
import umap

import pandas as pd

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets,
                suppress_callback_exceptions=True, title='Scatter Plot')

app.layout= html.Div(
    children= [

        html.H3('UMAP Visualization'),
        dcc.Link('Source code', href='https://github.com/tashrifbillah/dash-umap-demo',
                 target='blank'),
        html.Br(),
        dcc.Link('UMAP basics', href='https://umap-learn.readthedocs.io/en/latest/parameters.html',
                 target='blank'),
        html.Hr(),
        html.Br(),

        'n_neighbors: ',
        html.Div(
            dcc.Slider(
                id="neighbors", value=15,
                marks={i: str(i) for i in range(0,201,20)},
                min=2, max=200, step=1
            ),
            style={'width':'700px'}
        ),

        html.Br(),

        'min_dist: ',
        dcc.Input(
            id="min_dist", type="number", value=0.1,
            min=0, max=0.99, step=0.1,
        ),

        dcc.Loading(id='UMAP plot', fullscreen= False, type='graph'),
        html.Br(),
        dcc.Graph(id='umap-plot'),
    ],
    style={'margin':'30px'}
)


@app.callback([Output('umap-plot', 'figure'),
               Output('UMAP plot', 'children')],
              [Input('neighbors', 'value'),
               Input('min_dist', 'value')])
def umap_plot(n_neighbors, min_dist):

    try:
        n_neighbors= int(n_neighbors)
    except:
        n_neighbors= 2

    try:
        min_dist= float(min_dist)
    except:
        min_dist= 0.1

    ## load data ##
    data = pd.read_csv('data/anage_data_subset.csv')

    ## process data ##
    names = data.values[:, 0:8]
    props = data.values[:, 8:16].astype(float)
    props = zscore(props, ddof=1)

    ## perform UMAP ##
    P = umap.UMAP(n_neighbors=n_neighbors, min_dist=min_dist).fit_transform(props)

    ## define data to plot ##
    groups= data.groupby(['Class']).groups
    palette=['red','blue']
    plotdata= []
    for i,fclass in enumerate(groups.keys()):
        ind=groups.get(fclass)
        plotdata.append(
            dict(
                x= P[:,0][ind],
                y= P[:,1][ind],
                text= [f'{g} {s}' for g,s in zip(data['Genus'].values[ind],data['Species'].values[ind])],
                mode= 'markers',
                name= fclass,
                marker = {
                    'size': 15,
                    'opacity': 0.5,
                    'color': palette[i]
                }
            )
        )

    ## set plot properties ##
    fig = go.Figure({
        'data': plotdata,
        'layout': dict(
            xaxis={
                'title': 'dim 1'
            },
            yaxis={
                'title': 'dim 2'
            },
            margin={'l': 30, 'r': 30, 'b': 30, 't': 30},
            hovermode='closest',
            height=500,
            width=700
        )
    })

    return fig,True


if __name__=='__main__':
    app.run_server(debug=True)
