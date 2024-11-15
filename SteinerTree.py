import dash
import dash_cytoscape as cyto
from dash import html, dcc
import sys
import os
import networkx as nx
from dash.dependencies import Input, Output, State
import json

def agm_poda(grafo, terminais):
    mst = nx.minimum_spanning_tree(grafo)

    steiner_tree = mst.copy()
    
    for u, v in list(mst.edges()):
        if u not in terminais and v not in terminais:
            steiner_tree.remove_edge(u, v)

    return steiner_tree

def apresentar_resultados_agm(steiner_tree):
    if not steiner_tree or not steiner_tree.nodes():
        return "A árvore de Steiner não contém vértices."

    vertices = list(steiner_tree.nodes())
    arestas = list(steiner_tree.edges(data=True))
    custo_total = sum(data['weight'] for _, _, data in arestas)

    info_steiner = f"Vértices na Árvore de Steiner: {vertices}\n"
    info_steiner += "Arestas na Árvore de Steiner:\n"
    for u, v, data in arestas:
        info_steiner += f"({u} - {v}, Peso: {data['weight']})\n"
    info_steiner += f"Custo Total da Árvore de Steiner: {custo_total}\n"

    return info_steiner

def boruvka_steiner(G, terminals):

    steiner_tree = nx.Graph()
    componentes = {t: {t} for t in terminals}

    while len(componentes) > 1:
        arestas_menores = {}

        # Encontra a menor aresta pra cada vertice
        for componente in componentes.values():
            menor_aresta = None
            menor_peso = float('inf')

            # Verifica as arestas que conectam os vertices
            for u in componente:
                for u, v, dados in G.edges(u, data=True): 
                    if v not in componente and dados['weight'] < menor_peso:
                        menor_peso = dados['weight']
                        menor_aresta = (u, v, dados['weight'])

            if menor_aresta:
                arestas_menores[menor_aresta] = menor_peso

        # Une os vertices conectados pelas menores arestas
        for u, v, peso in arestas_menores.keys():
            steiner_tree.add_edge(u, v, weight=peso)

            componente_u = [c for c in componentes if u in componentes[c]][0]
            componente_v = [c for c in componentes if v in componentes[c]]

            # Verifica se v pertence a algum componente
            if componente_v:
                componente_v = componente_v[0]
            else:
                # Se v não pertence a nenhum componente, adiciona v ao componente de u
                componentes[componente_u].add(v)
                continue  # Continua para evitar unir o componente de v com o de u

            if componente_u != componente_v:
                # Unifica os dois componentes
                componentes[componente_u].update(componentes[componente_v])
                del componentes[componente_v]

    return steiner_tree

def apresentar_resultados_agm_boruvka(steiner_tree):
    if not steiner_tree or not steiner_tree.nodes():
        return "A árvore de Steiner não contém vértices."

    vertices = list(steiner_tree.nodes())
    arestas = list(steiner_tree.edges(data=True))
    custo_total = sum(data['weight'] for _, _, data in arestas)

    info_steiner_boruvka = f"Vértices na Árvore de Steiner: {vertices}\n"
    info_steiner_boruvka += "Arestas na Árvore de Steiner:\n"
    for u, v, data in arestas:
        info_steiner_boruvka += f"({u} - {v}, Peso: {data['weight']})\n"
    info_steiner_boruvka += f"Custo Total da Árvore de Steiner: {custo_total}\n"

    return info_steiner_boruvka

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

def salvar_grafo(arquivo):
    with open(arquivo, 'w') as f:
        for edge in G.edges():
            f.write(f"{edge[0]},{edge[1]}\n")
            

G = nx.DiGraph()
ponderado = False 

