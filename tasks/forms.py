from django.forms import ModelForm
from .models import Task

class TaskForm(ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'important']

# forms.py

from django import forms
from .models import Pregunta

class PreguntaForm(forms.ModelForm):
    class Meta:
        model = Pregunta
        fields = ['titulo', 'contenido']
        widgets = {
            'contenido': forms.Textarea(attrs={'rows': 4, 'cols': 40}),
        }
