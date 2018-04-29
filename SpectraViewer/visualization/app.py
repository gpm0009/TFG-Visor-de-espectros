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
from dash.dependencies import Input, Output, State

from SpectraViewer.utils.directories import get_dataset_data, \
    get_user_directory, get_path

# Importing cufflinks is required to able to get the plotly figure from
# a DataFrame, the import binds the DataFrame with the iplot method.
import pandas as pd
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
        html.Div(className='container', children=[
            dcc.Location(id='url', refresh=False),
            html.Div(id='page-content'),
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

    @app.callback(
        Output('class_data', 'options'),
        [Input('class_dropdown', 'value')])
    def change_data(value):
        dataset_data = get_dataset_data(session['current_dataset'])
        try:
            spectra = dataset_data[value]
            return [{'label': spectrum, 'value': spectrum} for spectrum in
                    spectra]
        except KeyError:
            # This happens the first time the page is loaded, no value
            # is selected so KeyError is raised, jus ignore it
            return None

    @app.callback(
        Output('spectrum', 'figure'),
        [Input('class_data', 'value')],
        [State('class_dropdown', 'value')])
    def plot_spectrum(value, class_name):
        user_directory = get_user_directory()
        spectrum_path = get_path(user_directory, session['current_dataset'])
        spectrum_path = get_path(spectrum_path, class_name)
        spectrum_path = get_path(spectrum_path, value)
        df = pd.read_csv(spectrum_path, delimiter=';', header=None)
        df.columns = ['Raman shift', 'Intensity']
        figure = df.iplot(x='Raman shift', y='Intensity', asFigure=True,
                          xTitle='Raman shift', yTitle='Intensity')
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
