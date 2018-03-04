# -*- coding: utf-8 -*-
from django.db import models


class Banco(models.Model):
    codigo_banco = models.CharField(u'Código do Banco', max_length=3)
    nome_banco = models.CharField(u'Nome do Banco', max_length=50)

    def __str__(self):
        return '%s - %s' % (self.codigo_banco, self.nome_banco)


CODICO_BAIXA_CHOICES = (
    (1, 'BAIXAR / DEVOLVER'),
    (2, 'NAO BAIXAR / NAO DEVOLVER'),
    (3, 'UTILIZAR PERFIL BENEFICIÁRIO')
)

CODIGO_JUROS = (
    (1, 'Valor por dia'),
    (2, 'Taxa Mensal'),
    (3, 'Isento')
)

CODIGO_MULTA = (
    (1, 'Valor fixo'),
    (2, 'Percentual')
)


class Conta(models.Model):
    banco = models.ForeignKey(Banco, null=True, blank=False, on_delete=models.CASCADE)
    carteira = models.CharField(max_length=5)
    carteira_remessa = models.CharField(max_length=5, null=True, blank=False)
    aceite = models.CharField(max_length=1, default='N')
    numero_documento = models.IntegerField(u'Ultimo Número do Documento')

    # Informações do Cedente
    codigo_transmissao = models.CharField(u'Código de Transmissão', max_length=15, null=True, blank=False)
    agencia_cedente = models.CharField(u'Agência Cedente', max_length=4)
    digito_agencia_cedente = models.CharField(u'Dígito da Agência do Cedente', max_length=1, null=True, blank=False)
    conta_cedente = models.CharField('Conta Cedente', max_length=9)
    digito_conta_cedente = models.CharField(u'Dígito da Conta do Cedente', max_length=1, null=True, blank=False)
    conta_cobranca = models.CharField('Conta Cobrança', max_length=9, null=True, blank=False)
    digito_conta_cobranca = models.CharField(u'Dígito da Conta de Cobrança', max_length=1, null=True, blank=False)
    cedente = models.CharField(u'Nome do Cedente', max_length=255)
    cedente_documento = models.CharField(u'Documento do Cedente', max_length=50)
    cedente_cidade = models.CharField(u'Cidade do Cedente', max_length=255)
    cedente_uf = models.CharField(u'Estado do Cedente', max_length=2)
    cedente_endereco = models.CharField(u'Endereço do Cedente',  max_length=255)
    cedente_bairro = models.CharField(u'Bairro do Cedente', max_length=255)
    cedente_cep = models.CharField(u'CEP do Cedente', max_length=9)
    cedente_seguencia_arquivo = models.IntegerField(u'Sequencia Arquivo', null=True, blank=False)

    # Informações Opcionais
    codigo_baixa = models.IntegerField(u'Código para Baixa/Devolução',  null=True, blank=True,  choices=CODICO_BAIXA_CHOICES, default=1)
    prazo_baixa = models.IntegerField(u'Prazo para Baixa/Devolução',  null=True, blank=True)
    especie_documento = models.IntegerField(u'Espécie do Documento',  blank=True)
    especie = models.CharField(u'Espécie', max_length=2, default="R$")
    moeda = models.CharField(max_length=2, default='9')
    local_pagamento = models.CharField(u'Local de Pagamento', max_length=255, default=u'Pagável em qualquer banco até o vencimento')
    codigo_juros = models.IntegerField(u'Código da multa', choices=CODIGO_JUROS, default=1)
    juros_mora_taxa = models.DecimalField(max_digits=8, decimal_places=2, default=0.2)

    codigo_multa = models.IntegerField(u'Código da multa', choices=CODIGO_MULTA, default=2)
    multa = models.DecimalField(u'Valor/Percentual a ser concedido', max_digits=8, decimal_places=2, default=2.00)
    instrucoes = models.TextField(u'Instruções',
                                  default=u"1 - Não receber após 30 dias. \n" +
                                  "2 - Multa de 2% após o vencimento. \n" +
                                  "3 - Taxa diária de permanência de {}.")


