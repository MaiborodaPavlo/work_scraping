from django.contrib import messages
from django.contrib.auth import (
    authenticate,
    login,
    logout,
    get_user_model,
)
from django.shortcuts import render, redirect

from work_scraping.settings import RECAPTCHA_SITE_KEY
from .forms import (
    UserLoginForm,
    UserRegisterForm,
    UserUpdateForm,
    ContactForm,
)
from .tasks import send_contact_email
from .utils import check_recaptcha

User = get_user_model()


def login_view(request):
    form = UserLoginForm(request.POST or None)
    if form.is_valid():
        user = authenticate(request, email=form.cleaned_data['email'], password=form.cleaned_data['password'])
        login(request, user)
        return redirect('home')
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('home')


def register_view(request):
    form = UserRegisterForm(request.POST or None)
    if form.is_valid():
        new_user = form.save(commit=False)
        new_user.set_password(form.cleaned_data['password'])
        new_user.save()
        return render(request, 'accounts/register_done.html', {'new_user': new_user})
    return render(request, 'accounts/register.html', {'form': form})


def update_view(request):
    if not request.user.is_authenticated:
        return redirect('accounts:login')

    user = request.user
    if request.method == 'POST':
        form = UserUpdateForm(request.POST)
        if form.is_valid():
            user.city = form.cleaned_data['city']
            user.language = form.cleaned_data['language']
            user.is_subscribed = form.cleaned_data['is_subscribed']
            user.save()
            messages.success(request, 'User updated successfully.')
            return redirect('accounts:update')

    form = UserUpdateForm(
        initial={
            'city': user.city,
            'language': user.language,
            'is_subscribed': user.is_subscribed
        }
    )
    return render(request, 'accounts/update.html', {'form': form})


def delete_view(request):
    if request.user.is_authenticated:
        user = request.user
        if request.method == 'POST':
            _user = User.objects.get(pk=user.pk)
            _user.delete()
            messages.success(request, 'User deleted successfully.')
    return redirect('home')


@check_recaptcha
def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid() and request.recaptcha_is_valid:
            send_contact_email.delay(form.cleaned_data)
            messages.success(request, 'Your request has been sent.')
    form = ContactForm()
    return render(request, 'accounts/contact.html', {'recaptcha_site_key': RECAPTCHA_SITE_KEY, 'form': form})
