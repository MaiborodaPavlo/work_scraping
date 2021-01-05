from django import forms
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.hashers import check_password

from scraping.models import City, Language

User = get_user_model()


class UserLoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        if email and password:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                raise forms.ValidationError('Invalid email or password.')
            if not check_password(password, user.password):
                raise forms.ValidationError('Invalid email or password.')
            if not authenticate(email=email, password=password):
                raise forms.ValidationError('User is inactive.')
        return super().clean()


class UserRegisterForm(forms.ModelForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    password2 = forms.CharField(
        label='Repeat password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ('email', )

    def clean_password2(self):
        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')
        if password != password2:
            raise forms.ValidationError('Passwords do not match.')
        return password2


class UserUpdateForm(forms.ModelForm):
    city = forms.ModelChoiceField(
        queryset=City.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    language = forms.ModelChoiceField(
        queryset=Language.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    is_subscribed = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(),
        label='Get emails?',
    )

    class Meta:
        model = User
        fields = ('city', 'language', 'is_subscribed')