class Boleto(models.Model):
    # Informações Gerais
    codigo_banco = models.CharField(u'Código do Banco', max_length=3)
    carteira = models.CharField(max_length=5)
    aceite = models.CharField(max_length=1, default='N')

    valor_documento = models.DecimalField(u'Valor do Documento',
                                          max_digits=8, decimal_places=2)
    valor = models.DecimalField(max_digits=8,
                                decimal_places=2, blank=True, null=True)

    data_vencimento = models.DateField(u'Data de Vencimento')
    data_documento = models.DateField(u'Data do Documento')
    data_processamento = models.DateField(u'Data de Processamento',
                                          auto_now=True)

    numero_documento = models.CharField(u'Número do Documento', max_length=11)

    # Informações do Cedente
    agencia_cedente = models.CharField(u'Agência Cedente', max_length=4)
    conta_cedente = models.CharField('Conta Cedente', max_length=7)

    cedente = models.CharField(u'Nome do Cedente', max_length=255)
    cedente_documento = models.CharField(u'Documento do Cedente',
                                         max_length=50)
    cedente_cidade = models.CharField(u'Cidade do Cedente', max_length=255)
    cedente_uf = models.CharField(u'Estado do Cedente', max_length=2)
    cedente_endereco = models.CharField(u'Endereço do Cedente',  max_length=255)
    cedente_bairro = models.CharField(u'Bairro do Cedente', max_length=255)
    cedente_cep = models.CharField(u'CEP do Cedente', max_length=9)

    # Informações do Sacado
    sacado_nome = models.CharField(u'Nome do Sacado', max_length=255)
    sacado_documento = models.CharField(u'Documento do Sacado', max_length=255)
    sacado_cidade = models.CharField(u'Cidade do Sacado', max_length=255)
    sacado_uf = models.CharField(u'Estado do Sacado', max_length=2)
    sacado_endereco = models.CharField(u'Endereço do Sacado', max_length=255)
    sacado_bairro = models.CharField(u'Bairro do Sacado', max_length=255)
    sacado_cep = models.CharField(u'CEP do Sacado', max_length=9)

    # Informações Opcionais
    quantidade = models.CharField(u'Quantidade', max_length=10, blank=True)
    especie_documento = models.CharField(u'Espécie do Documento',
                                         max_length=255, blank=True)
    especie = models.CharField(u'Espécie', max_length=2, default="R$")
    moeda = models.CharField(max_length=2, default='9')
    local_pagamento = models.CharField(u'Local de Pagamento', max_length=255, default=u'Pagável em qualquer banco até o vencimento')
    demonstrativo = models.TextField(blank=True)
    juros_mora_taxa = models.DecimalField(max_digits=8, decimal_places=2, default=0.2)
    instrucoes = models.TextField(u'Instruções',
                                  default=u"1 - Não receber após 30 dias. \n" +
                                  "2 - Multa de 2% após o vencimento. \n" +
                                  "3 - Taxa diária de permanência de {:.2f}.")

    def __unicode__(self):
        return self.numero_documento

    def __str__(self):
        return self.numero_documento

    def print_pdf_pagina(self, pdf_file):
        from pyboleto import bank

        ClasseBanco = bank.get_class_for_codigo(self.codigo_banco)

        boleto_dados = ClasseBanco()
        for field in self._meta.get_fields():
            if getattr(self, field.name):
                # if field.name == 'instrucoes':
                #    print(self.instrucoes)
                setattr(boleto_dados, field.name, getattr(self, field.name))

        setattr(boleto_dados, 'nosso_numero',
                getattr(self, 'numero_documento'))
        valor_dia = '{:.2f}'.format(self.valor*self.juros_mora_taxa/100).replace('.', ',')
        setattr(boleto_dados, 'instrucoes', self.instrucoes.format(valor_dia))

        pdf_file.drawBoleto(boleto_dados)
