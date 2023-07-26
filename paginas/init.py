import streamlit as st
import numpy as np
import random
import pandas as pd
import matplotlib.pyplot as plt
from pandas import Series
import plotly.express as px
import mysql.connector
import json
import traceback


class Bracos:
    def __init__(self, num_bracos, valor_max_recompensa):
        self.num_bracos = num_bracos
        self.valor_max_recompensa= valor_max_recompensa
        self.braco= []
        self.recompensas = []
        

    #cria os braços
    def cria_braco(self):
        for i in range(self.num_bracos):
            recompensa_braco = []
            recompensas_minima = random.uniform(0, self.valor_max_recompensa)
            recompensas_maxima = random.uniform(recompensas_minima, self.valor_max_recompensa)
            recompensa_braco.append(recompensas_minima)
            recompensa_braco.append(recompensas_maxima)
            self.recompensas.append(recompensa_braco)

        return self.recompensas

    #joga os braços
    def joga_bracos(self, indice_braco):
        braco_escolhido = indice_braco
        braco_jogado = 0
        braco_jogado = (random.uniform(self.recompensas[braco_escolhido][0],
                                            self.recompensas[braco_escolhido][1]))
        return braco_jogado
        
class MAB_Full_Feedback:
    def __init__(self, num_bracos, num_iteracoes, valor_max_recompensa, BracosObj):     
        self.num_iteracoes = num_iteracoes
        self.num_bracos = num_bracos
        self.valor_max_recompensa = valor_max_recompensa
        self.mab = BracosObj
        self.jogado = [[]for _ in range(self.num_bracos)]
        self.media_recompensa = []
        self.resultados = []

    #utiliza a classe braços para pegar as recompensas com o método joga braços
    def executar(self):
        indice_braco = random.randint(0, self.num_bracos -1)
        recompensa_de_cada_braco = []
        valor_resultado = self.mab.joga_bracos(indice_braco)
        
        for i in range(self.num_iteracoes):

            recompensa_de_cada_braco.clear()
            valor_resultado = self.mab.joga_bracos(indice_braco)
            self.jogado[indice_braco].append(valor_resultado)
 
            #resultados com iteração, braço puxado e resultado
            self.resultados.append((i+1, indice_braco, valor_resultado))

            #puxada falsa
            for puxada in range(self.num_bracos):
                recompensa_de_cada_braco.append(self.mab.joga_bracos(puxada))

            indice_braco = np.argmax(recompensa_de_cada_braco)
            
        
        return self.jogado, self.resultados
    
    #realiza a média e o total de vezes que foi jogado cada braço
    def media(self):
        self.media_recompensa 
        total = []
        divisor = 0
        for i in range(self.num_bracos):

            divisor =  len(self.jogado[i])
            soma = sum(self.jogado[i])
            if divisor == 0:
                self.media_recompensa.append((0, divisor))
                total.append(divisor)
            else:
                self.media_recompensa.append((soma / divisor, divisor))
                total.append(divisor)
     
                
        return self.media_recompensa, total

    


