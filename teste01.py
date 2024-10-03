import dash
import dash_cytoscape as cyto
from dash import html
import networkx as nx
from dash.dependencies import Input, Output, State
import dash_core_components as dcc

def gerar_elementos_cytoscape(grafo):
    elementos = []
    
    # Adicionar nós
    for node in grafo.nodes():
        elementos.append({
            'data': {'id': node, 'label': node},
            'style': {
                'backgroundColor': 'lightpink',
                'borderWidth': 0,
                'borderColor': 'blue',
                'color': 'plum',
                'textValign': 'center',
                'textAnchor': 'middle'
            }
        })
    
    # Adicionar arestas
    for edge in grafo.edges():
        elementos.append({
            'data': {'source': edge[0], 'target': edge[1]},
            'style': {
                'lineColor': 'gray',
                'width': 2,
                'targetArrow': 'triangle',
                'sourceArrow': 'circle'
            }
        })
    
    return elementos


#def gerar_elementos_cytoscape(grafo):
#    elementos = []
#    for node in grafo.nodes():
#        elementos.append({'data': {'id': node, 'label': node}})
#    for edge in grafo.edges():
#        elementos.append({'data': {'source': edge[0], 'target': edge[1]}})
#    return elementos

# Inicializando o grafo
G = nx.Graph()
G.add_edges_from([('A', 'B'), ('B', 'C'), ('C', 'D')])

# Inicializando a aplicação Dash
app = dash.Dash(__name__)

# Layout da página
app.layout = html.Div([
    html.H1("Visualização de Grafos"),
    cyto.Cytoscape(
        id='cytoscape',
        elements=gerar_elementos_cytoscape(G),
        style={'width': '100%', 'height': '400px'},
        layout={'name': 'circle'},
        zoom=2.0,
    ),
    
    html.Div(id='info-grafo'),
    
    # Inputs para adicionar e remover vértices e arestas
    html.Div([
        html.Button("Adicionar Vértice", id='add-node-btn', n_clicks=0),
        dcc.Input(id='node-name', type='text', placeholder='Nome do Vértice'),
        
        html.Button("Adicionar Aresta", id='add-edge-btn', n_clicks=0),
        dcc.Input(id='source-node', type='text', placeholder='Vértice de Origem'),
        dcc.Input(id='target-node', type='text', placeholder='Vértice de Destino'),

        html.Button("Remover Vértice", id='remove-node-btn', n_clicks=0),
        dcc.Input(id='remove-node-name', type='text', placeholder='Nome do Vértice para Remover'),

        html.Button("Remover Aresta", id='remove-edge-btn', n_clicks=0),
        dcc.Input(id='source-remove', type='text', placeholder='Vértice de Origem'),
        dcc.Input(id='target-remove', type='text', placeholder='Vértice de Destino'),

        html.Button("Tornar Orientado", id='toggle-directed-btn', n_clicks=0),
        html.Button("Adicionar Peso", id='toggle-weighted-btn', n_clicks=0),
    ])
])

@app.callback(
    Output('cytoscape', 'elements'),
    Output('info-grafo', 'children'),
    Input('add-node-btn', 'n_clicks'),
    Input('add-edge-btn', 'n_clicks'),
    Input('remove-node-btn', 'n_clicks'),
    Input('remove-edge-btn', 'n_clicks'),
    Input('toggle-directed-btn', 'n_clicks'),
    Input('toggle-weighted-btn', 'n_clicks'),
    State('node-name', 'value'),
    State('source-node', 'value'),
    State('target-node', 'value'),
    State('remove-node-name', 'value'),
    State('source-remove', 'value'),
    State('target-remove', 'value'),
)
def atualizar_grafo(
    add_node_clicks, add_edge_clicks, remove_node_clicks, remove_edge_clicks,
    toggle_directed_clicks, toggle_weighted_clicks,
    node_name, source_node, target_node, remove_node_name, source_remove, target_remove
):
    global G
    
    ctx = dash.callback_context
    if not ctx.triggered:
        raise dash.exceptions.PreventUpdate

    trigger = ctx.triggered[0]['prop_id'].split('.')[0]

    if trigger == 'add-node-btn' and node_name:
        G.add_node(node_name)
    
    elif trigger == 'add-edge-btn' and source_node and target_node:
        G.add_edge(source_node, target_node)

    elif trigger == 'remove-node-btn' and remove_node_name in G.nodes():
        G.remove_node(remove_node_name)

    elif trigger == 'remove-edge-btn' and G.has_edge(source_remove, target_remove):
        G.remove_edge(source_remove, target_remove)

    elif trigger == 'toggle-directed-btn':
        G = G.to_directed() if not G.is_directed() else G.to_undirected()

    elif trigger == 'toggle-weighted-btn':
        for edge in G.edges():
            G[edge[0]][edge[1]]['weight'] = 1

    elements = gerar_elementos_cytoscape(G)
    num_vertices = len(G.nodes())
    num_arestas = len(G.edges())
    orientado = "Sim" if G.is_directed() else "Não"
    ponderado = "Sim" if any('weight' in e for e in G.edges(data=True)) else "Não"
    
    info_text = f"Número de Vértices: {num_vertices}, Número de Arestas: {num_arestas}, Orientado: {orientado}, Ponderado: {ponderado}"
    
    return elements, info_text

# Iniciar o servidor
if __name__ == '__main__':
    app.run_server(debug=True)
