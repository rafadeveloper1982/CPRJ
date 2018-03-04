# -*- coding: utf-8 -*-

import io

from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from django.http import HttpResponse
from django.contrib import admin
from .models import Boleto, Banco, Conta
from pyboleto.pdf import BoletoPDF
from unicodedata import normalize

from associados.models import ContasaReceberConsolidado


def remover_acentos(txt):
    return normalize('NFKD', txt).encode('ASCII', 'ignore').decode('ASCII')


def modulo11(num, base=9, r=0):
        if not isinstance(num, str):
            raise TypeError
        soma = 0
        fator = 2
        for c in reversed(num):
            soma += int(c) * fator
            if fator == base:
                fator = 1
            fator += 1
        if r == 0:
            soma = soma * 10
            digito = soma % 11
            if digito == 10:
                digito = 0
            return digito
        if r == 1:
            resto = soma % 11
            return resto


def print_boletos(modeladmin, request, queryset):
    buffer = io.BytesIO()   # io.StringIO()
    boleto_pdf = BoletoPDF(buffer)

    for b in queryset:
        b.print_pdf_pagina(boleto_pdf)
        boleto_pdf.nextPage()

    boleto_pdf.save()

    pdf_file = buffer.getvalue()

    # response = HttpResponse(mimetype='application/pdf')
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=%s' % (
        u'boletos_%s.pdf' % (
            date.today().strftime('%Y%m%d'),
        ),
    )
    response.write(pdf_file)
    return response


print_boletos.short_description = u'Imprimir Boletos Selecionados'


def enviar_email(modeladmin, request, queryset):
    from django.core.mail import EmailMessage

    titulo = 'Circulo psicanalítico - Boleto de cobrança %s'
    texto = u"""
             Segue em anexo boleto n. %s.
             Associado: %s
             Valor: %s
             data de vencimento: %s
             Pague a mensalidade em dia evitando multas
             """

    for b in queryset:
        buffer = io.BytesIO()   # io.StringIO()
        boleto_pdf = BoletoPDF(buffer)

        b.print_pdf_pagina(boleto_pdf)
        boleto_pdf.nextPage()
        boleto_pdf.save()
        pdf_file = buffer.getvalue()
        buffer.close

        content = texto % (b.numero_documento, b.sacado_nome, b.valor_documento, b.data_vencimento)

        consolidado = ContasaReceberConsolidado.objects.filter(boleto=b.numero_documento)[0]

        if consolidado:

            email = consolidado.associado.email

            if email:
                msg = EmailMessage(titulo % (b.numero_documento),
                                   content,
                                   to=[email])
                msg.attach('boleto.pdf', pdf_file, 'application/pdf')
                msg.content_subtype = "html"
                msg.send()


enviar_email.short_description = u'Enviar Boletos Selecionados'


def gerar_arquivo_remessa(modeladmin, request, queryset):
    from boleto.models import Conta
    from decimal import Decimal
    from cnab240.bancos import santander
    from cnab240.tipos import Arquivo

    conta = Conta.objects.all()[0]
    # data_documento = datetime.today().date()
    ultimo = conta.numero_documento

    dict_arquivo = {
        'cedente_inscricao_tipo': 2,
        'cedente_inscricao_numero':34117705000105,
        #'cedente_inscricao_numero': int(conta.cedente_documento),
        'cedente_agencia': conta.agencia_cedente,
        'cedente_conta': conta.conta_cedente,
        'cedente_agencia_conta_dv': conta.digito_agencia_cedente,
        'cedente_nome': remover_acentos(conta.cedente),
        'arquivo_data_de_geracao': int(date.today().strftime('%d%m%Y')),
        'arquivo_hora_de_geracao': int(datetime.now().time().strftime('%H%M%S')),
        'arquivo_sequencia': conta.cedente_seguencia_arquivo + 1,
        'codigo_transmissao': int(conta.codigo_transmissao),
        'codigo_remessa': 1,
        'controlecob_data_gravacao': int(date.today().strftime('%d%m%Y'))
    }

    arquivo = Arquivo(santander, **dict_arquivo)

    for boleto in queryset:
        ultimo = ultimo + 1
        if True:
            data_multa = boleto.data_vencimento + relativedelta(days=+1)

            if boleto.sacado_cep == 'nan':
                cep = '22261-010'
            else:
                cep = boleto.sacado_cep
            

            dict_cobranca = {
                'cedente_agencia': int(conta.agencia_cedente),
                'cedente_conta': int(conta.conta_cedente),
                'cedente_conta_dv': int(conta.digito_conta_cedente),
                'conta_cobranca': int(conta.conta_cobranca),
                'conta_cobranca_dv': int(conta.digito_conta_cobranca),
                'cedente_agencia_conta_dv': conta.digito_agencia_cedente,
                'carteira_numero': conta.carteira_remessa,
                'nosso_numero': int("%s%s" % (boleto.numero_documento, modulo11(boleto.numero_documento))),
                'numero_documento':'34117705/0001-0',
                #'numero_documento': boleto.cedente_documento,
                'vencimento_titulo': int(boleto.data_vencimento.strftime('%d%m%Y')),
                'valor_titulo': Decimal(boleto.valor_documento),    
                'especie_titulo': conta.especie_documento,
                'aceite_titulo': conta.aceite,
                'data_emissao_titulo': int(date.today().strftime('%d%m%Y')),
                'codigo_juros': conta.codigo_juros,
                'juros_mora_data': int(boleto.data_vencimento.strftime('%d%m%Y')),
                'juros_mora_taxa': Decimal(round(boleto.valor_documento*boleto.juros_mora_taxa/100, 2)),
                'identificacao_titulo': boleto.numero_documento,
                'codigo_protesto': 3,
                'prazo_protesto': 0,
                'codigo_baixa': conta.codigo_baixa,
                'prazo_baixa': conta.prazo_baixa,
                'sacador_inscricao_tipo': 0,
                'sacado_inscricao_tipo': 1,
                'carne_identificador': 000,
                'sacado_inscricao_numero': int(boleto.sacado_documento),
                'sacado_nome': remover_acentos(boleto.sacado_nome),
                'sacado_endereco': remover_acentos(boleto.sacado_endereco),
                'sacado_bairro': remover_acentos(boleto.sacado_bairro),
                'sacado_cep': int(cep[:5]),
                'sacado_cep_sufixo': int(cep[-3:]),
                'sacado_cidade': remover_acentos(boleto.sacado_cidade),
                'sacado_uf': boleto.sacado_uf,
                'codigo_multa': conta.codigo_multa,
                'data_multa':  int(data_multa.strftime('%d%m%Y')),
                'juros_multa': conta.multa,
            }

            arquivo.incluir_cobranca(dict_arquivo, **dict_cobranca)

    conta.cedente_seguencia_arquivo = conta.cedente_seguencia_arquivo + 1
    conta.save()
    response = HttpResponse(content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename=%s' % (
        u'remessa_%s.txt' % (
            date.today().strftime('%Y%m%d'),
        ),
    )
    response.write(arquivo)
    return response


