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
os.chdir("c:/cprj/")

# List all files and directories in current directory
arquivos = fnmatch.filter(os.listdir('.'), '*.xlsx')

xl = pd.ExcelFile("titulos.xlsx")

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
    novoTitulo  = titulos(titulos=df1['Seminários'][x])
                                    

                                 
                                  
    novoTitulo.save()
    
print("registros processados: "+x)

    