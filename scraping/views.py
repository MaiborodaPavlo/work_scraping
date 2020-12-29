from django.shortcuts import render

from .forms import SearchForm
from .models import Vacancy


def home_view(request):
    city = request.GET.get('city')
    language = request.GET.get('language')

    query_set = []
    if city or language:
        _filters = {}
        if city:
            _filters['city__slug'] = city
        if language:
            _filters['language__slug'] = language
        query_set = Vacancy.objects.filter(**_filters)

    context = {
        'object_list': query_set,
        'form': SearchForm(),
    }
    return render(request, 'scraping/home.html', context)
