from django.forms import (
    Form,
    ModelChoiceField,
    Select,
)

from .models import City, Language


class SearchForm(Form):
    city = ModelChoiceField(
        queryset=City.objects.all(),
        to_field_name='slug',
        required=False,
        widget=Select(attrs={'class': 'form-control'}),
    )
    language = ModelChoiceField(
        queryset=Language.objects.all(),
        to_field_name='slug',
        required=False,
        widget=Select(attrs={'class': 'form-control'}),
    )