def gerar_elementos_cytoscape(grafo):
    elementos = []

    for node in grafo.nodes():
        elementos.append({
            'data': {'id': node, 'label': node}
        })

    for edge in grafo.edges(data=True):
        source, target, data = edge
        label = data.get('weight', '') if ponderado else ''  

        elementos.append({
            'data': {
                'source': str(source),
                'target': str(target),
                'label': str(label) if label else ''
            },
            'style': {
                'width': '2.8px',
                #'target-arrow-color': 'black',
                #'line-color': 'black',
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

button_style = {
    'backgroundColor': '#d5d8dc', 
    'color': 'black',             
    'border': '1px solid black',
    'padding': '5px 5px',       
    'textAlign': 'center',        
    'fontSize': '14px',           
    'margin': '5px',             
    'cursor': 'pointer',          
    'borderRadius': '5px',        
    'width': '95%',
    'cursor': 'pointer'
}

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
                            layout={'name': 'preset'},
                            zoom=0.8,
                            minZoom=0.5,
                            maxZoom=2.0,
                            boxSelectionEnabled=True,
                            userZoomingEnabled=True,
                            userPanningEnabled=True,
                            stylesheet = [
                                {'selector': 'node', 
                                'style': {
                                    'content': 'data(label)', 
                                    'text-valign': 'center', 
                                    'text-halign': 'center', 
                                    'background-color': '#d5d8dc', 
                                    'color': 'black',
                                    'borderWidth': 2,
                                    'borderColor': 'black',
                                    'textValign': 'center',
                                    'textAnchor': 'middle',
                                    'width': '60px',
                                    'height': '60px',}},
                                
                                {'selector': 'edge', 
                                'style': {
                                    'curve-style': 'bezier',
                                    'target-arrow-shape': 'triangle' if nx.is_directed(G) else 'none', 
                                    'line-color': 'black', 
                                    'target-arrow-color': 'black', 
                                    'label': 'data(label)',  # Isso agora reflete o peso das arestas se ponderado
                                    'color': 'black', 
                                    'text-background-color': '#ffffff', 
                                    'text-background-opacity': 0.5, 
                                    'text-background-shape': 'round-rectangle'}},

                                {'selector': 'node:selected',
                                'style': {
                                    'border-width': 2,
                                    'border-color': '#ff9147',
                                    'background-color': '#ffbd42'}},

                                {'selector': 'edge:selected',
                                'style': {
                                    'line-color': '#70e86c',
                                    'target-arrow-color': '#70e86c'}}
                            ],

                        ),
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
                                'zIndex': '1000'  
                            },
                        ),
                    ],
                    style={'width': '80%', 'height': '80vh', 'position': 'relative'}
                    ),
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
                                    html.Button("Adicionar Vértice", id='add-node-btn', n_clicks=0, style=button_style),
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
                                    html.Button("Remover Vértice", id='remove-node-btn', n_clicks=0, style=button_style),
                                ],
                                style={'marginBottom': '10px'}
                            ),
                            html.Div(
                                children=[
                                    html.Button("Adicionar Aresta", id='add-edge-btn', n_clicks=0, style=button_style),
                                    html.Button("Remover Aresta", id='remove-edge-btn', n_clicks=0, style=button_style),
                                ],
                                style={'marginBottom': '5px'}
                            ),
                            html.Div(
                                children=[
                                    html.Button("Adicionar Peso à Aresta", id='add-weight-btn', n_clicks=0, style=button_style),
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
                                style={'marginBottom': '5px'}
                            ),
                            html.Div(
                                style={'display': 'flex', 'justifyContent': 'space-around', 'marginBottom': '10px'},  # Alinha as duas colunas de botões
                                children=[
                                    html.Div(
                                        children=[
                                            html.Button("Executar BFS", id='bfs-btn', n_clicks=0, style=button_style),
                                            html.Button("Executar DFS", id='dfs-btn', n_clicks=0, style=button_style),
                                        ],
                                        style={'display': 'flex', 'flexDirection': 'column', 'marginRight': '10px'}  # Coloca BFS e DFS um embaixo do outro
                                    ),
                                    html.Div(
                                        children=[
                                            html.Button("Executar Boruvka", id='boruvka-btn', n_clicks=0, style=button_style),
                                            html.Button("Executar AGM", id='agm-btn', n_clicks=0, style=button_style),
                                        ],
                                        style={'display': 'flex', 'flexDirection': 'column',}  # Coloca Boruvka e AGM um embaixo do outro
                                    ),
                                ]
                            ),
                            html.Div(
                                children=[
                                    html.Button("Zoom In", id="zoom-in-btn", n_clicks=0, style=button_style),
                                    html.Button("Zoom Out", id="zoom-out-btn", n_clicks=0, style=button_style),
                                ],
                                style={'marginBottom': '5px'}
                            ),
                            html.Div(
                                children=[
                                    html.Button("Trocar Orientação", id='toggle-directed-btn', n_clicks=0, style=button_style),
                                    html.Button("Trocar Ponderação", id='toggle-weight-btn', n_clicks=0, style=button_style),
                                ],
                                style={'marginBottom': '5px'}
                            ),
                            html.Div(
                                children=[
                                    html.Button('Salvar Grafo', id='salvar-grafo', n_clicks=0, style=button_style),
                                    html.Button('Carregar Grafo', id='carregar-grafo', n_clicks=0, style=button_style),
                                ],
                                style={'marginBottom': '5px'}
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
        Input('boruvka-btn', 'n_clicks'),
        Input('agm-btn', 'n_clicks'),
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
        State('cytoscape', 'zoom'),
        State('cytoscape', 'elements')
    ]
)
def atualizar_grafo_e_buscas(

    add_node_clicks, add_edge_clicks, add_weight_clicks,
    remove_node_clicks, remove_edge_clicks,
    zoom_in_clicks, zoom_out_clicks,
    bfs_clicks, dfs_clicks,
    boruvka_clicks, agm_clicks,  # Botão de Steiner como argumento
    n_clicks_carregar_grafo, n_clicks_salvar_grafo,
    toggle_directed_clicks, toggle_weight_clicks,
    selected_nodes, selected_edges,  # Inputs adicionais
    node_name, edge_weight, current_zoom=None, elementos_atualizados=None  # States
):
    global G, ponderado

    node_name_output = dash.no_update

    trigger = dash.callback_context.triggered[0]['prop_id'].split('.')[0]
    grafo_atualizado = False
    resultado_busca = ""
    info_steiner = dash.no_update
    info_steiner_boruvka = dash.no_update

    if trigger == 'agm-btn':
        if selected_nodes:
            terminals = [node['id'] for node in selected_nodes]
            steiner_tree = agm_poda(G, terminals)
            info_steiner = apresentar_resultados_agm(steiner_tree)
            elementos = gerar_elementos_cytoscape(steiner_tree)
        else:
            info_steiner = "Selecione os nós terminais para calcular a árvore de Steiner."
        grafo_atualizado = True

    if trigger == 'boruvka-btn':
        if selected_nodes:
            terminals = [node['id'] for node in selected_nodes]

            # Chame a Heurística de Boruvka Modificada
            steiner_tree = boruvka_steiner(G, terminals)

            # Obtenha informações sobre a árvore de Steiner
            info_steiner_boruvka = apresentar_resultados_agm_boruvka(steiner_tree)

            # Para visualização (se necessário)
            elementos = gerar_elementos_cytoscape(steiner_tree)

        else:
            info_steiner_boruvka = "Selecione os nós terminais para calcular a árvore de Steiner."
        grafo_atualizado = True

        #return elementos, info_steiner, current_zoom, node_name_output

    if trigger == 'toggle-directed-btn':
        if G.is_directed():
            G_novo = nx.Graph()
            G_novo.add_nodes_from(G.nodes(data=True))
            for u, v, data in G.edges(data=True):
                G_novo.add_edge(u, v, weight=data.get('weight', 1))
            G = G_novo
        else:
            G_novo = nx.DiGraph()
            G_novo.add_nodes_from(G.nodes(data=True))
            for u, v, data in G.edges(data=True):
                G_novo.add_edge(u, v, weight=data.get('weight', 1))
            G = G_novo
        grafo_atualizado = True

    if trigger == 'toggle-weight-btn':
        ponderado = not ponderado
        for u, v, data in G.edges(data=True):
            if ponderado:
                if 'original_weight' in data:
                    data['weight'] = data['original_weight']
                elif 'weight' not in data:
                    data['weight'] = 1
            else:
                if 'weight' in data:
                    data['original_weight'] = data['weight']
                    del data['weight']
        grafo_atualizado = True

    if current_zoom is None:
        current_zoom = 1.0 

    if trigger == 'zoom-in-btn':
        current_zoom += 0.1
    elif trigger == 'zoom-out-btn':
        current_zoom -= 0.1
    
    if trigger == 'add-node-btn':
        if not node_name:
            node_name = f"{len(G.nodes) + 1}"

        if node_name not in G.nodes:
            G.add_node(node_name)
            grafo_atualizado = True
            node_name_output = ""

    if trigger == 'add-edge-btn':
        if selected_nodes and len(selected_nodes) > 1:
            for i in range(len(selected_nodes) - 1):
                u, v = selected_nodes[i]['id'], selected_nodes[i + 1]['id']
                if G.is_directed() and G.has_edge(u, v):
                    continue
                G.add_edge(u, v)
                if ponderado:
                    G[u][v]['weight'] = edge_weight if edge_weight else 1 
                grafo_atualizado = True

    if trigger == 'add-weight-btn' and selected_edges and edge_weight:
        weight_value = edge_weight 
        for edge_data in selected_edges:
            source = edge_data['source']
            target = edge_data['target']
            if G.has_edge(source, target):
                G[source][target]['weight'] = weight_value
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
               f"\nQuantidade de Vértices: {num_vertices},"\
               f"\nQuantidade de Arestas: {num_arestas}, "
        if resultado_busca: 
            info += f"\n{resultado_busca}"
        if trigger == 'agm-btn' and info_steiner is not dash.no_update:
            info += f"\n{info_steiner}"
        if trigger == 'boruvka-btn' and info_steiner_boruvka is not dash.no_update:
            info += f"\n{info_steiner_boruvka}"
        return elementos, info, current_zoom, node_name_output

    return dash.no_update, dash.no_update, current_zoom, node_name_output

if __name__ == '__main__':
    app.run_server(debug=True)
