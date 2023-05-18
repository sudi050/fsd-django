from django import forms
from .models import pred_images 

class UserForm(forms.ModelForm):
    class Meta:
        model = pred_images 
        fields = ['photo']