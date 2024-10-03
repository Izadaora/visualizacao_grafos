import dash
import dash_cytoscape as cyto
from dash import html, dcc
import sys
import os
import networkx as nx
from dash.dependencies import Input, Output, State
import json

# Função para carregar o grafo de um arquivo de texto
def carregar_grafo(arquivo):
    diretorio_atual = os.path.dirname(__file__)
    caminho_arquivo = os.path.join(diretorio_atual, arquivo)
    with open(caminho_arquivo, 'r') as f:
        for linha in f:
            dados = linha.strip().split(',')
            vertice1, vertice2 = dados[0], dados[1]
            if len(dados) == 3:
                peso = int(dados[2])
                G.add_edge(vertice1, vertice2, weight=peso)
            else:
                G.add_edge(vertice1, vertice2)

# Função para salvar o grafo em um arquivo de texto
def salvar_grafo(arquivo):
    with open(arquivo, 'w') as f:
        for edge in G.edges():
            f.write(f"{edge[0]},{edge[1]}\n")
            
# Inicializando o grafo como um grafo orientado
G = nx.DiGraph()
ponderado = False  # Flag para controlar se o grafo é ponderado

def gerar_elementos_cytoscape(grafo):
    elementos = []

    # Adicionar os nós
    for node in G.nodes():
        elementos.append({
            'data': {'id': node, 'label': node},
            'style': {
                'backgroundColor': '#d5d8dc',
                'borderWidth': 2,
                'borderColor': 'black',
                'color': 'black',
                'textValign': 'center',
                'textAnchor': 'middle',
                'width': '60px',
                'height': '60px',
            }
        })

    # Adicionar as arestas
    for edge in G.edges(data=True):
        source, target, data = edge
        label = data.get('weight', '') if ponderado else ''  # Mostrar peso se ponderado

        elementos.append({
            'data': {
                'source': str(source),
                'target': str(target),
                'label': str(label) if label else ''
            },
            'style': {
                'width': '2.8px',
                'target-arrow-color': 'black',
                'line-color': 'black',
                'target-arrow-shape': 'triangle' if nx.is_directed(G) else 'none',
                'arrow-scale': 1.3,
                'label': str(label) if label else '',
                'text-color': '#d5d8dc',
                'text-background-opacity': 0.8,
                'text-background-shape': 'round-rectangle',
            }
        })

    return elementos

app = dash.Dash(__name__)

