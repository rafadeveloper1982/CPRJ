from django import forms
from .models import LancamentosMensais, Matricula


class LancamentosMensaisForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        # instance = kwargs.get('instance')

        # print('insxxxxx', instance)

        # if instance:
        #    print(instance.matricula.turma.seminario.vl_hora_aula)
        #    vl_hora_aula = kwargs['instance'].vl_hora_aula
        #    kwargs.setdefault('initial', {})['confirm_email'] = vl_hora_aula

        super(LancamentosMensaisForm, self).__init__(*args, **kwargs)
        # print(self)
        self.fields['qt_hora'].widget.attrs['class'] = 'qtdHora'
        self.fields['qt_hora'].widget.attrs['style'] = 'width:80px;'

    class Meta:
        model = LancamentosMensais
        fields = ['qt_hora',  'vl_hora_aula', 'valor', 'recebido']


class MantriculaForm(forms.ModelForm):
    valor_aula = forms.FloatField()

    def __init__(self, *args, **kwargs):
        super(MantriculaForm, self).__init__(*args, **kwargs)
        self.fields['valor_aula'].widget.attrs['class'] = 'valor_aula inputDisable'
        self.fields['valor_aula'].widget.attrs['style'] = 'width:80px;'
        self.fields['valor_aula'].widget.attrs['name'] = 'valor_aula'
        self.fields['valor_aula'].widget.attrs['readonly'] = True

    class Meta:
        model = Matricula
        fields = ['associado', 'turma', 'data_de_matricula', 'data_de_conclusao', 'valor_aula']