@admin.register(Boleto)
class BoletoAdmin(admin.ModelAdmin):
    list_display = ('numero_documento',
                    'sacado_nome',
                    'data_vencimento',
                    'data_documento',
                    'valor_documento')
    search_fields = ('numero_documento', 'sacado_nome')
    date_hierarchy = 'data_documento'
    list_filter = ('data_vencimento', 'data_documento')
    actions = (print_boletos, gerar_arquivo_remessa, enviar_email, )
    fieldsets = (
        (None, {
            'fields': (('codigo_banco', 'carteira', 'aceite', ),
                       ('valor_documento', 'valor',),
                       ('data_vencimento', 'data_documento',),
                       # 'data_processamento',
                       'numero_documento', ),
        }),
        ('Cedente', {
            'fields': (('agencia_cedente', 'conta_cedente', ),
                       'cedente', 'cedente_documento',
                       'cedente_endereco', ('cedente_bairro', 'cedente_cep'),
                       'cedente_cidade', 'cedente_uf', ),
            'classes': ('collapse',),
        }),
        ('Sacado', {
            'fields': (('sacado_nome', 'sacado_documento', ),
                       'sacado_endereco', ('sacado_bairro', 'sacado_cep'),
                       'sacado_cidade', 'sacado_uf', ),
            'classes': ('collapse',),
        }),
        (None, {
            'fields': (
                # Informações Opcionais
                'quantidade',
                'especie_documento',
                'especie',
                'moeda',
                'local_pagamento',
                'juros_mora_taxa',
                'instrucoes',),
        }),
    )

    class Media:
        css = {
            'all': ('css/custom_admin.css', )     # Include extra css
        }


@admin.register(Banco)
class BancoAdmin(admin.ModelAdmin):
    list_display = ('codigo_banco', 'nome_banco')


@admin.register(Conta)
class ContaAdmin(admin.ModelAdmin):
    list_display = ('banco', 'numero_documento', 'agencia_cedente',
                    'digito_agencia_cedente', 'conta_cedente',
                    'digito_conta_cedente')
    fieldsets = (
        (None, {
            'fields': (('banco', 'carteira', 'aceite',),
                       'numero_documento', 'carteira_remessa',
                       'cedente_seguencia_arquivo', 'codigo_transmissao', ),
        }),
        ('Cedente', {
            'fields': (('agencia_cedente', 'digito_agencia_cedente',
                       'conta_cedente', 'digito_conta_cedente',),
                       ('conta_cobranca', 'digito_conta_cobranca',),
                       'cedente',
                       'cedente_documento', 'cedente_endereco',
                       ('cedente_bairro', 'cedente_cep'),
                       'cedente_cidade', 'cedente_uf', ),
            'classes': ('collapse',),
        }),

        (None, {
            'fields': (
                # Informações Opcionais
                'codigo_baixa',
                'prazo_baixa',
                'especie_documento',
                'especie',
                'moeda',
                'local_pagamento',
                'codigo_juros',
                'juros_mora_taxa',
                'codigo_multa',
                'multa',
                'instrucoes', ),
        }),
    )

    class Media:
        css = {
            'all': ('css/custom_admin.css', )     # Include extra css
        }