app.layout = html.Div(
    children=[
        html.H1("Visualização de Grafos", style={'textAlign': 'center', 'fontFamily': 'Courier', 'color': 'black'}),
        # Container principal
        html.Div(
            style={'display': 'flex', 'width': '100%', 'height': '100vh', 'position': 'relative', 'backgroundColor': 'white'},
            children=[
                # Container do grafo
                html.Div(
                    children=[
                        cyto.Cytoscape(
                            id='cytoscape',
                            elements=gerar_elementos_cytoscape(G),
                            style={'width': '100%', 'height': '100%','border': '1px solid black', 'borderRadius': '5px'},
                            layout={'name': 'cose'},
                            zoom=0.8,
                            minZoom=0.5,
                            maxZoom=2.0,
                            boxSelectionEnabled=True,
                            userZoomingEnabled=True,
                            userPanningEnabled=True,
                            stylesheet=[
                                {'selector': 'node', 'style': {'content': 'data(label)', 'text-valign': 'center', 
                                'text-halign': 'center', 'background-color': 'white', 'color': '#81F7D8'}},
                                {'selector': 'edge', 'style': {'curve-style': 'bezier', 'target-arrow-shape': 'triangle' if nx.is_directed else 'none', 
                                'line-color': 'black', 'target-arrow-color': 'gray', 'label': 'data(weight)', 'color': 'black', 
                                'text-background-color': '#ffffff', 'text-background-opacity': 0.5, 'text-background-shape': 'round-rectangle',}
                                }
                            ],
                        ),
                        # Informações do grafo sobrepostas no mesmo container
                        html.Div(
                            id='info-grafo',
                            style={
                                'position': 'absolute', 
                                'top': '10px', 
                                'left': '10px',
                                'color': 'black',
                                'backgroundColor': 'white', 
                                'padding': '10px',
                                'border': '1px solid black',
                                'borderRadius': '5px',
                                'zIndex': '1000'  # Mantém o div acima do grafo
                            },
                        ),
                    ],
                    style={'width': '80%', 'height': '80vh', 'position': 'relative'}  # Largura do grafo com a div relativa
                ),
                # Container dos botões
                html.Div(
                    style={
                        'width': '20%', 
                        'display': 'flex', 
                        'flexDirection': 'column', 
                        'justifyContent': 'space-around', 
                        'height': '80vh',
                        'border': '1px solid black', 
                        'borderRadius': '5px',
                    },
                    children=[
                        html.Div(
                            children=[
                                html.Button("Adicionar Vértice", id='add-node-btn', n_clicks=0, style={ \
                                        'backgroundColor': '#d5d8dc', 
                                        'color': 'black',             
                                        'border': '1px solid black',
                                        'padding': '5px 5px',       
                                        'textAlign': 'center',        
                                        'fontSize': '14px',           
                                        'margin': '5px',             
                                        'cursor': 'pointer',          
                                        'borderRadius': '5px',        
                                        'width': '95%'                 
                                    }),
                                dcc.Input(id='node-name', type='text', placeholder='Nome do Vértice', style={ \
                                        'backgroundColor': '#d5d8dc', 
                                        'color': 'black',             
                                        'border': '1px solid black',
                                        'padding': '5px 5px',       
                                        'textAlign': 'center',        
                                        'fontSize': '14px',           
                                        'margin': '5px',             
                                        'cursor': 'pointer',          
                                        'borderRadius': '5px',        
                                        'width': '91%'                 
                                    }),
                                html.Button("Remover Vértice", id='remove-node-btn', n_clicks=0, style={'display': 'block',
                                        'backgroundColor': '#d5d8dc', 
                                        'color': 'black',             
                                        'border': '1px solid black',
                                        'padding': '5px 5px',       
                                        'textAlign': 'center',        
                                        'fontSize': '14px',           
                                        'margin': '5px',             
                                        'cursor': 'pointer',          
                                        'borderRadius': '5px',        
                                        'width': '95%'                 
                                    } ),
                            ],
                            style={'marginBottom': '10px'}
                        ),
                        html.Div(
                            children=[
                                html.Button("Adicionar Aresta", id='add-edge-btn', n_clicks=0, style={'display': 'block',
                                        'backgroundColor': '#d5d8dc', 
                                        'color': 'black',             
                                        'border': '1px solid black',
                                        'padding': '5px 5px',       
                                        'textAlign': 'center',        
                                        'fontSize': '14px',           
                                        'margin': '5px',             
                                        'cursor': 'pointer',          
                                        'borderRadius': '5px',        
                                        'width': '95%'                 
                                    } ),
                                html.Button("Remover Aresta", id='remove-edge-btn', n_clicks=0, style={'display': 'block',
                                        'backgroundColor': '#d5d8dc', 
                                        'color': 'black',             
                                        'border': '1px solid black',
                                        'padding': '5px 5px',       
                                        'textAlign': 'center',        
                                        'fontSize': '14px',           
                                        'margin': '5px',             
                                        'cursor': 'pointer',          
                                        'borderRadius': '5px',        
                                        'width': '95%'                 
                                    } ),
                            ],
                            style={'marginBottom': '10px'}
                        ),
                        html.Div(
                            children=[
                                html.Button("Adicionar Peso à Aresta", id='add-weight-btn', n_clicks=0, style={'display': 'block',
                                        'backgroundColor': '#d5d8dc', 
                                        'color': 'black',             
                                        'border': '1px solid black',
                                        'padding': '5px 5px',       
                                        'textAlign': 'center',        
                                        'fontSize': '14px',           
                                        'margin': '5px',             
                                        'cursor': 'pointer',          
                                        'borderRadius': '5px',        
                                        'width': '95%'                 
                                    } ),
                                dcc.Input(id='edge-weight', type='number', placeholder='Peso da Aresta', style={'display': 'block',
                                        'backgroundColor': '#d5d8dc', 
                                        'color': 'black',             
                                        'border': '1px solid black',
                                        'padding': '5px 5px',       
                                        'textAlign': 'center',        
                                        'fontSize': '14px',           
                                        'margin': '5px',             
                                        'cursor': 'pointer',          
                                        'borderRadius': '5px',        
                                        'width': '91%'                 
                                    } ),
                            ],
                            style={'marginBottom': '10px'}
                        ),
                        html.Div(
                            children=[
                                html.Button("Executar BFS", id='bfs-btn', n_clicks=0, style={'display': 'block',
                                        'backgroundColor': '#d5d8dc', 
                                        'color': 'black',             
                                        'border': '1px solid black',
                                        'padding': '5px 5px',       
                                        'textAlign': 'center',        
                                        'fontSize': '14px',           
                                        'margin': '5px',             
                                        'cursor': 'pointer',          
                                        'borderRadius': '5px',        
                                        'width': '95%'                 
                                    } ),
                                html.Button("Executar DFS", id='dfs-btn', n_clicks=0, style={'display': 'block',
                                        'backgroundColor': '#d5d8dc', 
                                        'color': 'black',             
                                        'border': '1px solid black',
                                        'padding': '5px 5px',       
                                        'textAlign': 'center',        
                                        'fontSize': '14px',           
                                        'margin': '5px',             
                                        'cursor': 'pointer',          
                                        'borderRadius': '5px',        
                                        'width': '95%'                 
                                    } ),
                            ],
                            style={'marginBottom': '10px'}
                        ),
                        html.Div(
                            children=[
                                html.Button("Zoom In", id="zoom-in-btn", n_clicks=0, style={'display': 'block',
                                        'backgroundColor': '#d5d8dc', 
                                        'color': 'black',             
                                        'border': '1px solid black',
                                        'padding': '5px 5px',       
                                        'textAlign': 'center',        
                                        'fontSize': '14px',           
                                        'margin': '5px',             
                                        'cursor': 'pointer',          
                                        'borderRadius': '5px',        
                                        'width': '95%'                 
                                    } ),
                                html.Button("Zoom Out", id="zoom-out-btn", n_clicks=0, style={'display': 'block',
                                        'backgroundColor': '#d5d8dc', 
                                        'color': 'black',             
                                        'border': '1px solid black',
                                        'padding': '5px 5px',       
                                        'textAlign': 'center',        
                                        'fontSize': '14px',           
                                        'margin': '5px',             
                                        'cursor': 'pointer',          
                                        'borderRadius': '5px',        
                                        'width': '95%'                 
                                    } ),
                            ],
                            style={'marginBottom': '10px'}
                        ),
                        html.Div(
                            children=[
                                html.Button("Trocar Orientação", id='toggle-directed-btn', n_clicks=0, style={'display': 'block',
                                        'backgroundColor': '#d5d8dc', 
                                        'color': 'black',             
                                        'border': '1px solid black',
                                        'padding': '5px 5px',       
                                        'textAlign': 'center',        
                                        'fontSize': '14px',           
                                        'margin': '5px',             
                                        'cursor': 'pointer',          
                                        'borderRadius': '5px',        
                                        'width': '95%'                 
                                    } ),
                                html.Button("Trocar Ponderação", id='toggle-weight-btn', n_clicks=0, style={'display': 'block',
                                        'backgroundColor': '#d5d8dc', 
                                        'color': 'black',             
                                        'border': '1px solid black',
                                        'padding': '5px 5px',       
                                        'textAlign': 'center',        
                                        'fontSize': '14px',           
                                        'margin': '5px',             
                                        'cursor': 'pointer',          
                                        'borderRadius': '5px',        
                                        'width': '95%'                 
                                    } ),
                            ],
                            style={'marginBottom': '10px'}
                        ),
                        html.Div(
                            children=[
                                html.Button('Salvar Grafo', id='salvar-grafo', n_clicks=0, style={'display': 'block',
                                        'backgroundColor': '#d5d8dc', 
                                        'color': 'black',             
                                        'border': '1px solid black',
                                        'padding': '5px 5px',       
                                        'textAlign': 'center',        
                                        'fontSize': '14px',           
                                        'margin': '5px',             
                                        'cursor': 'pointer',          
                                        'borderRadius': '5px',        
                                        'width': '95%'                 
                                    } ),
                                 html.Button('Carregar Grafo', id='carregar-grafo', n_clicks=0, style={'display': 'block',
                                        'backgroundColor': '#d5d8dc', 
                                        'color': 'black',             
                                        'border': '1px solid black',
                                        'padding': '5px 5px',       
                                        'textAlign': 'center',        
                                        'fontSize': '14px',           
                                        'margin': '5px',             
                                        'cursor': 'pointer',          
                                        'borderRadius': '5px',        
                                        'width': '95%'                 
                                    } ),
                            ],
                            style={'marginBottom': '10px'}
                        ),
                    ]
                )
            ]
        )
    ],
    style={'display': 'flex', 'flexDirection': 'column','backgroundColor': 'white', 'color': 'white'} # Permitir que o conteúdo cresça verticalmente
)

