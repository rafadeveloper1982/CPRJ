# coding:utf-8

from django.contrib.contenttypes.models import ContentType

from associados.models import Associado,Categoria

import datetime

import sys

#Ler planilha
import pandas as pd
import xlrd
import os, fnmatch


print("carregando ....")
cwd = os.getcwd()
os.chdir("/home/rafael/cprj/")

# List all files and directories in current directory
arquivos = fnmatch.filter(os.listdir('.'), '*.xlsx')

xl = pd.ExcelFile("associados_associado.xlsx")

# Load a sheet into a DataFrame by name: df1
df1 = xl.parse(xl.sheet_names[0])

total = len(df1['nome'])  # total de registros


contador = 0  # contador

categoria=Categoria.objects.get(id=3)
for x in range(0,total):
    try:
      data=df1['data de nascimento'][x].split("/")
      sdata=datetime.date(int(data[2]),int(data[1]),int(data[0]))   
    except:
    	sdata=None
    contador = contador + 1
    novoAssociado  = Associado(referencia=int(df1['referencia'][x]),
                                nome=df1['nome'][x],
                                endereco = df1['endereco1'][x],
                                bairro=df1['bairro1'][x],
                                cep = df1['cep1'][x],
                                cidade=df1['cidade1'][x],
                                estado=df1['uf1'][x],
                                pais=df1['pais1'][x],
                                telefone=df1['tel1'][x],
                                celular=df1['celular1'][x],
                                celular2=df1['celular2'][x],
                                endereco_residencial=df1['endereco2'][x],
                                bairro_residencial=df1['bairro2'][x],
                                cep_residencial=df1['cep2'][x],
                                cidade_residencial=df1['cidade2'][x],
                                estado_residencial=df1['uf2'][x],
                                pais_residencial=df1['pais2'][x],
                                telefone_residencial=df1['tel2'][x],
                                email=df1['e-mail'][x],
                                data_de_nascimento=sdata,
                                cpf=df1['cpf'][x],
                                #ano_de_formacao= None if df1['data'][x]=='' else df1['data'][x],
                                historico=df1['historico'][x],
                                ativo=df1['ativo'][x],
                                categoria=categoria)
                                    

                                 
                                  
    novoAssociado.save()
    
print("registros processados: "+x)

    