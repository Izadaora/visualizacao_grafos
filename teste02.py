import dash
import dash_cytoscape as cyto
from dash import html, dcc
import networkx as nx
from dash.dependencies import Input, Output, State
import json

def salvar_grafo(grafo, nome_arquivo):
    with open(nome_arquivo, 'w') as f:
        json.dump(nx.node_link_data(grafo), f)  # Salva o grafo no formato JSON

def carregar_grafo(nome_arquivo):
    with open(nome_arquivo, 'r') as f:
        return nx.node_link_graph(json.load(f))  # Carrega o grafo a partir do arquivo JSON

# Inicializando o grafo como um grafo orientado
G = nx.DiGraph()  # Mudança para um grafo orientado

def gerar_elementos_cytoscape(grafo):
    elementos = []
    
    # Adicionar nós
    for node in grafo.nodes():
        elementos.append({
            'data': {'id': node, 'label': node},
            'style': {'backgroundColor': 'lightpink', 'borderColor': 'blue', 'color': 'black', 'width': '60px', 'height': '60px'}
        })
    
    # Adicionar arestas
    for edge in grafo.edges(data=True):
        weight = edge[2].get('weight', 1)  # Usa 1 como peso padrão
        elementos.append({
            'data': {
                'source': edge[0],
                'target': edge[1],
                'label': f'Peso: {weight}'
            },
            'style': {
                'lineColor': 'gray',
                'width': 2,
                'targetArrow': 'triangle',  # Define a seta na extremidade da aresta
                'sourceArrow': 'none'        # Não exibe seta na origem (opcional)
            }
        })
    
    return elementos



# Inicializando o grafo
G = nx.Graph()

app = dash.Dash(__name__)

app.layout = html.Div(
    children=[
        html.H1("Visualização de Grafos", style={'textAlign': 'center'}),
        # Container principal
        html.Div(
            style={'display': 'flex', 'width': '100%', 'height': '100vh'},  # Flexbox para organizar horizontalmente
            children=[
                # Container do grafo
                html.Div(
                    children=[
                        cyto.Cytoscape(
                            id='cytoscape',
                            elements=gerar_elementos_cytoscape(G),
                            style={'width': '100%', 'height': '100%'},
                            layout={'name': 'circle'},
                            zoom=1.0,
                            minZoom=0.3,
                            maxZoom=2.0,
                            boxSelectionEnabled=True,
                            userZoomingEnabled=True,
                            userPanningEnabled=True
                        ),
                    ],
                    style={'width': '60%', 'height': '80vh'}  # Largura do grafo
                ),
                # Container dos botões
                html.Div(
                    style={
                        'width': '30%', 
                        'display': 'flex', 
                        'flexDirection': 'column', 
                        'justifyContent': 'space-around', 
                        'height': '80vh'
                    },
                    children=[
                        html.Div(
                            children=[
                                html.Button("Adicionar Vértice", id='add-node-btn', n_clicks=0),
                                dcc.Input(id='node-name', type='text', placeholder='Nome do Vértice'),
                            ],
                            style={'marginBottom': '10px'}
                        ),
                        html.Div(
                            children=[
                                html.Button("Adicionar Aresta", id='add-edge-btn', n_clicks=0),
                                dcc.Input(id='source-node', type='text', placeholder='Vértice de Origem'),
                                dcc.Input(id='target-node', type='text', placeholder='Vértice de Destino'),
                                dcc.Input(id='edge-weight', type='number', placeholder='Peso da Aresta'),
                            ],
                            style={'marginBottom': '10px'}
                        ),
                        html.Div(
                            children=[
                                html.Button("Remover Vértice", id='remove-node-btn', n_clicks=0),
                                dcc.Input(id='remove-node-name', type='text', placeholder='Nome do Vértice para Remover'),
                            ],
                            style={'marginBottom': '10px'}
                        ),
                        html.Div(
                            children=[
                                html.Button("Remover Aresta", id='remove-edge-btn', n_clicks=0),
                                dcc.Input(id='source-remove', type='text', placeholder='Vértice de Origem'),
                                dcc.Input(id='target-remove', type='text', placeholder='Vértice de Destino'),
                            ],
                            style={'marginBottom': '10px'}
                        ),
                        html.Div(
                            children=[
                                html.Button("Executar BFS", id='bfs-btn', n_clicks=0),
                                html.Button("Executar DFS", id='dfs-btn', n_clicks=0),
                                dcc.Input(id='start-node', type='text', placeholder='Vértice de Início para Busca'),
                            ],
                            style={'marginBottom': '10px'}
                        ),
                        html.Div(
                            children=[
                                html.Button("Zoom In", id="zoom-in-btn", n_clicks=0),
                                html.Button("Zoom Out", id="zoom-out-btn", n_clicks=0),
                            ],
                            style={'marginBottom': '10px'}
                        ),
                        html.Div(
                            children=[
                                html.Button("Salvar Grafo", id='save-graph-btn', n_clicks=0),
                                dcc.Input(id='filename-save', type='text', placeholder='Nome do arquivo para salvar'),
                                html.Button("Carregar Grafo", id='load-graph-btn', n_clicks=0),
                                dcc.Input(id='filename-load', type='text', placeholder='Nome do arquivo para carregar'),
                            ],
                            style={'marginBottom': '10px'}
                        ),
                    ]
                )
            ]
        ),
        # Container das informações do grafo
        html.Div(
            id='info-grafo',
            style={'width': '100%', 'padding': '20px'},
        )
    ],
    style={'display': 'flex', 'flexDirection': 'column'}  # Permitir que o conteúdo cresça verticalmente
)

