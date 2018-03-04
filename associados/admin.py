from django.contrib import admin
from django.urls import resolve

from django.contrib import messages

from .models import Associado, Categoria, Seminario, ContasaReceber, ContasaReceberConsolidado
from .models import Professores, Titulos, LancamentosMensais, Matricula, Turma, DataAula, ControlePresenca

from datetime import datetime
from dateutil.relativedelta import relativedelta
from .forms import MantriculaForm

import nested_admin


def gerar_mensalidade_proximo_mes(modeladmin, request, queryset):
    associados = queryset.filter(ativo=1)
    contador = 0
    contador2 = 0
    for associado in associados:
        database = datetime.today().date() + relativedelta(months=+1)
        database = database.replace(day=10)
        contasareceber = ContasaReceber.objects.filter(associado=associado, tipo='m', data_de_vencimento__gte=database)
        if (not contasareceber.exists()) and (associado.categoria.gera_financeiro == 1):
            c = ContasaReceber(associado=associado,
                               tipo='m',
                               valor=associado.categoria.valor,
                               data_de_vencimento=database)
            c.save()
            contador = contador + 1
        else:
            contador2 = contador2 + 1

    if contador > 0:
        messages.success(request, "%s Mensalidades geradas com sucesso!" % contador)
    if contador2 > 0:
        messages.error(request, "Já existem  %s mensalidades criadas para o período informado" % contador2)


def gerar_mensalidade__mes_atual(modeladmin, request, queryset):
    associados = queryset.filter(ativo=1)
    contador = 0
    contador2 = 0
    for associado in associados:
        database = datetime.today().date()
        database = database.replace(day=10)
        contasareceber = ContasaReceber.objects.filter(associado=associado, tipo='m', data_de_vencimento__gte=database)
        if (not contasareceber.exists()) and (associado.categoria.gera_financeiro == 1):
            c = ContasaReceber(associado=associado,
                               tipo='m',
                               valor=associado.categoria.valor,
                               data_de_vencimento=database)
            c.save()
            contador = contador + 1
        else:
            contador2 = contador2 + 1

    if contador > 0:
        messages.success(request, "%s Mensalidades geradas com sucesso!" % contador)
    if contador2 > 0:
        messages.error(request, "%s já foram geradas ou não obedecem os parâmetros de lançamento " % contador2)


def gerar_boleto_mes(modeladmin, request, queryset):
    from boleto.models import Conta, Boleto

    conta = Conta.objects.all()[0]

    data_documento = datetime.today().date()
    ultimo = conta.numero_documento

    for consolidado in queryset:
        ultimo = ultimo + 1

        if consolidado.associado.endereco_residencial and consolidado.associado.bairro_residencial and consolidado.associado.cep_residencial:
            endereco = consolidado.associado.endereco_residencial
            bairro = consolidado.associado.bairro_residencial
            cep = consolidado.associado.cep_residencial
        else:
            endereco = consolidado.associado.endereco
            bairro = consolidado.associado.bairro
            cep = consolidado.associado.cep

        if not consolidado.boleto_gerado and endereco and bairro and cep:
            boleto = Boleto(codigo_banco=conta.banco.codigo_banco,
                            carteira=conta.carteira,
                            aceite='N',
                            valor_documento=consolidado.valor_cobrado,
                            valor=consolidado.valor_cobrado,

                            data_vencimento=consolidado.data_de_vencimento,
                            data_documento=data_documento,
                            data_processamento=data_documento,

                            numero_documento=ultimo,

                            # Informações do Cedente
                            agencia_cedente=conta.agencia_cedente,
                            conta_cedente=conta.conta_cedente,

                            cedente=conta.cedente,
                            cedente_documento=conta.cedente_documento,
                            cedente_cidade=conta.cedente_cidade,
                            cedente_uf=conta.cedente_uf,
                            cedente_endereco=conta.cedente_endereco,
                            cedente_bairro=conta.cedente_bairro,
                            cedente_cep=conta.cedente_cep,

                            # Informações do Sacado
                            sacado_nome=consolidado.associado.nome,
                            sacado_documento=consolidado.associado.cpf,
                            sacado_cidade=consolidado.associado.cidade,
                            sacado_uf=consolidado.associado.estado,
                            sacado_endereco=endereco,
                            sacado_bairro=bairro,
                            sacado_cep=cep,

                            # Informações Opcionais
                            quantidade='',
                            especie_documento=conta.especie_documento,
                            especie=conta.especie,
                            moeda=conta.moeda,
                            local_pagamento=conta.local_pagamento,
                            demonstrativo='',
                            instrucoes=conta.instrucoes,)
            boleto.save()

            contasaReceberConsolidado = ContasaReceberConsolidado.objects.get(pk=consolidado.pk)
            contasaReceberConsolidado.boleto = ultimo
            contasaReceberConsolidado.boleto_gerado = True
            contasaReceberConsolidado.save()
            conta.numero_documento = ultimo
            conta.save()

