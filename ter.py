#começa pomderado independente, qnd troca ele apaga e não atuliza tipo nem aresta
import networkx as nx
import dash
import dash_cytoscape as cyto
from dash import html, dcc
import networkx as nx
from dash.dependencies import Input, Output, State
import pandas as pd
import json
import os


# Função para carregar o grafo de um arquivo de texto
def carregar_grafo(arquivo):
    diretorio_atual = os.path.dirname(__file__)
    caminho_arquivo = os.path.join(diretorio_atual, arquivo)
    if not os.path.exists(caminho_arquivo):
        print(f"Arquivo {caminho_arquivo} não encontrado.")
        return
    with open(caminho_arquivo, 'r') as f:
        for linha in f:
            dados = linha.strip().split(',')
            vertice1, vertice2 = dados[0], dados[1]
            # Verifica se há um peso especificado
            if len(dados) == 3:
                peso = int(dados[2])
                G.add_edge(vertice1, vertice2, weight=peso)
            else:
                G.add_edge(vertice1, vertice2)                

# Função para salvar o grafo em um arquivo de texto
def salvar_grafo(arquivo):
    with open(arquivo, 'w') as f:
        for edge in G.edges(data=True):
            weight = edge[2]['weight'] if 'weight' in edge[2] else ''
            f.write(f"{edge[0]},{edge[1]},{weight}\n")

# Inicializando o grafo como um grafo orientado
G = nx.DiGraph()

