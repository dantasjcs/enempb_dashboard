import streamlit as st
import plotly.express as px
import pandas as pd
from streamlit_plotly_mapbox_events import plotly_mapbox_events
import numpy as np
import plotly.graph_objects as go


st.set_page_config(layout="wide", page_title='ENEM na Paraíba')
st.markdown("""
        <style> 
               .block-container {
                    padding-top: 1rem;
                    padding-bottom: 0rem;
                    padding-left: 5rem;
                    padding-right: 5rem;
                }
        </style>
        """, unsafe_allow_html=True)

# Lê dados dos .csv files
data = pd.read_csv('data.csv')
deltas = pd.read_csv('deltas.csv')

# Consegue o dado anual do enem com base na latitude do ponto clicado
def valor_anual(coluna, lat):
    valor = data[data['Latitude']==lat][coluna].iloc[0]
    return valor

# Plota os resultados do enem do ponto clicado
def plotar_stats(lat):
    container = []
    cod = data[data['Latitude']==lat]['COD INEP'].iloc[0]
    delta_escola = deltas[deltas['COD INEP']==int(cod)] 
    for i in data.columns[9:24]:
        valor = valor_anual(i, lat)
        container.append([i, valor])

   
    
    with coluna2:
        escola = data[data['COD INEP']==cod]['Escola'].iloc[0]
        st.subheader(escola)
        rows = [st.columns(5) for _ in range(3)]                     # Cria grid 
        cols = [column for row in rows for column in row]        
        for col, cat in zip(cols, container):
            if cat[0][-4:]=='2017':                                  # Não plotar métricas de 2017
                col.metric(label=cat[0], value=cat[1])
            else:
                d = f"delta_{cat[0]}"
                valor_delta = delta_escola[d].iloc[0]                     
                col.metric(label=cat[0], value=cat[1], delta=f'{valor_delta:.2f}%')           


# Plota estatísticas do estado e da escola em radar
def plotar_estado(inicio, fim, legenda=False):
    categories = data.columns[inicio:fim]
    notas_escola = list(data[data['COD INEP']==cod].iloc[0, inicio:fim])
    media_estado = data[data.columns[inicio:fim]].mean().astype(int)
    fig = go.Figure()           # Maneira de plotar um gráfico em cima do outro com Plotly

    fig.add_trace(go.Scatterpolar(
      r=notas_escola,
      theta=categories,
      fill='toself',
      name='Escola',  showlegend=legenda))
    
    fig.add_trace(go.Scatterpolar(
      r=media_estado,
      theta=categories,
      fill='toself', 
      name='Média do estado',  showlegend=legenda))
    
    fig.update_layout(
    polar=dict(
        radialaxis=dict(visible=True, range=[400, 600],  # Define o intervalo do eixo radial
            ),
        ),
    width=500,
    height=200,
    margin={"r": 100, "t": 35, "l": 80, "b": 20}, legend=dict(x=0.8,y=1))
    st.plotly_chart(fig)

# Gráfico de linhas das matriculas
def plotar_matriculas():
    st.subheader('Matrículas')
    matriculas = data[data['COD INEP']==cod].iloc[:, 3:7]
    matriculas = matriculas.transpose()
    matriculas = matriculas.rename({'mat_2017':'2017', 'mat_2018':'2018', 'mat_2019':'2019', 'mat_2020':'2020'})
    mat_bar = px.line(matriculas, markers=True)
    mat_bar.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0}, width=500, height=200, showlegend=False, xaxis=dict(title=None), yaxis=dict(title=None))
    st.plotly_chart(mat_bar)

# Boxplot das médias estudais
def plotar_box(inicio, fim):
    box_graf = px.box(data, x=data.columns[inicio: fim],  hover_name='Escola',  hover_data={'variable': False})
    box_graf.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0}, width=600, height=300,  xaxis=dict(title=None), yaxis=dict(title=None))
    st.plotly_chart(box_graf)


st.markdown("### Resultado do ENEM na Paraíba")
st.markdown("Clique em uma escola para saber mais sobre o seu desempenho entre 2017 e 2019.")
coluna1, coluna2, coluna3 = st.columns((1, 1.3, 1))


with coluna1:
    mapbox = px.scatter_mapbox(data, lat="Latitude", lon="Longitude", zoom=7, height=450, mapbox_style="carto-positron", hover_name='Escola', hover_data={'Latitude': False, 'Longitude': False})
    mapbox.update_layout(margin={"r": 0, "t": 40, "l": 0, "b": 0})
    plot_name_holder_clicked = st.empty()
    mapbox_events = plotly_mapbox_events(mapbox, click_event=True)
    

# Gatilho de clique
if len(mapbox_events[0])>0:
    lat = mapbox_events[0][0]['lat']
    cod = data[data['Latitude']==lat]['COD INEP'].iloc[0]
    plotar_stats(lat)
    with coluna1:
        plotar_matriculas()
    with coluna3:
        st.subheader('Notas da escola em relação a média da Paraíba')
        plotar_estado(9, 14, True)
        plotar_estado(14, 19, True)
        plotar_estado(19, 24, True)

    with coluna2:
        col2_1, col2_2 = st.columns(2)
    with col2_1:
        st.subheader('Médias estaduais')
    with col2_2:
        ano = st.radio('Ano:', ('2017', '2018', '2019', 'Tudo'), horizontal=True)
    if ano:
        if ano=='2017':
            data1, data2 = (9, 14)
        if ano=='2018':
            data1, data2 = (14, 19)
        if ano=='2019':
            data1, data2 = (19, 24)
        if ano=='Tudo':
            data1, data2 = (9, 24)
        with coluna2:
            plotar_box(data1, data2)
            