def baixar_financeiro(modeladmin, request, queryset):

    data = datetime.now().date()
    cc = queryset.exclude(status__contains='l')
    for i in cc:
        i.status = 'l'
        i.recebido = True
        i.data_de_recebimento = data
        i.save()
        print('salvo com sucesso')






@admin.register(Categoria)
class CategoriaAdmin(nested_admin.NestedModelAdmin):
    list_display = ('categoria', 'valor', 'gera_financeiro')


@admin.register(Seminario)
class SeminarioAdmin(nested_admin.NestedModelAdmin):
    # actions = [make_published]
    autocomplete_fields = ('seminario',)
    list_display = ('seminario', 'todosProfessores', 'tipo', 'vl_hora_aula')
    list_filter = ('tipo', 'seminario')
    search_fields = ['seminario__titulos', 'tipo', 'vl_hora_aula']


@admin.register(Professores)
class ProfessoresAdmin(nested_admin.NestedModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)


@admin.register(Titulos)
class TitulosAdmin(nested_admin.NestedModelAdmin):
    list_display = ('titulos',)
    search_fields = ('titulos',)    # valor_aula = forms.CharField(required=False)


class inlineContasaReceber(nested_admin.NestedTabularInline):
    model = ContasaReceber
    extra = 0
    list_display = ['lancamentos_mensais', 'data_de_vencimento', 'data_de_recebimento', 'valor', 'recebido']
    readonly_fields = ['tipo', 'lancamentos_mensais', 'data_de_vencimento', 'data_de_recebimento', 'valor', 'recebido']
    can_delete = False
    classes = ['collapse']
    # exclude=['associado', 'tipo']

    class Media:
        css = {
            'all': ('css/custom_admin.css', )     # Include extra css
        }

    def has_add_permission(self, request):
        return False


class inlineLancamentosMensais(nested_admin.NestedTabularInline):
    model = LancamentosMensais
    extra = 0
    readonly_fields = ['qt_hora', 'vl_hora_aula', 'valor', 'recebido', 'data_de_recebimento']
    fields = ['qt_hora', 'vl_hora_aula',  'valor', 'data_de_recebimento', 'recebido']
    can_delete = False

    def has_add_permission(self, request):
        return False


class inlineControlePresenca(nested_admin.NestedTabularInline):
    model = ControlePresenca
    extra = 0
    readonly_fields = ['associado']
    fields = ['associado', 'presente']
    can_delete = False
    classes = ['collapse']

    class Media:
        css = {
            'all': ('css/custom_admin.css', )     # Include extra css
        }

    def has_add_permission(self, request):
        return False


class inlineDataAula(nested_admin.NestedTabularInline):
    model = DataAula
    inlines = [inlineControlePresenca]
    extra = 0
    can_delete = True
    classes = ['collapse']

    class Media:
        css = {
            'all': ('css/custom_admin.css', )     # Include extra css
        }


class inlineMatricula(nested_admin.NestedTabularInline):
    model = Matricula
    inlines = [inlineLancamentosMensais]
    extra = 0
    readonly_fields = ['associado', 'turma', 'data_de_matricula', 'data_de_conclusao']
    can_delete = False
    classes = ['collapse']

    def has_add_permission(self, request):
        return False

    class Media:
        js = ['js/vendor/jquery/jquery.min.js',
              'js/associados/lancamentos.js']
        css = {
            'all': ('css/custom_admin.css', )     # Include extra css
        }


