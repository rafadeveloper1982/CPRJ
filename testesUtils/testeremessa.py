import os
import codecs
from decimal import Decimal
from cnab240.bancos import santander, itau
from cnab240.tipos import Lote, Evento, Arquivo


itau_data = dict()
dict_arquivo = {
    'cedente_inscricao_tipo': 2,
    'cedente_inscricao_numero': 15594050000111,
    'cedente_agencia': 4459,
    'cedente_conta': 17600,
    'cedente_agencia_conta_dv': 6,
    'cedente_nome': "TRACY TECNOLOGIA LTDA ME",
    'arquivo_data_de_geracao': 27062012,
    'arquivo_hora_de_geracao': 112000,
    'arquivo_sequencia': 900002
}

dict_cobranca = {
    'cedente_agencia': 4459,
    'cedente_conta': 17600,
    'cedente_agencia_conta_dv': 6,
    'carteira_numero': 109,
    'nosso_numero': '99999999',
    'nosso_numero_dv': 9,
    'numero_documento': '9999999999',
    'vencimento_titulo': 30072012,
    'valor_titulo': Decimal('100.00'),
    'especie_titulo': 8,
    'aceite_titulo': 'A',
    'data_emissao_titulo': 27062012,
    'juros_mora_taxa_dia': Decimal('2.00'),
    'valor_abatimento': Decimal('0.00'),
    'identificacao_titulo': 'BOLETO DE TESTE',
    'codigo_protesto': 3,
    'prazo_protesto': 0,
    'codigo_baixa': 0,
    'prazo_baixa': 0,
    'sacado_inscricao_tipo': 1,
    'sacado_inscricao_numero': 83351622120,
    'sacado_nome': 'JESUS DO CEU',
    'sacado_endereco': 'RUA AVENIDA DO CEU, 666',
    'sacado_bairro': 'JD PARAISO',
    'sacado_cep': 60606,
    'sacado_cep_sufixo': 666,
    'sacado_cidade': 'PARAISO DE DEUS',
    'sacado_uf': 'SP',
}
'''
itau_data['arquivo'] = dict_arquivo
itau_data['cobranca'] = dict_cobranca
itau_data['header_arquivo'] = itau.registros.HeaderArquivo()
'''
evento = Evento(itau, 1)

# header_arquivo = itau.registros.HeaderArquivo(**dict_arquivo)
# print(header_arquivo)

# header_lote = Lote(itau, dict_cobranca)

arquivo = Arquivo(itau, **dict_arquivo)
arquivo.incluir_cobranca(dict_arquivo, **dict_cobranca)
arquivo.incluir_cobranca(dict_arquivo, **dict_cobranca)

print(arquivo)
