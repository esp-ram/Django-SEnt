from django import forms
from django.forms import BaseFormSet
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from crispy_forms.layout import Layout, Submit


class EntregaForm(forms.Form):
    name = forms.CharField(min_length=1)
    student_id = forms.IntegerField(min_value=1)

class MyEntregaForm(EntregaForm):
    def __init__(self, *args, exercises, **kwargs):
        self.exercises = exercises
        super().__init__(*args, **kwargs)


class BaseEntregaFormSet(BaseFormSet):
    def add_fields(self, form, index):
        super().add_fields(form, index)
        for i in range(form.exercises):
            form.fields[f'ex {i}'] = forms.FileField()
            form.fields[f'ex {i}'].required = False


class EntregaFormSetHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form_method = 'post'
        self.layout = Layout(
            'name',
            'student_id',
        )
        self.render_required_fields = True
        self.render_hidden_fields = True
        self.form_class = 'form-horizontal'
        self.label_class = 'col-lg-2'
        self.field_class = 'col-lg-8'
        self.add_input(Submit("submit", "Submit"))