@admin.register(Matricula)
class MatriculaAdmin(nested_admin.NestedModelAdmin):
    inlines = [inlineLancamentosMensais]
    autocomplete_fields = ['associado', 'turma']
    list_display = ('associado', 'turma', 'data_de_matricula', 'data_de_conclusao', 'valor_aula')
    search_fields = ['associado__nome', ]
    fields = ('associado', 'turma', ('data_de_matricula', 'data_de_conclusao', 'valor_aula'))
    form = MantriculaForm

    def valor_aula(self, obj):
        return obj.turma.seminario.vl_hora_aula
    valor_aula.short_description = 'valor aula'

    class Media:
        js = ['js/vendor/jquery/jquery.min.js',
              'js/associados/lancamentos.js']
        css = {
            'all': ('css/custom_admin.css', )     # Include extra css
        }


class inlineContasaReceberConsolidado(nested_admin.NestedTabularInline):
    model = ContasaReceber
    extra = 0
    fields = ['tipo', 'lancamentos_mensais', 'valor']
    readonly_fields = ('lancamentos_mensais',)

    class Media:
        js = ['js/vendor/jquery/jquery.min.js',
              'js/associados/consolidado.js']
        css = {
            'all': ('css/custom_admin.css', )     # Include extra css
        }


@admin.register(ContasaReceberConsolidado)
class ContasaReceberConsolidadoAdmin(nested_admin.NestedModelAdmin):
    inlines = [inlineContasaReceberConsolidado]
    actions = [gerar_boleto_mes, baixar_financeiro]
    list_display = ('associado', 'status', 'valor_cobrado', 'data_de_vencimento', 'boleto_gerado', 'data_de_recebimento', 'recebido')
    list_filter = ('status', 'data_de_vencimento', 'boleto_gerado', 'data_de_recebimento', 'recebido')
    search_fields = ['associado__nome', 'valor_cobrado', 'data_de_vencimento', 'data_de_recebimento', 'recebido']
    fields = ['associado', 'status', ('data_de_vencimento', 'valor_cobrado',), ('data_de_recebimento', 'recebido', 'boleto_gerado')]
    #can_delete = False

    def associadoCodigo(self, obj):
        return obj.associado.nome
    associadoCodigo.short_description = 'nome'
'''
    #def has_add_permission(self, request):
        #return False

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = ['associado', 'status', 'valor_cobrado']
        if obj:
            return ['associado', 'status', 'valor_cobrado', 'data_de_vencimento', 'data_de_recebimento', 'recebido', 'boleto_gerado']
        else:
            return readonly_fields

    #def has_delete_permission(self, request, obj=None):
        #return False

'''
@admin.register(ContasaReceber)
class ContasaReceberAdmin(nested_admin.NestedModelAdmin):
    autocomplete_fields = ['associado']
    list_display = ('associado', 'tipo', 'valor', 'data_de_vencimento', 'data_de_recebimento', 'recebido')
    list_filter = ('tipo', 'data_de_vencimento', 'data_de_recebimento', 'recebido')
    search_fields = ['associado__nome', 'valor', 'data_de_vencimento', 'data_de_recebimento', 'recebido']
    fields = ['associado', 'tipo',  'lancamentos_mensais', 'contas_areceber_consolidado', ('data_de_vencimento', 'valor',),
              ('data_de_recebimento', 'recebido',)]

    readonly_fields = ['associado', 'tipo',  'lancamentos_mensais', 'contas_areceber_consolidado', 'valor', 'data_de_vencimento']

    def associadoCodigo(self, obj):
        return obj.associado.nome
    associadoCodigo.short_description = 'nome'

    def has_add_permission(self, request):
        return False

    '''
    def get_readonly_fields(self, request, obj=None):
        readonly_fields = ['lancamentos_mensais']
        if obj:
            return ['associado', 'tipo',  'lancamentos_mensais', 'valor', 'data_de_vencimento']
        else:
            return readonly_fields
    '''

    '''
    def has_delete_permission(self, request, obj=None):
        if obj:
            if obj.lancamentos_mensais:
                return False
            else:
                return True
        else:
            return False
    '''

    '''
    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        c = ContasaReceber.objects.get(pk=object_id)
        print(object_id)
        print(self)
        print(request)
        extra_context['show_save_and_continue'] = False
        extra_context['show_save'] = False
        extra_context['show_save_and_add_another'] = False  # this not works if has_add_permision is True
        return super(ContasaReceberAdmin, self).change_view(request, object_id, extra_context=extra_context)
    '''

    class Meta:
        default_related_name = 'Contas a receber'

    class Media:
        css = {
            'all': ('css/custom_admin.css', )     # Include extra css
        }


