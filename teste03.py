import dash
from dash import dcc, html, Input, Output, State
import dash_cytoscape as cyto
import networkx as nx
from graph_manager import *

# Inicialização do app
app = dash.Dash(__name__)

# Criação do layout
app.layout = html.Div([
    html.H1("Gerenciador de Grafos"),
    
    # Input para adicionar um nó
    html.Div([
        dcc.Input(id='node-name', type='text', placeholder='Nome do nó'),
        html.Button('Adicionar Nó', id='add-node-btn', n_clicks=0)
    ]),
    
    # Input para adicionar uma aresta
    html.Div([
        dcc.Input(id='source-node', type='text', placeholder='Nó de origem'),
        dcc.Input(id='target-node', type='text', placeholder='Nó de destino'),
        dcc.Input(id='edge-weight', type='number', placeholder='Peso', min=1),
        html.Button('Adicionar Aresta', id='add-edge-btn', n_clicks=0)
    ]),
    
    # Botões para remover nós e arestas
    html.Div([
        dcc.Input(id='remove-node-name', type='text', placeholder='Nome do nó para remover'),
        html.Button('Remover Nó', id='remove-node-btn', n_clicks=0),
        dcc.Input(id='source-remove', type='text', placeholder='Nó de origem para remover aresta'),
        dcc.Input(id='target-remove', type='text', placeholder='Nó de destino para remover aresta'),
        html.Button('Remover Aresta', id='remove-edge-btn', n_clicks=0)
    ]),
    
    # Botões para carregar e salvar grafo
    html.Div([
        html.Button('Salvar Grafo', id='save-graph-btn', n_clicks=0),
        html.Button('Carregar Grafo', id='load-graph-btn', n_clicks=0)
    ]),
    
    # Container do grafo
    cyto.Cytoscape(
        id='cytoscape',
        layout={'name': 'cose'},
        style={'width': '100%', 'height': '500px'},
        elements=[],
    ),
    
    # Container das informações do grafo
    html.Div(id='info-grafo', style={'width': '100%', 'padding': '20px'})
])

# Callbacks para interagir com a interface
@app.callback(
    Output('cytoscape', 'elements'),
    Input('add-node-btn', 'n_clicks'),
    Input('add-edge-btn', 'n_clicks'),
    Input('remove-node-btn', 'n_clicks'),
    Input('remove-edge-btn', 'n_clicks'),
    Input('load-graph-btn', 'n_clicks'),
    Input('save-graph-btn', 'n_clicks'),
    State('node-name', 'value'),
    State('source-node', 'value'),
    State('target-node', 'value'),
    State('edge-weight', 'value'),
    State('remove-node-name', 'value'),
    State('source-remove', 'value'),
    State('target-remove', 'value'),
    State('cytoscape', 'elements')
)
def manage_graph(add_node_clicks, add_edge_clicks, remove_node_clicks, remove_edge_clicks, load_clicks, save_clicks,
                 node_name, source_node, target_node, edge_weight, remove_node_name, source_remove, target_remove, elements):
    
    # Criar um grafo vazio ao iniciar
    if not elements:
        G = create_graph(directed=False)  # Criar grafo não direcionado por padrão
    else:
        G = reconstruct_graph_from_elements(elements, directed=False)  # Recriar grafo a partir dos elementos

    # Adicionar nó
    if add_node_clicks > 0 and node_name:
        G = add_node(G, node_name)
    
    # Adicionar aresta
    if add_edge_clicks > 0 and source_node and target_node:
        weight = edge_weight if edge_weight else 1.0  # Usar 1.0 como peso padrão
        G = add_edge(G, source_node, target_node, weight)

    # Remover nó
    if remove_node_clicks > 0 and remove_node_name:
        G = remove_node(G, remove_node_name)

    # Remover aresta
    if remove_edge_clicks > 0 and source_remove and target_remove:
        G = remove_edge(G, source_remove, target_remove)

    # Salvar grafo
    if save_clicks > 0:
        save_graph_to_csv(G)

    # Carregar grafo
    if load_clicks > 0:
        G = load_graph_from_csv()

    # Atualizar elementos
    elements = networkx_to_cytoscape(G)

    # Exibir informações do grafo
    info = f"Grafo: {len(G.nodes)} nós, {len(G.edges)} arestas"
    
    return elements, info

# Callback para exibir informações do grafo
@app.callback(
    Output('info-grafo', 'children'),
    Input('cytoscape', 'elements')
)
def display_graph_info(elements):
    if elements:
        G = reconstruct_graph_from_elements(elements)
        info = f"Grafo: {len(G.nodes)} nós, {len(G.edges)} arestas"
        return info
    return "Grafo vazio."

if __name__ == '__main__':
    app.run_server(debug=True)
