"""
    SpectraViewer.visualization
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This module contains all necessary things to manipulate the
    visualization of the graphs.

    :copyright: (c) 2018 by Iván Iglesias
    :license: license_name, see LICENSE for more details
"""
from flask import session, abort
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
from dash.dependencies import Input, Output

import pandas as pd
# Importing cufflinks is required to able to get the plotly figure from
# a DataFrame, the import binds the DataFrame with the iplot method.
import cufflinks

_instance = None


def create_dash_app(server):
    """
    Create the Dash app and initialize it.

    Parameters
    ----------
    server : Flask
        Flask instance

    """
    global _instance
    app = dash.Dash(__name__, server=server, url_base_pathname='/plot/')
    app.config.suppress_callback_exceptions = True

    app.layout = html.Div(children=[
        html.Div(className='container-fluid', children=[
            dcc.Location(id='url', refresh=False),
            html.Div(id='page-content'),
            html.Div(dt.DataTable(rows=[{}]), style={'display': 'none'})
            # This is because of how Dash works
            # (see https://community.plot.ly/t/display-tables-in-dash/4707/40)
        ])
    ])
    app.css.append_css({
        'external_url': 'https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/3.3.7/css/bootstrap.min.css'})

    app.scripts.append_script({'external_url': [
        'https://cdnjs.cloudflare.com/ajax/libs/jquery/1.12.4/jquery.min.js',
        'https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/3.3.7/js/bootstrap.min.js']})

    _add_callbacks(app)

    _instance = app


def set_title(title):
    _instance.title = title


def _add_callbacks(app):
    @app.callback(Output('page-content', 'children'),
                  [Input('url', 'pathname')])
    def display_page(pathname):
        if pathname == '/plot/dataset':
            from SpectraViewer.visualization import dataset
            return dataset.compose_layout()
        elif pathname == '/plot/spectrum/temp':
            data = pd.read_csv(session['temp_file'], sep=';', header=None)
            data.columns = ['Raman shift', 'Intensity']
            figure = data.iplot(x='Raman shift', y='Intensity', asFigure=True,
                                xTitle='Raman shift', yTitle='Intensity')
            return temp_spectrum_layout(figure)
        else:
            abort(404)

    @app.callback(Output('spectrum-original', 'figure'),
                  [Input('metadata', 'rows'),
                   Input('metadata', 'selected_row_indices')])
    def update_spectrum(rows, spectra_index):
        from SpectraViewer.utils.mongo_facade import get_user_dataset
        dataset = session['current_dataset']
        user_id = session['user_id']
        dataset_data = get_user_dataset(dataset, user_id)
        figure = {
            'layout': {
                'xaxis': {'title': 'Raman shift'},
                'yaxis': {'title': 'Intensity'}
            },
            'data': list()
        }
        for i in spectra_index:
            name = rows[i]['Nombre']
            spectrum = dataset_data[dataset_data['Nombre'] == name]
            spectrum = spectrum.drop(
                columns=['Nombre', 'Etiqueta', 'Mina', 'Profundidad',
                         'Profundidad_num'])
            figure['data'].append({
                'x': spectrum.columns.tolist(),
                'y': spectrum.values[0],
                'name': f'{name}'
            })
        return figure


def temp_spectrum_layout(figure):
    """
    Build and set the layout for the Dash application.

    Receives the figure returned by the iplot() method and returns the
    layout of the Dash application with that figure.

    Parameters
    ----------
    figure : plotly Figure
        The figure which will be represented.
    title : str
        Title of the web page.

    """
    layout = html.Div(children=[
        html.A(className='btn btn-default', href='/',
               children=['Volver a la página principal']),
        html.Div(className='page-header', children=[
            html.H2('Visualización del espectro')
        ]),
        dcc.Graph(
            id='spectrum',
            figure=figure
        )
    ])
    return layout
