from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save
from dateutil.relativedelta import relativedelta
from datetime import datetime
from django.db.models import Sum
# from boleto.models import Boleto


# Create your models here.

STATUS_CHOICES = (
    ('p', 'Palestra'),
    ('a', 'Aula'),
    ('s', 'Seminário')
)


class Categoria(models.Model):
    categoria = models.CharField(max_length=35)
    gera_financeiro = models.BooleanField(default=True)
    valor = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.categoria


class Professores(models.Model):
    nome = models.CharField('Nome', max_length=55)
    obs = models.TextField('Observações', blank=True, null=True)

    class Meta:
        verbose_name_plural = 'Cadastro de professores'
        verbose_name = 'Professor'
        ordering = ('nome',)

    def __str__(self):
        return '%s' % (self.nome)


class Titulos(models.Model):
        titulos = models.CharField('Nome', max_length=100)
        descricao = models.TextField('Descrição', null=True, blank=True)

        def __str__(self):
            return self.titulos

        class Meta:
            verbose_name_plural = 'Cadastro de títulos'
            ordering = ('titulos',)


class Associado(models.Model):
    id = models.AutoField(primary_key=True)
    referencia = models.IntegerField('Código do associado')
    nome = models.CharField('nome associado', max_length=100)
    endereco = models.CharField('endereço', max_length=200, null=True, blank=True)
    bairro = models.CharField(max_length=45, null=True, blank=True)
    cep = models.CharField(max_length=10, null=True, blank=True)
    cidade = models.CharField(max_length=25, null=True, blank=True)
    estado = models.CharField(max_length=4, null=True, blank=True)
    pais = models.CharField(max_length=25, null=True, blank=True)
    telefone = models.CharField(max_length=15, null=True, blank=True)
    celular = models.CharField(max_length=15, null=True, blank=True)
    celular2 = models.CharField(max_length=15, null=True, blank=True)
    endereco_residencial = models.CharField('endereço residencial', max_length=200, null=True, blank=True)
    bairro_residencial = models.CharField(max_length=25, null=True, blank=True)
    cep_residencial = models.CharField(max_length=10, null=True, blank=True)
    cidade_residencial = models.CharField(max_length=25, null=True, blank=True)
    estado_residencial = models.CharField(max_length=4, null=True, blank=True)
    pais_residencial = models.CharField(max_length=25, null=True, blank=True)
    telefone_residencial = models.CharField(max_length=15, null=True, blank=True)
    email = models.EmailField(max_length=100, null=True, blank=True)
    data_de_nascimento = models.DateField(null=True, blank=True)
    cpf = models.CharField(max_length=20, null=True, blank=True)
    ano_de_formacao = models.IntegerField('ano de formação',  null=True, blank=True)
    historico = models.TextField(null=True, blank=True)
    ativo = models.BooleanField(default=True)
    categoria = models.ForeignKey(Categoria, null=True, blank=True, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Cadastro de associado'
        ordering = ('nome',)

    def __str__(self):
        return '%s - %s' % (self.id, self.nome)


class Seminario(models.Model):
    seminario = models.ForeignKey(Titulos, max_length=100,  null=True, blank=False, on_delete=models.CASCADE)
    professor = models.ManyToManyField(Professores, blank=False)
    tipo = models.CharField('Tipo', max_length=10, null=True, blank=True,  choices=STATUS_CHOICES, default='s')
    vl_hora_aula = models.DecimalField('Valor hora/aula', max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        todos = ""
        for p in self.professor.all():
            todos = todos+p.nome+','
        return '%s - %s - %s' % (self.seminario, self.vl_hora_aula, todos)

    def todosProfessores(self):
        todos = ""
        for p in self.professor.all():
            todos = todos + p.nome + ', '
        return todos
    todosProfessores.short_description = 'Professores'

    class Meta:
        verbose_name_plural = 'Cadastro de seminários e aulas'


class Turma(models.Model):
    seminario = models.ForeignKey(Seminario, on_delete=models.CASCADE)
    data_inicio = models.DateField('Data de inicio', null=True, blank=True)
    data_final = models.DateField('Data final', null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Turmas'
        verbose_name = 'Turma'

    def __str__(self):
        return '%s' % (self.seminario)


class DataAula(models.Model):
    turma = models.ForeignKey(Turma, on_delete=models.CASCADE)
    data = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = 'Data da aula'
        verbose_name_plural = 'Datas das aulas'

    def __str__(self):
        return '%s' % (self.data)

    # delete ControlePresenca cascate


class Matricula(models.Model):
    associado = models.ForeignKey(Associado, null=True, blank=False, on_delete=models.CASCADE)
    turma = models.ForeignKey(Turma, null=True, blank=False, on_delete=models)
    data_de_matricula = models.DateField('Data de matricula', null=True)
    data_de_conclusao = models.DateField('Data de conclusão', null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Matriculas'
        unique_together = ('associado', 'turma',)

    def __str__(self):
        return '%s' % (self.associado)


class LancamentosMensais(models.Model):
    matricula = models.ForeignKey(Matricula, null=True, blank=False, on_delete=models.CASCADE)
    qt_hora = models.IntegerField('Quantidade de aulas')
    vl_hora_aula = models.DecimalField('Valor hora/aula', max_digits=10, decimal_places=2, default=0)
    valor = models.DecimalField('Valor total', max_digits=10, decimal_places=2)
    data_de_recebimento = models.DateField('Data de recebimento', null=True, blank=True)
    recebido = models.BooleanField('Recebido', default=False)

    class Meta:
        verbose_name_plural = 'Lançamentos mensais'

    def save(self, *args, **kwargs):
        self.valor = self.qt_hora * self.matricula.turma.seminario.vl_hora_aula
        if self.data_de_recebimento:
            self.recebido = True

        super(LancamentosMensais, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        consolidado = ContasaReceber.objects.filter(lancamentos_mensais=self)[0].contas_areceber_consolidado
        ContasaReceber.objects.filter(lancamentos_mensais=self).delete()
        soma = ContasaReceber.objects.filter(contas_areceber_consolidado=consolidado).aggregate(soma=Sum('valor'))

        if soma['soma']:
            ContasaReceberConsolidado.objects.filter(pk=consolidado.pk).update(valor_cobrado=soma['soma'])
        else:
            ContasaReceberConsolidado.objects.filter(pk=consolidado.pk).delete()

        super(LancamentosMensais, self).delete(*args, **kwargs)

    def __str__(self):
        return '%s' % (self.matricula.turma)


TSTATUS_CHOICES = (('a', 'Aberto'),
                   ('b', 'boleto gerado'),
                   ('l', 'liquidado'))


class ContasaReceberConsolidado(models.Model):
    associado = models.ForeignKey(Associado, on_delete=models.CASCADE)
    status = models.CharField('Status', max_length=10, null=True, blank=True, choices=TSTATUS_CHOICES, default='a')
    valor_cobrado = models.DecimalField(max_digits=10, decimal_places=2)
    data_de_vencimento = models.DateField('Data de Vencimento')
    data_de_recebimento = models.DateField('Data de Recebimento', null=True, blank=True)
    recebido = models.BooleanField("Recebido", default=False)
    boleto = models.IntegerField(null=True, blank=True)
    boleto_gerado = models.BooleanField('Boleto gerado?', default=False)

    class Meta:
        verbose_name_plural = 'Contas a receber'

    def __str__(self):
        return '%s' % (self.data_de_vencimento)


TIPO_CHOICES = (('m', 'mensalidade'),
                ('s', 'seminario'),
                ('m', 'multa'),
                ('v', 'vencimentos em atraso'),
                ('n', 'multa de vencimentos em atraso'),
                ('o', 'outros'))


class ContasaReceber(models.Model):
    associado = models.ForeignKey(Associado, on_delete=models.CASCADE)
    tipo = models.CharField('Tipo', max_length=10, null=True, blank=True, choices=TIPO_CHOICES, default='o')
    lancamentos_mensais = models.ForeignKey(LancamentosMensais, null=True, blank=True, on_delete=models.CASCADE)
    contas_areceber_consolidado = models.ForeignKey(ContasaReceberConsolidado, null=True, blank=True, on_delete=models.CASCADE)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data_de_vencimento = models.DateField('Data de Vencimento')
    data_de_recebimento = models.DateField('Data de Recebimento', null=True, blank=True)
    recebido = models.BooleanField("Recebido", default=False)

    class Meta:
        verbose_name_plural = 'Lançamentos Financeiros'

    def __str__(self):
        return '%s' % (self.associado)

    def save(self, *args, **kwargs):
        if not self.associado_id:
            self.associado = self.contas_areceber_consolidado.associado
        if not self.data_de_vencimento:
            self.data_de_vencimento = self.contas_areceber_consolidado.data_de_vencimento
        if self.lancamentos_mensais:
            LancamentosMensais.objects.filter(pk=self.lancamentos_mensais.pk).update(
                data_de_recebimento=self.data_de_recebimento,
                recebido=self.recebido
            )

        super(ContasaReceber, self).save(*args, **kwargs)


class ControlePresenca(models.Model):
    data_aula = models.ForeignKey(DataAula, on_delete=models.CASCADE)
    associado = models.ForeignKey(Associado, null=True, blank=True, on_delete=models.CASCADE)
    presente = models.BooleanField("Presente", default=True)
    lancamentos_mensais = models.ForeignKey(LancamentosMensais, null=True, blank=True, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = 'Controle de Presenças'

    def save(self, *args, **kwargs):
        totalPresenca = ControlePresenca.objects.filter(lancamentos_mensais=self.lancamentos_mensais).count()

        LancamentosMensais.objects.filter(pk=self.lancamentos_mensais.pk).update(
            qt_hora=totalPresenca,
            vl_hora_aula=self.data_aula.turma.seminario.vl_hora_aula,
            valor=self.data_aula.turma.seminario.vl_hora_aula*totalPresenca
        )

        contasareceber = ContasaReceber.objects.filter(lancamentos_mensais=self.lancamentos_mensais)[0]
        ContasaReceber.objects.filter(pk=contasareceber.pk).update(valor=self.data_aula.turma.seminario.vl_hora_aula*totalPresenca)
        soma = ContasaReceber.objects.filter(contas_areceber_consolidado=contasareceber.contas_areceber_consolidado).aggregate(soma=Sum('valor'))
        ContasaReceberConsolidado.objects.filter(pk=contasareceber.contas_areceber_consolidado.pk).update(valor_cobrado=soma['soma'])
        super(ControlePresenca, self).save(*args, **kwargs)


'''
@receiver(post_save, sender=LancamentosMensais)
def post_lancamentosMensais(sender, instance, created, **kwargs):
    if instance.valor > 0:
        c = ContasaReceber.objects.filter(lancamentos_mensais=instance)

        if c.count() == 0:
            novoCR = ContasaReceber(associado=instance.matricula.associado,
                                    lancamentos_mensais=instance,
                                    tipo='s',
                                    valor=instance.valor,
                                    data_de_vencimento=instance.data_de_vencimento,
                                    data_de_recebimento=instance.data_de_recebimento,
                                    recebido=instance.recebido)
            novoCR.save()
        else:
            cr = ContasaReceber.objects.get(pk=c[0].pk)
            cr.valor = instance.valor
            cr.data_de_vencimento = instance.data_de_vencimento
            cr.data_de_recebimento = instance.data_de_recebimento
            cr.recebido = instance.recebido
            cr.save()
'''


def createDataAula(instance):
    dia_padrão_de_vencimento = 10

    data_vencimento = datetime.today().date()
    data_vencimento = data_vencimento.replace(day=dia_padrão_de_vencimento)

    datas = DataAula.objects.filter(turma=instance.turma)
    for data in datas:
        controlePresenca = ControlePresenca.objects.filter(associado=instance.associado, data_aula=data).count()
        contasaReceber = None
        if controlePresenca == 0 and data.data >= instance.data_de_matricula:
            consolidados = ContasaReceberConsolidado.objects.filter(associado=instance.associado, data_de_vencimento=data_vencimento, status='a')
            if consolidados.count() == 0:
                novoConsolidado = ContasaReceberConsolidado(associado=instance.associado,
                                                            status='a',
                                                            valor_cobrado=instance.turma.seminario.vl_hora_aula,
                                                            data_de_vencimento=data_vencimento,
                                                            recebido=False)
                novoConsolidado.save()
                consolidado = novoConsolidado
            else:
                consolidado = consolidados[0]
                contasaReceber = ContasaReceber.objects.filter(contas_areceber_consolidado=consolidado, tipo='s')
                if contasaReceber.count() > 0:
                    contasaReceber = contasaReceber[0]
                else:
                    contasaReceber = None

            if consolidados.count() == 0 or contasaReceber is None:
                lancamentosMensais = LancamentosMensais(matricula=instance,
                                                        qt_hora=1,
                                                        vl_hora_aula=instance.turma.seminario.vl_hora_aula,
                                                        valor=instance.turma.seminario.vl_hora_aula)
                lancamentosMensais.save()

                contasaReceber = ContasaReceber(associado=instance.associado,
                                                lancamentos_mensais=lancamentosMensais,
                                                contas_areceber_consolidado=consolidado,
                                                tipo='s',
                                                valor=instance.turma.seminario.vl_hora_aula,
                                                data_de_vencimento=data_vencimento)
                contasaReceber.save()

            controlePresenca = ControlePresenca(
                                                associado=instance.associado,
                                                data_aula=data,
                                                lancamentos_mensais=contasaReceber.lancamentos_mensais,
                                                presente=True
                                                )
            controlePresenca.save()

            totalPresenca = ControlePresenca.objects.filter(lancamentos_mensais=contasaReceber.lancamentos_mensais).count()
            LancamentosMensais.objects.filter(pk=contasaReceber.lancamentos_mensais.pk).update(
                qt_hora=totalPresenca,
                vl_hora_aula=instance.turma.seminario.vl_hora_aula,
                valor=instance.turma.seminario.vl_hora_aula*totalPresenca
            )

            ContasaReceber.objects.filter(pk=contasaReceber.pk).update(valor=instance.turma.seminario.vl_hora_aula*totalPresenca)
            soma = ContasaReceber.objects.filter(contas_areceber_consolidado=consolidado).aggregate(soma=Sum('valor'))
            ContasaReceberConsolidado.objects.filter(pk=consolidado.pk).update(valor_cobrado=soma['soma'])


@receiver(post_save, sender=DataAula)
def post_DataAula(sender, instance, created, **kwargs):
    if created:
        matriculas = Matricula.objects.filter(turma=instance.turma)

        for matricula in matriculas:
            createDataAula(matricula)


@receiver(post_save, sender=Matricula)
def post_MatriculaDataAula(sender, instance, created, **kwargs):
    if created:
        createDataAula(instance)


@receiver(post_save, sender=ContasaReceber)
def post_ContasaReceber(sender, instance, created, **kwargs):
        if created:
            data_vencimento = instance.data_de_vencimento
            if not instance.data_de_vencimento:
                dia_padrão_de_vencimento = 10
                data_vencimento = datetime.today().date() + relativedelta(months=+1)
                data_vencimento = data_vencimento.replace(day=dia_padrão_de_vencimento)
            consolidado = ContasaReceberConsolidado.objects.filter(associado=instance.associado, data_de_vencimento=data_vencimento)

            if consolidado.count() == 0:
                    novoConsolidado = ContasaReceberConsolidado(associado=instance.associado,
                                                                status='a',
                                                                valor_cobrado=instance.valor,
                                                                data_de_vencimento=data_vencimento,
                                                                recebido=False)
                    novoConsolidado.save()

                    ContasaReceber.objects.filter(pk=instance.pk).update(contas_areceber_consolidado=novoConsolidado)
            else:
                    ContasaReceber.objects.filter(pk=instance.pk).update(contas_areceber_consolidado=consolidado[0])
                    soma = ContasaReceber.objects.filter(contas_areceber_consolidado=consolidado[0]).aggregate(soma=Sum('valor'))
                    ContasaReceberConsolidado.objects.filter(pk=consolidado[0].pk).update(valor_cobrado=soma['soma'])
        else:
            soma = ContasaReceber.objects.filter(contas_areceber_consolidado=instance.contas_areceber_consolidado).aggregate(soma=Sum('valor'))
            ContasaReceberConsolidado.objects.filter(pk=instance.contas_areceber_consolidado.pk).update(
                    valor_cobrado=soma['soma'])


'''
@receiver(post_save, sender=Lancamentos)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        valor_parcela = instance.valor / instance.parcelas

        if (instance.parcelas == 1):

            for x in range(0, instance.parcelas):
                primeira_parcela = instance.data_de_matricula
                c = ContasaReceber(associado=instance.associado,
                                   titulo=instance,
                                   tipo='s',
                                   valor=valor_parcela,
                                   data_de_vencimento=primeira_parcela )
            c.save()

        else:

            for x in range(0, instance.parcelas):
               primeira_parcela = instance.data_de_matricula.replace(day=instance.dia_padrão_de_vencimento)
               c = ContasaReceber(associado=instance.associado,
                                  lancamentos=instance,
                                  tipo='s',
                                  valor=valor_parcela,
                                  data_de_vencimento=primeira_parcela + relativedelta(months=+x))
            c.save()
'''
