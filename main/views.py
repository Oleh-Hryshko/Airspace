from django.shortcuts import render
from django.http import HttpResponse
from .base import convert, countries_list


def index(request):
    countries = countries_list()
    result = ''
    airspace_file = ''
    airspace_ccode = str(request.GET.get('airspace_ccode')).upper()
    if (request.GET.get('comand')):

        if airspace_ccode != 'NONE':
            airspace_file = convert(airspace_ccode)
            if airspace_file == '':
                result = 'Airspace not found'
        else:
            result = 'Airspace not specified'

    return render(
        request,
        'main/index.html',
        context={'countries': countries, 'airspace_ccode': airspace_ccode, 'result': result,
                 'airspace_file': airspace_file},
    )
