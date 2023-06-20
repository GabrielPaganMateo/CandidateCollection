from django.forms import ModelForm
from django import forms
from .models import Opening, Candidate
from .utils import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class OpeningForm(ModelForm):
    class Meta:
        model = Opening
        fields = ['name']
    
    def __init__(self, *args, **kwargs):
        super(OpeningForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'placeholder': 'Enter Job Title'})

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result


class CandidateForm(forms.Form):
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['opening'] = forms.ModelChoiceField(
            queryset=Opening.objects.filter(user=user), 
            empty_label="Select Job Opening"
        )
    resumes = MultipleFileField()

class SearchForm(forms.Form):
    EDUCATION_CHOICES = [
    ('', 'All education levels'),
    ('None', 'None'),
    ('Certificate', 'Certificate'),
    ('Associate\'s', 'Associate\'s'),
    ('Bachelor\'s', 'Bachelor\'s'),
    ('Master\'s', 'Master\'s'),
    ('Doctor', 'Doctor'),
    ]

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['opening'] = forms.ModelChoiceField(
            queryset=Opening.objects.filter(user=user),
            empty_label="All Candidates",
            required=False
        )
    query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Filter By Keyword'}),
        label=''
    )
    education = forms.ChoiceField(choices=EDUCATION_CHOICES, required=False)

class RegisterUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super(RegisterUserForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['placeholder'] = 'Enter Username'
        self.fields['email'].widget.attrs['placeholder'] = 'Enter Email'
        self.fields['password1'].widget.attrs['placeholder'] = 'Enter Password'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm Password'