def gerar_elementos_cytoscape(grafo):
    elementos = []

    # Adicionar os nós
    for node in G.nodes():
        elementos.append({
            'data': {'id': node, 'label': node},
            'style': {
                'backgroundColor': 'lightpink',
                'borderWidth': 2,
                'borderColor': 'black',
                'color': 'black',
                'textValign': 'center',
                'textAnchor': 'middle',
                'width': '60px',  # Ajuste o tamanho aqui
                'height': '60px',  # Ajuste o tamanho aqui
            }
        })

    # Adicionar as arestas
    for edge in G.edges(data=True):
        source, target, data = edge
        label = data.get('weight', '')

        elementos.append({
            'selector': f'edge[source="{source}"][target="{target}"]',
            'data': {
                'source': str(source),
                'target': str(target),
                'label': str(label) if label else ''
            },
            'classes': 'edge',
            'style': {
                'width': '2.8px',
                'target-arrow-color': '#252525',
                'line-color': '#252525',
                'target-arrow-shape': 'triangle' if nx.is_directed(G) else 'none',
                'arrow-scale': 1.3,
                'label': str(label) if label else '',
                'text-background-color': '#ffffff',
                'text-background-opacity': 0.5,
                'text-background-shape': 'round-rectangle',
            }
        })

    return elementos

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
                            layout={'name': 'cose'},
                            zoom=1.0,
                            minZoom=0.5,
                            maxZoom=2.0,
                            boxSelectionEnabled=True,
                            userZoomingEnabled=True,
                            userPanningEnabled=True,
                            stylesheet=[
                                {'selector': 'node', 'style': {'content': 'data(label)', 'text-valign': 'center', 
                                'text-halign': 'center', 'background-color': 'white', 'color': 'black'}},
                                {'selector': 'edge', 'style': {'curve-style': 'bezier', 'target-arrow-shape': 'triangle', 
                                'line-color': 'black', 'target-arrow-color': 'gray', 'label': 'data(weight)', 'color': 'black', 
                                'text-background-color': '#ffffff', 'text-background-opacity': 0.5, 'text-background-shape': 'round-rectangle',}
                                }
                            ],
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
                                html.Button("Remover Vértice", id='remove-node-btn', n_clicks=0, style={'display': 'block'}),
                            ],
                            style={'marginBottom': '10px'}
                        ),
                        html.Div(
                            children=[
                                html.Button("Adicionar Aresta", id='add-edge-btn', n_clicks=0),
                                html.Button("Remover Aresta", id='remove-edge-btn', n_clicks=0),
                                html.P("Selecione 2 nós para adicionar uma aresta"),
                                html.P("Selecione as arestas para removê-las"),
                            ],
                            style={'marginBottom': '10px'}
                        ),
                        html.Div([
                            html.Label('Tipo de Grafo:'),
                            dcc.RadioItems(
                                id='tipo-grafo',
                                options=[
                                    {'label': 'Não Orientado', 'value': 'undirected'},
                                    {'label': 'Orientado', 'value': 'directed'}
                                ],
                                value='undirected'
                            ),
                        ], style={'marginBottom': '10px'}),
                        html.Div([
                            html.Label('Peso nas Arestas:'),
                            dcc.RadioItems(
                                id='peso-aresta',
                                options=[
                                    {'label': 'Sem Peso', 'value': 'none'},
                                    {'label': 'Com Peso', 'value': 'weighted'}
                                ],
                                value='none'
                            ),
                        ], style={'marginBottom': '10px'}),

                        html.Div(
                            children=[
                                html.Button("Adicionar Peso à Aresta", id='add-weight-btn', n_clicks=0),
                                dcc.Input(id='edge-weight', type='number', placeholder='Peso da Aresta'),
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
                                html.Button('Carregar Grafo', id='carregar-grafo', n_clicks=0),
                                html.Button('Salvar Grafo', id='salvar-grafo', n_clicks=0),
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
    Output('cytoscape', 'elements'),
    Output('info-grafo', 'children'),
    Output('cytoscape', 'zoom'),
    Output('node-name', 'value'),
    Output('start-node', 'value'),
    Input('add-node-btn', 'n_clicks'),
    Input('remove-node-btn', 'n_clicks'),
    Input('add-edge-btn', 'n_clicks'),
    Input('remove-edge-btn', 'n_clicks'),
    Input('salvar-grafo', 'n_clicks'),
    Input('carregar-grafo', 'n_clicks'),
    Input('tipo-grafo', 'value'),
    Input('cytoscape', 'selectedNodeData'),
    Input('cytoscape', 'selectedEdgeData'),
    State('node-name', 'value'),
    State('cytoscape', 'zoom'),
    State('edge-weight', 'value')
)
def atualizar_grafo(add_node_clicks, remove_node_clicks, add_edge_clicks,
                     remove_edge_clicks, salvar_grafo_clicks, carregar_grafo_clicks,
                     tipo_grafo, selected_nodes, selected_edges,
                     node_name, current_zoom, edge_weight):

    # Controla as atualizações de acordo com os clicks
    ctx = dash.callback_context

    if not ctx.triggered:
        return gerar_elementos_cytoscape(G), dash.no_update, current_zoom, "", ""

    trigger = ctx.triggered[0]['prop_id'].split('.')[0]

    # Controla a criação do grafo
    if trigger == 'tipo-grafo':
        criar_grafo(tipo_grafo)

    # Executa a ação correspondente
    if trigger == 'carregar-grafo':
        carregar_grafo('grafo.txt')
    elif trigger == 'salvar-grafo':
        salvar_grafo('grafo.txt')

    # Atualiza os elementos do grafo e retorna as informações
    return atualizar_elementos_grafo(trigger, selected_nodes, selected_edges,
                                      node_name, current_zoom, edge_weight)


def criar_grafo(tipo_grafo):
    global G
    if tipo_grafo == 'directed':
        G = nx.DiGraph()
    else:
        G = nx.Graph()

def atualizar_elementos_grafo(trigger, selected_nodes, selected_edges,
                               node_name, current_zoom, edge_weight):
    global G
    grafo_atualizado = False

    # Adicionar vértice
    if trigger == 'add-node-btn' and node_name:
        if node_name not in G.nodes:
            G.add_node(node_name)
            grafo_atualizado = True

    # Remover vértice
    if trigger == 'remove-node-btn' and selected_nodes:
        for node_data in selected_nodes:
            node_to_remove = node_data['id']
            if node_to_remove in G.nodes:
                G.remove_node(node_to_remove)
                grafo_atualizado = True

    # Adicionar aresta
    if trigger == 'add-edge-btn' and len(selected_nodes) == 2:
        source, target = selected_nodes[0]['id'], selected_nodes[1]['id']
        if not G.has_edge(source, target):
            G.add_edge(source, target)
            grafo_atualizado = True

    # Remover aresta
    if trigger == 'remove-edge-btn' and selected_edges:
        for edge_data in selected_edges:
            G.remove_edge(edge_data['source'], edge_data['target'])
        grafo_atualizado = True

    # Adicionar peso à aresta
    if trigger == 'add-weight-btn' and selected_edges and edge_weight:
        for edge_data in selected_edges:
            source, target = edge_data['source'], edge_data['target']
            if G.has_edge(source, target):
                G[source][target]['weight'] = edge_weight
                grafo_atualizado = True

    # Atualiza o grafo e retorna as informações
    if grafo_atualizado:
        return gerar_elementos_cytoscape(G), calcular_informacoes_grafo(), current_zoom, "", ""
    
    return gerar_elementos_cytoscape(G), dash.no_update, current_zoom, "", ""

def calcular_informacoes_grafo():
    num_vertices = len(G.nodes())
    num_arestas = len(G.edges())
    orientado = 'Sim' if isinstance(G, nx.DiGraph) else 'Não'
    ponderado = 'Sim' if any('weight' in G[u][v] for u, v in G.edges()) else 'Não'
    return [
        html.Div(f"Número de Vértices: {num_vertices}"),
        html.Div(f"Número de Arestas: {num_arestas}"),
        html.Div(f"É Orientado: {orientado}"),
        html.Div(f"É Ponderado: {ponderado}")
    ]

if __name__ == '__main__':
    G = nx.DiGraph()
    app.run_server(debug=True)