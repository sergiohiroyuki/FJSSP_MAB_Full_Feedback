import streamlit as st
import mysql.connector
import json
import pandas as pd
import matplotlib.pyplot as plt
from pandas import Series
import plotly.express as px
import traceback


try:
    st.set_page_config(
        page_title = "Execuções anteriores",
        page_icon = "📓"
    )
    st.sidebar.success("Selecione uma pagina acima")

    #conecta com o banco
    conexao_bd = mysql.connector.connect(host="localhost", user="root", password="", database="mab")
    cursor = conexao_bd.cursor()

    #pega o nome do banco e coloca num select box
    st.header("SELECIONE UMA INSTANCIA ANTERIOR DO MAB :octopus:")
    
    cursor.execute('SELECT DISTINCT nome FROM mab.mab;')
    nomes = cursor.fetchall()
    nomes = [item[0] for item in nomes] 
    item_selecionado = st.selectbox('Selecione um item', nomes)

    if st.button("executar"):

        nome = item_selecionado

        #seleciona o numero de iterações 
        sql1 = "SELECT COUNT(r.iteracao) AS id_max  FROM mab.results r inner JOIN mab.mab m ON r.id_mab = m.id where m.nome = %s;"
        cursor.execute(sql1, (nome,))
        
        passa_iteracoes = cursor.fetchone()[0]
        st.write(passa_iteracoes)
        num_iteracoes = passa_iteracoes
        st.write("Foram feitas", num_iteracoes, "iterações")

        #seleciona o numero de braços
        sql2 = "SELECT COUNT(nome) FROM mab.mab WHERE nome = %s;"
        cursor.execute(sql2, (nome,))

        passa_bracos = cursor.fetchone()[0]
        num_bracos = passa_bracos
        st.write("Foram gerados", num_bracos, "braços")

        #seleciona o range das recompensas
        sql4 = "SELECT primeiro_braco, segundo_braco FROM mab.mab WHERE nome = %s;"
        cursor.execute(sql4,(nome,))
        passa_bracos = cursor.fetchall()

        recompensa_bracos = pd.DataFrame(passa_bracos, columns=["Valor minimo da recompensa", "Valor maximo da recompensa"])

        
        st.subheader("ALCANCE DAS RECOMPENSAS :game_die:")
        st.dataframe(recompensa_bracos.style.highlight_max(color='purple'))

        #seleciona a média e o total de jogadas
        sql3 = "SELECT media, total_jogadas FROM mab.mab WHERE nome = %s;"
        cursor.execute(sql3,(nome,))
        passa_media_total = cursor.fetchall()
    
        media_total = pd.DataFrame(passa_media_total, columns=["Média do braço", "Total de jogadas"])
        
        
        st.subheader("MÉDIA E TOTAL :chart_with_upwards_trend:")
        st.dataframe(media_total.style.highlight_max(color='purple'))

        #seleciona os resultados iteraçãos, recompensas e valor do resultados
        sql5 = "SELECT r.iteracao, r.indice_braco, r.valor_resultado FROM mab.results r INNER JOIN mab.mab m ON r.id_mab = m.id WHERE m.nome = %s;"
        cursor.execute(sql5, (nome,))
        passa_resultados = cursor.fetchall()

        def destacar_maximo(valor):
            estilo = 'background-color: purple' if valor == resultados['Valor do Resultado'].max() else ''
            return estilo

        resultados = pd.DataFrame(passa_resultados, columns=["Iteração", "Indice do braço", "Valor do Resultado"])
        
        st.subheader("RESULTADOS POR RODADA :moneybag:")
        st.dataframe(resultados.style.applymap(destacar_maximo))

        #grafico de linha
        resultados_grafico_linha = resultados.copy()
        fig = px.line(resultados_grafico_linha, x="Iteração", y="Valor do Resultado", color='Indice do braço', title="Braços Utilizados", markers=True)
        st.write(fig)

        #grafico de setores
        resultados_grafico_setores = resultados.copy()
        fig1 = px.pie(resultados_grafico_setores, values="Iteração", names='Indice do braço', title="Quantidade que Cada Braço foi Utilizado") 
        st.write(fig1)

    #fecha a conexao
    cursor.close()
    conexao_bd.close() 
except:
    traceback.print_exc()