@admin.register(Associado)
class AssociadoAdmin(nested_admin.NestedModelAdmin):
    inlines = [inlineContasaReceber, inlineMatricula]
    actions = [gerar_mensalidade__mes_atual, gerar_mensalidade_proximo_mes]
    list_display = ('referencia', 'nome', 'categoria', 'telefone',  'celular', 'ativo')
    list_filter = ('ativo', 'categoria')
    search_fields = ['referencia', 'nome', 'telefone', 'ativo']
    fieldsets = (
        (None, {
            'fields': (('referencia', 'nome',), ('cpf', 'data_de_nascimento',), ('categoria', 'email',), 'ano_de_formacao', 'ativo', 'historico',)
        }),
        ('Endereço', {
            'fields': ('endereco', ('bairro', 'cep'), 'cidade', 'estado', 'pais', ),
            'classes': ('collapse',),
        }),
        ('Telefones', {
            'fields': (('telefone', 'celular', 'celular2'),),
            'classes': ('collapse',),
        }),
        ('Endereço Residencial', {
            'fields': ('endereco_residencial', ('bairro_residencial', 'cep_residencial'), 'cidade_residencial', 'estado_residencial', 'pais_residencial', 'telefone_residencial',),
            'classes': ('collapse',),
        }),
    )


class inlineMatriculados(nested_admin.NestedTabularInline):
    verbose_name = 'Matriculado'
    verbose_name_plural = 'Matriculados'
    model = Matricula
    extra = 0
    readonly_fields = ['associado', 'data_de_matricula', 'data_de_conclusao']
    can_delete = False
    classes = ['collapse']

    def has_add_permission(self, request):
        return False

    class Media:
        js = ['js/vendor/jquery/jquery.min.js']
        css = {
            'all': ('css/custom_admin.css', )     # Include extra css
        }


class inlineMatricular(nested_admin.NestedTabularInline):
    verbose_name = 'Matricular'
    verbose_name_plural = 'Matricular'
    model = Matricula
    extra = 0
    readonly_fields = []
    can_delete = False
    autocomplete_fields = ['associado']
    classes = ['collapse']

    def has_change_permission(self, obj=None):
        return False

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        object_id = None
        try:
            object_id = resolve(request.path).kwargs['object_id']
        except:
            pass

        field = super(inlineMatricular, self).formfield_for_foreignkey(db_field, request, **kwargs)
        if db_field.name == 'associado' and object_id is not None:
            if request is not None:
                field.queryset = field.queryset.exclude(matricula__turma__id=object_id)
            else:
                field.queryset = field.queryset.none()

        return field

    '''
    def get_readonly_fields(self, request, obj=None):
        if obj:      # editing an existing object
            return ['associado', 'data_de_matricula', 'data_de_conclusao']
        return self.readonly_fields
    '''
    # def has_add_permission(self, request):
    #    return False

    class Media:
        js = ['js/vendor/jquery/jquery.min.js']
        css = {
            'all': ('css/custom_admin.css', )     # Include extra css
        }


@admin.register(Turma)
class TurmaAdmin(nested_admin.NestedModelAdmin):
    inlines = [inlineMatriculados, inlineMatricular, inlineDataAula]
    autocomplete_fields = ['seminario']
    search_fields = ['seminario__seminario__titulos']
    list_display = ('seminario', 'data_inicio', 'data_final')
    # search_fields = ['seminario__nome', ]
    fields = ('seminario', ('data_inicio', 'data_final'))