@app.callback(
    [
        Output('cytoscape', 'elements'),
        Output('info-grafo', 'children'),
        Output('cytoscape', 'zoom'),
        Output('node-name', 'value'),
        Output('source-node', 'value'),
        Output('target-node', 'value'),
        Output('remove-node-name', 'value'),
        Output('source-remove', 'value'),
        Output('target-remove', 'value'),
        Output('start-node', 'value')
    ],
    [
        Input('add-node-btn', 'n_clicks'),
        Input('add-edge-btn', 'n_clicks'),
        Input('remove-node-btn', 'n_clicks'),
        Input('remove-edge-btn', 'n_clicks'),
        Input('zoom-in-btn', 'n_clicks'),
        Input('zoom-out-btn', 'n_clicks'),
        Input('bfs-btn', 'n_clicks'),
        Input('dfs-btn', 'n_clicks'),
        Input('save-graph-btn', 'n_clicks'),
        Input('load-graph-btn', 'n_clicks'),
        Input('cytoscape', 'selectedNodeData')  # Nova entrada para capturar os nós selecionados
    ],
    [
        State('node-name', 'value'),
        State('source-node', 'value'),
        State('target-node', 'value'),
        State('remove-node-name', 'value'),
        State('source-remove', 'value'),
        State('target-remove', 'value'),
        State('edge-weight', 'value'),
        State('cytoscape', 'zoom'),
        State('filename-save', 'value'),
        State('filename-load', 'value'),
    ]
)
def atualizar_grafo_e_buscas(
    add_node_clicks, add_edge_clicks, remove_node_clicks, remove_edge_clicks,
    zoom_in_clicks, zoom_out_clicks,
    bfs_clicks, dfs_clicks,
    save_clicks, load_clicks,
    selected_nodes,  # Novo parâmetro para nós selecionados
    node_name, source_node, target_node, remove_node_name,
    source_remove, target_remove, edge_weight, current_zoom,
    filename_save, filename_load
):
    global G
    ctx = dash.callback_context
    if not ctx.triggered:
        raise dash.exceptions.PreventUpdate

    trigger = ctx.triggered[0]['prop_id'].split('.')[0]
    
    # Variável para controlar se o grafo foi atualizado
    grafo_atualizado = False
    resultado_busca = ""
    
    # Processar zoom
    if trigger == 'zoom-in-btn':
        current_zoom += 0.1  # Aumenta o zoom
    elif trigger == 'zoom-out-btn':
        current_zoom -= 0.1  # Diminui o zoom
    current_zoom = min(max(current_zoom, 0.5), 2.5)  # Limitar o zoom

    # Processar adição/remover vértices
    if trigger == 'add-node-btn' and node_name:
        G.add_node(node_name)
        grafo_atualizado = True
    elif trigger == 'remove-node-btn' and remove_node_name:
        G.remove_node(remove_node_name)
        grafo_atualizado = True
    
    # Processar adição/remover arestas
    if trigger == 'add-edge-btn':
        if len(selected_nodes) == 2:  # Verifica se exatamente 2 nós estão selecionados
            source_node = selected_nodes[0]['id']
            target_node = selected_nodes[1]['id']
            G.add_edge(source_node, target_node, weight=edge_weight)
            grafo_atualizado = True
    elif trigger == 'remove-edge-btn' and source_remove and target_remove:
        G.remove_edge(source_remove, target_remove)
        grafo_atualizado = True
    
    # Processar buscas
    if trigger == 'bfs-btn' and source_node:
        resultado_busca = f"BFS a partir de {source_node}: " + " -> ".join(list(nx.bfs_nodes(G, source_node)))
    elif trigger == 'dfs-btn' and source_node:
        resultado_busca = f"DFS a partir de {source_node}: " + " -> ".join(list(nx.dfs_nodes(G, source_node)))
    
    # Salvar ou carregar o grafo
    if trigger == 'save-graph-btn' and filename_save:
        salvar_grafo(G, filename_save)  # Chama a função para salvar o grafo
    elif trigger == 'load-graph-btn' and filename_load:
        G = carregar_grafo(filename_load)  # Chama a função para carregar o grafo
        grafo_atualizado = True

    # Atualizar grafo
    if grafo_atualizado:
        elementos = gerar_elementos_cytoscape(G)
    else:
        elementos = dash.no_update  # Não atualiza se o grafo não foi modificado

    num_nos = len(G.nodes())
    num_arestas = len(G.edges())
    info_grafo = f"Nós: {num_nos}, Arestas: {num_arestas}"

    # Garantir que todos os valores sejam retornados
    return (
        elementos, 
        info_grafo, 
        current_zoom, 
        "",  # node-name
        "",  # source-node
        "",  # target-node
        "",  # remove-node-name
        "",  # source-remove
        "",  # target-remove
        ""   # start-node
    )

if __name__ == '__main__':
    app.run_server(debug=True)