@app.callback(
    [
        Output('cytoscape', 'elements'),
        Output('info-grafo', 'children'),
        Output('cytoscape', 'zoom'),
        Output('node-name', 'value')
    ],
    [
        Input('add-node-btn', 'n_clicks'),
        Input('add-edge-btn', 'n_clicks'),
        Input('add-weight-btn', 'n_clicks'),
        Input('remove-node-btn', 'n_clicks'),
        Input('remove-edge-btn', 'n_clicks'),
        Input('zoom-in-btn', 'n_clicks'),
        Input('zoom-out-btn', 'n_clicks'),
        Input('bfs-btn', 'n_clicks'),
        Input('dfs-btn', 'n_clicks'),
        Input('carregar-grafo', 'n_clicks'),
        Input('salvar-grafo', 'n_clicks'),
        Input('toggle-weight-btn', 'n_clicks'),
        Input('toggle-directed-btn', 'n_clicks'),
        Input('cytoscape', 'selectedNodeData'),
        Input('cytoscape', 'selectedEdgeData')
    ],
    [
        State('node-name', 'value'),
        State('edge-weight', 'value'),
        State('cytoscape', 'zoom')
    ]
)
def atualizar_grafo_e_buscas(
    add_node_clicks, add_edge_clicks, add_weight_clicks,
    remove_node_clicks, remove_edge_clicks,
    zoom_in_clicks, zoom_out_clicks,
    bfs_clicks, dfs_clicks,
    n_clicks_carregar_grafo, n_clicks_salvar_grafo,
    toggle_directed_clicks, toggle_weight_clicks,
    selected_nodes, selected_edges,
    node_name, current_zoom=None,
    edge_weight=None
):
    global G, ponderado

    node_name_output = dash.no_update

    trigger = dash.callback_context.triggered[0]['prop_id'].split('.')[0]
    grafo_atualizado = False
    resultado_busca = ""

    if trigger == 'toggle-directed-btn':
        if G.is_directed():
            G_novo = nx.Graph()
            # Adiciona nós e arestas do grafo orientado
            G_novo.add_nodes_from(G.nodes(data=True))
            for u, v, data in G.edges(data=True):
                # Adiciona a aresta com o peso
                G_novo.add_edge(u, v, weight=data.get('weight', 1))
            G = G_novo
        else:
            G_novo = nx.DiGraph()
            # Adiciona nós e arestas do grafo não orientado
            G_novo.add_nodes_from(G.nodes(data=True))
            for u, v, data in G.edges(data=True):
                # Adiciona a aresta com o peso
                G_novo.add_edge(u, v, weight=data.get('weight', 1))
            G = G_novo
        grafo_atualizado = True

    if trigger == 'toggle-weight-btn':
        ponderado = not ponderado
        for u, v, data in G.edges(data=True):
            if ponderado:
                if 'weight' not in data:
                    data['weight'] = 1
            else:
                if 'weight' in data:
                    del data['weight']
        grafo_atualizado = True

    if current_zoom is None:
        current_zoom = 1.0 

    if trigger == 'zoom-in-btn':
        current_zoom += 0.1
    elif trigger == 'zoom-out-btn':
        current_zoom -= 0.1
    
    if trigger == 'add-node-btn' and node_name:
        if node_name not in G.nodes:
            G.add_node(node_name)
            grafo_atualizado = True
            node_name_output = ""
    
    if trigger == 'add-edge-btn':
        if selected_nodes and len(selected_nodes) == 2:
            u, v = selected_nodes[0]['id'], selected_nodes[1]['id']

            if G.is_directed() and G.has_edge(u, v):
                return dash.no_update
            G.add_edge(u, v)
            if ponderado and edge_weight:
                G[u][v]['weight'] = edge_weight
            grafo_atualizado = True

    if trigger == 'add-weight-btn' and selected_edges and edge_weight:
        weight_value = edge_weight  # Obtenha o valor do peso a ser adicionado
        for edge_data in selected_edges:
            source = edge_data['source']
            target = edge_data['target']
            if G.has_edge(source, target):
                G[source][target]['weight'] = weight_value  # Adiciona o peso à aresta
                grafo_atualizado = True
    
    if trigger == 'remove-node-btn' and len(selected_nodes) >= 1:
        for node_data in selected_nodes:
            node_to_remove = node_data['id']
            if node_to_remove in G.nodes:
                G.remove_node(node_to_remove)
                grafo_atualizado = True

    if trigger == 'remove-edge-btn' and selected_edges:
        for edge_data in selected_edges:
            G.remove_edge(edge_data['source'], edge_data['target'])
        grafo_atualizado = True
    
    if trigger == 'bfs-btn' and bfs_clicks:
        if selected_nodes and selected_nodes[0]['id'] in G:
            bfs_result = list(nx.bfs_tree(G, selected_nodes[0]['id']))
            resultado_busca = f"BFS a partir de {selected_nodes[0]['id']}: {bfs_result}"
            grafo_atualizado = True
    
    elif trigger == 'dfs-btn' and dfs_clicks:
        if selected_nodes and selected_nodes[0]['id'] in G:
            dfs_result = list(nx.dfs_tree(G, selected_nodes[0]['id']))
            resultado_busca = f"DFS a partir de {selected_nodes[0]['id']}: {dfs_result}"
            grafo_atualizado = True
    
    if trigger == 'carregar-grafo':
        G.clear()
        carregar_grafo('grafo.txt')
    if trigger == 'salvar-grafo':
        salvar_grafo('grafo.txt')

    num_vertices = len(G.nodes())
    num_arestas = len(G.edges())

    if grafo_atualizado:
        elementos = gerar_elementos_cytoscape(G)
        info = f"Grafo {'ponderado' if ponderado else 'não ponderado'}, " \
               f"\nOrientado: {'sim' if G.is_directed() else 'não'}, " \
               f"\nQuantidade de Vértices: {num_vertices}, Vértices: {list(G.nodes)}" \
               f"\nQuantidade de Arestas: {num_arestas}, Arestas: {list(G.edges)}"
        if resultado_busca: 
            info += f"\n{resultado_busca}"
        return elementos, info, current_zoom, node_name_output

    return dash.no_update, dash.no_update, current_zoom, node_name_output

if __name__ == '__main__':
    app.run_server(debug=True)
