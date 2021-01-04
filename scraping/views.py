from django.core.paginator import Paginator
from django.shortcuts import render

from .forms import SearchForm
from .models import Vacancy


def home_view(request):
    city = request.GET.get('city')
    language = request.GET.get('language')

    page_obj = None
    if city or language:
        _filters = {}
        if city:
            _filters['city__slug'] = city
        if language:
            _filters['language__slug'] = language
        query_set = Vacancy.objects.filter(**_filters)

        paginator = Paginator(query_set, 10)  # Show 10 contacts per page.
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

    context = {
        'city': city,
        'language': language,
        'object_list': page_obj,
        'form': SearchForm(),
    }
    return render(request, 'scraping/home.html', context)
