"""
    SpectraViewer.visualization.dataset
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This module contains things related to the visualization of datasets.

    :copyright: (c) 2018 by Iván Iglesias
    :license: license_name, see LICENSE for more details
"""
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
from flask import session

from SpectraViewer.processing.Preprocess import PreprocessOperator


def compose_layout():
    """
    Compose and return the layout when visualizing a dataset.

    Returns
    -------
    layout

    """
    from SpectraViewer.utils.mongo_facade import get_user_dataset
    dataset = session['current_dataset']
    user_id = session['user_id']
    dataset_data = get_user_dataset(dataset, user_id)
    metadata = dataset_data.loc[:, ['Nombre', 'Etiqueta', 'Mina', 'Profundidad',
                                    'Profundidad_num']]
    prep = PreprocessOperator('normalize', type='norm')
    prep_options = prep.get_options()
    norm_options = prep_options['normalize']['type']
    squash_options = prep_options['squash']['type']
    smooth_options = prep_options['smooth']['type']
    crop_min = prep_options['crop']['orig'][0]
    crop_max = prep_options['crop']['orig'][1]
    baselines = ['ALS_old', 'airpls', 'als', 'fabc', 'median', 'mpls', 'tophat']
    layout = html.Div(children=[

        html.A(className='btn btn-default', href='/manage',
               children=['Volver a mis archivos']),
        html.Details(children=[
            html.Summary(className='btn btn-default', children='Ayuda'),
            html.Div(className='row', children=[
                html.Div(className='col-md-4', children=[
                    html.Div(className='panel panel-default', children=[
                        html.Div(className='panel-heading',
                                 children=html.H4('Tabla de datos')),
                        html.Div(className='panel-body', children=[
                            html.Ul(children=[
                                html.Li(
                                    'Seleccione en la tabla los ejemplos que quiera representar'),
                                html.Li(
                                    'Se pueden seleccionar varios ejemplos a la vez'),
                                html.Li(
                                    'Pulsando el botón "Filter Rows" aparcen unas cajas de texto en cada columna para filtrar las filas por ese valor'),
                                html.Li(
                                    'Pulsando en el nombre de la columna, se ordena de forma ascendente o descendente')
                            ])
                        ])
                    ])
                ]),
                html.Div(className='col-md-4', children=[
                    html.Div(className='panel panel-default', children=[
                        html.Div(className='panel-heading',
                                 children=html.H4(
                                     'Controles de procesamiento')),
                        html.Div(className='panel-body', children=[
                            html.P(
                                'Cada etiqueta asociada a un control tiene entre paréntesis la letra que lo representa'),
                            html.P(
                                'En el cuadro "Orden de procesado" hay que introducir '
                                'las letras de los controles en el orden que se quiera realizar el procesado'),
                            html.Dl(className='dl-horizontal', children=[
                                html.Dt('Recorte'), html.Dd(
                                    'Muestra los valores entre el rango definido'),
                                html.Dt('Línea base'),
                                html.Dd('Elimina la línea base del gráfico'),
                                html.Dt('Normalización'),
                                html.Dd('Normaliza los valores de los datos'),
                                html.Dt('Aplastado'),
                                html.Dd('Aplasta los valores de los datos'),
                                html.Dt('Suavizado'),
                                html.Dd('Elimina pequeños picos en los datos, '
                                        'se requiere escoger un tipo y un tamaño, '
                                        'cuanto mayor sea el tamaño menos picos quedan'),

                            ])
                        ])
                    ])
                ]),
                html.Div(className='col-md-4', children=[
                    html.Div(className='panel panel-default', children=[
                        html.Div(className='panel-heading',
                                 children=html.H4('Opciones de los gráficos')),
                        html.Div(className='panel-body', children=[
                            html.Ul(children=[
                                html.Li(
                                    'Seleccionando una zona sobre el gráfico se hace zoom en esa parte'),
                                html.Li(
                                    'Haciendo doble click después de hacer zoom se vuelve a la vista general'),
                                html.P('Con varios ejemplos seleccionados:'),
                                html.Ul(children=[
                                    html.Li(
                                        'Haciendo click en el nombre de uno se oculta del gŕafico'),
                                    html.Li(
                                        'Haciendo doble click en el nombre de uno se ocultan el resto'),
                                ]),
                                html.Li(
                                    'El propio gráfico tiene que varias cuya función se muestra al pasar el ratón por encima de su icono')
                            ])
                        ])
                    ])
                ])
            ])
        ])
        ,
        html.H3(f'Dataset {dataset}'),
        html.Div(className='row', children=[
            html.Div(className='col-md-8', children=[
                dt.DataTable(
                    rows=metadata.to_dict('records'),
                    row_selectable=True,
                    filterable=True,
                    sortable=True,
                    editable=False,
                    selected_row_indices=[],
                    max_rows_in_viewport=6,
                    id='metadata'
                )
            ]),
            html.Div(className='col-md-4', children=[
                html.Div(className='form-horizontal', children=[
                    html.Div(className='form-group', children=[
                        html.Label(htmlFor='order',
                                   className='col-md-4 control-label',
                                   children='Orden de procesado'),
                        html.Div(className='col-md-8', children=[
                            dcc.Input(
                                id='order',
                                className='form-control',
                                placeholder='Introduce el orden de procesado',
                                type='text',
                                value='sCBN'
                            )
                        ])
                    ]),
                    html.Div(className='form-group', children=[
                        html.Label(htmlFor='crop-min',
                                   className='col-md-4 control-label',
                                   children='Recorte (min, max) (C)'),
                        html.Div(className='col-md-4', children=[
                            dcc.Input(
                                id='crop-min',
                                min=crop_min,
                                max=crop_max,
                                className='form-control',
                                placeholder=50,
                                type='number',
                                value=50
                            )
                        ]),
                        html.Div(className='col-md-4', children=[
                            dcc.Input(
                                id='crop-max',
                                min=crop_min,
                                max=crop_max,
                                className='form-control',
                                placeholder=2800,
                                type='number',
                                value=1800
                            )
                        ])
                    ]),
                    html.Div(className='form-group', children=[
                        html.Label(htmlFor='baseline',
                                   className='col-md-4 control-label',
                                   children='Línea base (B)'),
                        html.Div(className='col-md-8', children=[
                            dcc.Dropdown(options=[
                                {'label': baseline, 'value': baseline}
                                for baseline in baselines
                            ], value='ALS_old', searchable=False,
                                clearable=False, id='baseline')
                        ])
                    ]),
                    html.Div(className='form-group', children=[
                        html.Label(htmlFor='normalize',
                                   className='col-md-4 control-label',
                                   children='Normalización (N)'),
                        html.Div(className='col-md-8', children=[
                            dcc.Dropdown(options=[
                                {'label': norm_option, 'value': norm_option}
                                for norm_option in norm_options
                            ], value='norm',
                                searchable=False, clearable=False,
                                id='normalize')
                        ])
                    ]),
                    html.Div(className='form-group', children=[
                        html.Label(htmlFor='squash',
                                   className='col-md-4 control-label',
                                   children='Aplastado (S)'),
                        html.Div(className='col-md-8', children=[
                            dcc.Dropdown(options=[
                                {'label': squash_option, 'value': squash_option}
                                for squash_option in squash_options
                            ], value='sqrt',
                                searchable=False, clearable=False,
                                id='squash')
                        ])
                    ]),
                    html.Div(className='form-group', children=[
                        html.Label(htmlFor='smooth-type',
                                   className='col-md-4 control-label',
                                   children='Tipo de suavizado (s)'),
                        html.Div(className='col-md-8', children=[
                            dcc.Dropdown(options=[
                                {'label': smooth_option, 'value': smooth_option}
                                for smooth_option in smooth_options
                            ], value='sg',
                                searchable=False, clearable=False,
                                id='smooth-type')
                        ])
                    ]),
                    html.Div(className='form-group', children=[
                        html.Label(htmlFor='smooth-s',
                                   className='col-md-4 control-label',
                                   children='Ventana de suavizado'),
                        html.Div(className='col-md-8', children=[
                            dcc.Slider(
                                id='smooth-s',
                                min=3,
                                max=35,
                                step=2,
                                marks={i: i for i in range(3, 36, 2)},
                                value=25,
                            ),
                        ])
                    ])

                ]),
            ])
        ]),
        html.Div(className='row', children=[
            html.Div(className='col-md-6', children=[
                dcc.Graph(
                    id='spectrum-original'
                )
            ]),
            html.Div(className='col-md-6', children=[
                dcc.Graph(
                    id='spectrum-processed'
                )
            ])
        ])
    ])

    return layout