#Exibição
try:
    st.set_page_config(
        page_title = "Inicio",
        page_icon = "🏠"
    )
    st.sidebar.success("Selecione uma pagina acima")

    st.header("EXECUTE O MAB :octopus:")

    #pega parametros
    
    num_iteracoes = st.number_input('número de iterações', step=1, min_value =1,max_value=10000)
    num_bracos = st.number_input('número de braços', step=1, min_value =1, max_value=50)
    valor_max_recompensa = st.number_input('valor máximo da recompensa', step=1, min_value =1, max_value=100)

    #passa para as classes
    bracos = Bracos(num_bracos, valor_max_recompensa)
    mab = MAB_Full_Feedback(num_bracos, num_iteracoes, valor_max_recompensa, bracos)

    #executa e armazena os métodos em variaveis
    todos_bracos = bracos.cria_braco()
    executado, resultados= mab.executar()
    media, total_puxadas = mab.media()

    if st.button("executa MAB"):

        st.subheader("EXECUÇÃO APENAS PARA CURIOSIDADE")

        #cria os dataframes e graficos
        df = pd.DataFrame(
            todos_bracos,
            columns=(['recompensaº %d' % i for i in range(2)])
        )
        
        df_resultados = pd.DataFrame(
            resultados,
            columns=['Iteração', 'Índice do Braço', 'Valor do Resultado'],   
            )
        
        df_resultados_grafico_linha = df_resultados.copy()

        fig = px.line(df_resultados_grafico_linha, x="Iteração",
                    y="Valor do Resultado", color='Índice do Braço',
                        title="Braços Utilizados", markers=True)
        
        df_resultados_grafico_setores = df_resultados.copy()

        fig1 = px.pie(df_resultados_grafico_setores,
                    values="Iteração", names='Índice do Braço', title="Quantidade que Cada Braço foi Utilizado") 


        df_media = pd.DataFrame(
            media, 
            columns=['media', 'total']
        )
        
        #marca somente uma coluna
        def destacar_maximo(valor):
            estilo = 'background-color: purple' if valor == df_resultados['Valor do Resultado'].max() else ''
            return estilo

        #printa os resultados
        st.subheader("ALCANCE DAS RECOMPENSAS :game_die:")
        st.dataframe(df.style.highlight_max(color='purple'))

        st.subheader("RESULTADOS POR RODADA :moneybag:")
        st.dataframe(df_resultados.style.applymap(destacar_maximo))

        st.subheader("MÉDIA E TOTAL :chart_with_upwards_trend:")
        st.dataframe(df_media.style.highlight_max(color='purple'))  
        
        st.write(fig)
        st.write(fig1)

    #Banco de Dados
    #conecta com o banco
    conexao_bd = mysql.connector.connect(host="localhost", user="root", password="", database="mab")
    cursor = conexao_bd.cursor()

    nome = st.text_input('nome da execução')

    if st.button("adicionar ao banco"):

        st.subheader("EXECUÇÃO SALVA NO BANCO DE DADOS")

        #verifica se o nome não exeste no banco
        sql0 = "SELECT EXISTS (SELECT 1 FROM mab.mab WHERE nome = %s) AS contains_value;"
        cursor.execute(sql0, (nome,))
        result = cursor.fetchone()[0]
        st.write(result)

        if result == 0:

    
            for i in range(num_bracos):

                media1 = media[i][0]
                total_jogadas = media[i][1]
                primeiro_braco = todos_bracos[i][0]
                segundo_braco = todos_bracos[i][1]
                
                #insere a média nome total de jagadas e range dos braços
                sql1 = "INSERT INTO mab.mab(nome, media, total_jogadas, primeiro_braco, segundo_braco) VALUES (%s, %s, %s, %s, %s)"
                valores1 = (nome, media1, total_jogadas, primeiro_braco, segundo_braco)
                cursor.execute(sql1, valores1)
                conexao_bd.commit()

            # seleciona o id para ser passado como chave estrangeira
            sql2 = "SELECT id FROM mab.mab WHERE nome = %s"
            cursor.execute(sql2, (nome,))
            id_mab_passando = cursor.fetchone()[0]
             
            
            resultados_primeira_consulta = cursor.fetchall()

            for h in range(num_iteracoes):
                

                id_mab = int(id_mab_passando)
                iteracao = int(resultados[h][0])
                indice_braco = int(resultados[h][1])
                valor_resultado = (resultados[h][2])
                
                # insere a iteração o indice do braço e o valor dos resultados
                sql3 = "INSERT INTO mab.results(id_mab, iteracao, indice_braco, valor_resultado) VALUES (%s, %s, %s, %s)"

                valores3 = (id_mab, iteracao, indice_braco, valor_resultado)
                
                cursor.execute(sql3, valores3)

                conexao_bd.commit()
                resultados_primeira_consulta = cursor.fetchall()
            
                #cria os dataframes e graficos
            df = pd.DataFrame(
                todos_bracos,
                columns=(['recompensaº %d' % i for i in range(2)])
            )
            
            df_resultados = pd.DataFrame(
                resultados,
                columns=['Iteração', 'Índice do Braço', 'Valor do Resultado'],   
                )
            
            df_resultados_grafico_linha = df_resultados.copy()

            fig = px.line(df_resultados_grafico_linha, x="Iteração",
                        y="Valor do Resultado", color='Índice do Braço',
                            title="Braços Utilizados", markers=True)
            
            df_resultados_grafico_setores = df_resultados.copy()

            fig1 = px.pie(df_resultados_grafico_setores,
                        values="Iteração", names='Índice do Braço', title="Quantidade que Cada Braço foi Utilizado") 


            df_media = pd.DataFrame(
                media, 
                columns=['media', 'total']
            )
            
            #marca somente uma coluna
            def destacar_maximo(valor):
                estilo = 'background-color: purple' if valor == df_resultados['Valor do Resultado'].max() else ''
                return estilo

            #printa os resultados
            st.subheader("ALCANCE DAS RECOMPENSAS :game_die:")
            st.dataframe(df.style.highlight_max(color='purple'))

            st.subheader("RESULTADOS POR RODADA :moneybag:")
            st.dataframe(df_resultados.style.applymap(destacar_maximo))

            st.subheader("MÉDIA E TOTAL :chart_with_upwards_trend:")
            st.dataframe(df_media.style.highlight_max(color='purple'))  
            
            st.write(fig)
            st.write(fig1)
            #fecha a conexão
            cursor.close()
            conexao_bd.close()  
except:
    traceback.print_exc()