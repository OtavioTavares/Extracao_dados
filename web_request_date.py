from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from datetime import datetime
import os
import time
import pandas as pd
import datetime
import xlrd
import os
import requests
from bs4 import BeautifulSoup


lista_subdataframes = []


class WebScraping:
    
    def __init__(self):
        localdir = os.path.dirname(os.path.realpath(__file__))
        chromeOptions = webdriver.ChromeOptions()
        chromeOptions.add_argument('lang=pt-br')
        #chromeOptions.add_argument('--headless')
        exe_path = os.path.join(localdir, 'chromedriver.exe')
        self.driver = webdriver.Chrome(executable_path=exe_path, options=chromeOptions)
        self.driver.get('https://www.in.gov.br/leiturajornal')
        time.sleep(5)
                                  
    def localizar_arquivos(self):
        #Selecionando a pesquisa avancada
        pesquisa_avancada = self.driver.find_element_by_xpath("//*[@id='toggle-search-advanced']")
        pesquisa_avancada.click()
        print("Entrando no site...")
        time.sleep(3)

        #Selecionando o filtro buscar exato 
        busca_exata = self.driver.find_element_by_xpath("//*[@id='tipo-pesquisa-1']")
        busca_exata.click()
        
        #Localizando o campo para escrever
        campo_texto = self.driver.find_element_by_xpath("//*[@id='search-bar']")
        time.sleep(3)
        campo_texto.click()
        print("Realizando a pesquisa...")
     
        
        #Escrevendo o texto
        campo_texto.send_keys(mensagem)

        #Campo personalizado
        selecionar_data = self.driver.find_element_by_xpath("//*[@id='personalizado']")
        time.sleep(3)
        selecionar_data.click()


        #Data inicio
        data_inicio = self.driver.find_element_by_xpath("//*[@id='data-inicio']")
        data_inicio.click()
        time.sleep(2)
        data_inicio.send_keys(Keys.BACKSPACE+Keys.BACKSPACE+Keys.BACKSPACE+Keys.BACKSPACE+Keys.BACKSPACE+Keys.DELETE+Keys.DELETE+Keys.DELETE+Keys.DELETE+Keys.DELETE+Keys.BACKSPACE+Keys.DELETE+Keys.BACKSPACE)
        time.sleep(2)
        data_inicio.send_keys(inicio)
        data_inicio.send_keys(Keys.ENTER)

        
        #Data final
        data_final = self.driver.find_element_by_xpath("//*[@id='data-fim']")
        data_final.click()
        time.sleep(2)
        data_final.send_keys(Keys.BACKSPACE+Keys.BACKSPACE+Keys.BACKSPACE+Keys.BACKSPACE+Keys.BACKSPACE+Keys.DELETE+Keys.DELETE+Keys.DELETE+Keys.DELETE+Keys.DELETE+Keys.BACKSPACE+Keys.DELETE+Keys.BACKSPACE)
        data_final.send_keys(final)
        data_final.send_keys(Keys.ENTER)

        #Enviando o texto
        botao_enviar = self.driver.find_element_by_xpath("//*[@id='search-advanced']/div[2]/div[1]/button")
        botao_enviar.click()
        time.sleep(3)
        

    def selecionar_arquivos(self):

        #Definindo o URL após realizar a busca
        global url_busca
        url_busca = self.driver.current_url

       
        #Buscando cada resolucao
        post = self.driver.find_elements_by_class_name('title-marker')

        x = 0
        while x < len(post):
            post = self.driver.find_elements_by_class_name('title-marker')


            #Apresentando a resolucao que esta senso executada
            data = str(post[x].text)
            data = data.split(" ")
            data_upper =[]
            for dado in data:
                data_upper.append(dado.upper())
                    
            print(data_upper)
            post[x].click()

            #Extração da pagina utilizando REQUEST 
            texto_pagina = []
            url = self.driver.current_url
            page = requests.get(url)

            #Realizando o tratamento com BS4
            soup = BeautifulSoup(page.text,'html.parser')

            #Definindo o nome da resolucao
            resolucao = soup.find_all('p', class_='identifica')
            resolucao = str(resolucao).split('<p class="identifica">')
            resolucao = resolucao[1].split("</p>]")
            resolucao = resolucao[0]

            #Listando todos os dados do site
            dados = soup.find_all('p', class_='dou-paragraph')
            dados = str(dados).split('<p class="dou-paragraph">')
            dados = str(dados).split('</p>')
                    
            contador = 0
            inicio = time.time()

            #Realizando o tratamento dos dados de cada parágrafo
            while contador < len(dados) - 1:
                try:
                    ajuste_dados = str(dados[contador]).split("', '")
                    texto_pagina.append(ajuste_dados[1])
                    contador += 1
                except:
                    ajuste_dados = str(dados[contador]).split(', "')
                    texto_pagina.append(ajuste_dados[1])
                    contador += 1

                           
            fim = time.time()
            print("Tempo de extração: " + str(round(fim-inicio,3)) + " s")


            # Esse bloco é responsável para dividir as empresas
            bloco_geral = str(texto_pagina).split("_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _")
            print("Empresas na página: ",len(bloco_geral))


            #Para cada empresa é realizado uma organização para criar um sub dataset
            for sub_bloco in bloco_geral:
                frases = sub_bloco.split("', '")
                num = 0

                #Cada vez que o "NOME DO PRODUTO" era encontrado, um novo registro para a mesma empresa era criado
                for frase in frases:
                    if 'NOME DO PRODUTO' in frase:
                        num += 1
                        
                #Lista responsavel para adicionar os registros no dataframe
                lista_empresa = [None,None,None,None,None,None,None,None,None,None,None,None,None,None]

                #O primeiro item se mantem com o nome da resolucao da pagina
                lista_empresa[0] = resolucao


                #É inserido o nome da empresa e da autorização para cada registro
                for frase in frases:
                    if 'NOME DA EMPRESA' in frase:
                        nome_empresa = frase.split(":")[1]
                        lista_empresa[1] = nome_empresa
                    if 'AUTORIZAÇÃO' in frase:
                        autorizacao = frase.split(":")[1]
                        lista_empresa[2] = autorizacao


                #Neste pedaço de código vamos adicionando as outras informações que o cliente deseja na planilha
                adicional = 0
                while adicional < num:
                    indice = 0
                    while indice < len(frases):
                        frase = frases[indice]
                        if (('NOME DO PRODUTO E MARCA' in frase) and (lista_empresa[3] == None)):
                            marca = frase.split(":")[1]
                            lista_empresa[3] = marca
                            del frases[indice]
                            if indice > 0:
                                indice = indice - 1
                            else:
                                indice = indice
                        if (('NUMERO DE PROCESSO' in frase)and (lista_empresa[4] == None)):
                            processo = frase.split(":")[1]
                            lista_empresa[4] = processo
                            del frases[indice]
                            if indice > 0:
                                indice = indice - 1
                            else:
                                indice = indice
                        if (('NUMERO DE REGISTRO' in frase)and (lista_empresa[5] == None)):
                            registro = frase.split(":")[1]
                            lista_empresa[5] = registro
                            del frases[indice]
                            if indice > 0:
                                indice = indice - 1
                            else:
                                indice = indice
                        if (('VENDA E EMPREGO' in frase)and (lista_empresa[6] == None)):
                            venda_emprego = frase.split(":")[1]
                            lista_empresa[6] = venda_emprego
                            del frases[indice]
                            if indice > 0:
                                indice = indice - 1
                            else:
                                indice = indice
                        if (('VENCIMENTO' in frase)and (lista_empresa[7] == None)):
                            vencimento = frase.split(":")[1]
                            lista_empresa[7] = vencimento
                            del frases[indice]
                            if indice > 0:
                                indice = indice - 1
                            else:
                                indice = indice
                        if (('APRESENTAÇÃO' in frase)and (lista_empresa[8] == None)):
                            apresentacao = frase.split(":")[1]
                            lista_empresa[8] = apresentacao
                            del frases[indice]
                            if indice > 0:
                                indice = indice - 1
                            else:
                                indice = indice
                        if (('VALIDADE DO PRODUTO' in frase)and (lista_empresa[9] == None)):
                            validade = frase.split(":")[1]
                            lista_empresa[9] = validade
                            del frases[indice]
                            if indice > 0:
                                indice = indice - 1
                            else:
                                indice = indice
                        if (('CATEGORIA' in frase)and (lista_empresa[10] == None)):
                            categoria = frase.split(":")[1]
                            lista_empresa[10] = categoria
                            del frases[indice]
                            if indice > 0:
                                indice = indice - 1
                            else:
                                indice = indice
                        if (('ASSUNTO DA PETIÇÃO' in frase) and (lista_empresa[11] == None)):
                            assunto_peticao = frase.split(":")[1]
                            lista_empresa[11] = assunto_peticao
                            del frases[indice]
                            if indice > 0:
                                indice = indice - 1
                            else:
                                indice = indice
                        if (('EXPEDIENTE DA PETIÇÃO' in frase)and (lista_empresa[12] == None)):
                            expediente_peticao = frase.split(":")[1]
                            lista_empresa[12] = expediente_peticao
                            del frases[indice]
                            if indice > 0:
                                indice = indice - 1
                            else:
                                indice = indice
                        if (('VERSÃO' in frase)and (lista_empresa[13] == None)):
                            versao = frase.split(":")[1]
                            lista_empresa[13] = versao
                            del frases[indice]
                            if indice > 0:
                                indice = indice - 1
                            else:
                                indice = indice
                        indice += 1

                    adicional += 1

                    # Neste momento é criado um dataframe para cada resolução
                    
                    dados = {"RESOLUCAO":lista_empresa[0],"EMPRESA":lista_empresa[1],"AUTORIZACAO":lista_empresa[2],
                                                              "MARCA":lista_empresa[3],"PROCESSO":lista_empresa[4],"REGISTRO":lista_empresa[5],
                                                               "VENDA E EMPREGO":lista_empresa[6],"VENCIMENTO":lista_empresa[7],
                                                              "APRESENTACAO":lista_empresa[8],"VALIDADE PRODUTO":lista_empresa[9],
                                                               "CATEGORIA":lista_empresa[10],"ASSUNTO PETICAO":lista_empresa[11],
                                                              "EXPEDIENTE E PETICAO":lista_empresa[12],"VERSAO":lista_empresa[13]}
                    
                    df = pd.DataFrame.from_dict(dados,orient="index").reset_index()
                    df_T = df.transpose()
                    global colunas
                    colunas = ["RESOLUCAO","EMPRESA","AUTORIZACAO","MARCA","PROCESSO","REGISTRO",
                                                               "VENDA E EMPREGO","VENCIMENTO","APRESENTACAO","VALIDADE PRODUTO",
                                                               "CATEGORIA","ASSUNTO PETICAO","EXPEDIENTE E PETICAO","VERSAO"]
                    df_T.columns = colunas
                    df_T.reset_index(drop=True,inplace=True)
                    df_T = df_T.drop(0)

                    #Neste momento o dataframe de cada empresa é adicionado em uma lista master
                    lista_subdataframes.append(df_T)
                    lista_empresa = [resolucao,nome_empresa,autorizacao,None,None,None,None,None,None,None,None,None,None,None]

            print("Trocando de pagina...")
            self.driver.get(url_busca)
            time.sleep(5)

            x += 1
                

inicio = '04/11/2020'
final = '04/01/2021'
mensagem = "deferir os registros e as petições dos produtos saneantes"


bot = WebScraping()
bot.localizar_arquivos()
bot.selecionar_arquivos()

while True:
    try:
        #Tenta clicar no botao da próxima página e repete o processo de criar novos sub dataframes
        next_page = bot.driver.find_element_by_xpath("/html/body/div[1]/div[2]/main/div[2]/div/section/div/div/div/div/div[1]/section/div/div[2]/div/div[3]/ul/li[4]/button")
        next_page.click()
        time.sleep(5)
        bot.selecionar_arquivos()

    except:
        print("Extração concluida")
        #É criado o último dataframe master, que utiliza todos os sub dataframes
        df_grupo = pd.concat(lista_subdataframes, axis=0)
        df_grupo.columns = colunas
        df_grupo.reset_index(drop=True, inplace=True)

        #Salva o arquivo em CSV
        df_grupo.to_csv('Webscraping.csv')

        #Salva o arquivo em XLSX
        excel = pd.ExcelWriter("Webscraping.xlsx", mode ="w", engine="xlsxwriter")
        df_grupo.to_excel(excel, sheet_name="Extraido Web")
        excel.save()
        
        break
