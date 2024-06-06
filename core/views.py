from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.staticfiles import finders
from core.models import *
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Q, Value, IntegerField
from django.db.models.functions import Coalesce


# Create your views here.
def home(request):
    jugadores = Jugador.objects.all()
    jugadores = jugadores.annotate(
        valor_mercado_actual_coalesce=Coalesce('valor_mercado_actual', Value(-1), output_field=IntegerField())
    )
    jugadores_mas_valiosos = jugadores.order_by('-valor_mercado_actual_coalesce')[:5]

    # Obtener los 5 clubes con el mayor valor total de jugadores
    mejores_clubes = Club.objects.filter(pk__in=[418, 27, 281, 46, 131])

    context = {
        'jugadores_mas_valiosos': jugadores_mas_valiosos,
        'mejores_clubes': mejores_clubes
    }

    return render(request, 'core/home.html', context)


def login_ajax(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False})

def logout_view(request):
    logout(request)
    return redirect('home')

def players_list(request, page=1):
    # Obtener todos los jugadores
    jugadores = Jugador.objects.all()

    # Obtener el parámetro de consulta de búsqueda por nombre (si existe)
    query_nombre = request.GET.get('q')

    # Obtener el parámetro de consulta de búsqueda por nacionalidad (si existe)
    query_nacionalidad = request.GET.get('nacionalidad')

    # Obtener el parámetro de consulta de búsqueda por posición (si existe)
    query_posicion = request.GET.get('posicion')

    # Filtrar los jugadores por nombre si se proporciona una búsqueda
    if query_nombre:
        jugadores = jugadores.filter(nombre__icontains=query_nombre)

    # Filtrar los jugadores por nacionalidad si se proporciona una búsqueda
    if query_nacionalidad:
        jugadores = jugadores.filter(nacionalidad=query_nacionalidad)

    # Filtrar los jugadores por posición si se proporciona una búsqueda
    if query_posicion:
        jugadores = jugadores.filter(posicion=query_posicion)

    # Obtener todas las nacionalidades de los jugadores para el dropdown
    nacionalidades = Jugador.objects.values_list('nacionalidad', flat=True).distinct()

    # Obtener todas las posiciones de los jugadores para el dropdown
    posiciones = Jugador.objects.values_list('posicion', flat=True).distinct()

    # Anotar el campo valor_mercado_actual con un valor por defecto para los campos nulos
    jugadores = jugadores.annotate(
        valor_mercado_actual_coalesce=Coalesce('valor_mercado_actual', Value(-1), output_field=IntegerField())
    )

    # Ordenar los jugadores por el campo valor_mercado_actual_coalesce
    jugadores = jugadores.order_by('-valor_mercado_actual_coalesce')

    # Configurar la paginación
    paginator = Paginator(jugadores, 10)  # Muestra 10 jugadores por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Pasar los datos paginados al contexto de la plantilla
    context = {
        'page_obj': page_obj,
        'nacionalidades': nacionalidades,
        'nacionalidad_seleccionada': query_nacionalidad,  # Pasar la nacionalidad seleccionada al contexto
        'posiciones': posiciones,
        'posicion_seleccionada': query_posicion  # Pasar la posición seleccionada al contexto
    }
    return render(request, 'core/players_list.html', context)

def player_detail(request, jugador_id, page_number):
    context = {}
    try:
        jugador = Jugador.objects.get(pk=jugador_id)
    except Jugador.DoesNotExist:
        raise Http404("El jugador no existe")
    
    context['jugador'] = jugador
    context['page_number'] = page_number

    valores_mercado = list(ValoresDeMercado.objects.filter(jugador_id=jugador_id).order_by('fecha').values())
    for valor in valores_mercado:
        valor['fecha'] = valor['fecha'].strftime('%Y-%m-%d')
        
    context['valores_mercado'] = json.dumps(valores_mercado, cls=DjangoJSONEncoder)
    posiciones_jugador= {
        'Mediocentro Ofensivo': {'top': 90, 'right': 177},
        'Delantero Centro': {'top': 45, 'right': 177},
        'Portero': {'top': 250, 'right': 177},
        'Extremo Izquierdo': {'top': 70, 'right': 237},
        'Extremo Derecho': {'top': 70, 'right': 115},
        'Lateral Derecho': {'top': 210, 'right': 115},
        'Lateral Izquierdo': {'top': 210, 'right': 237},
        'Mediocentro Defensivo': {'top': 180, 'right': 177},
        'Mediocentro': {'top': 145, 'right': 177},
        'Interior Derecho': {'top': 135, 'right': 127},
        'Interior Izquierdo': {'top': 135, 'right': 227},
        'Defensa Central': {'top': 215, 'right': 177},
        'Segundo Delantero': {'top': 70, 'right': 177},
    }
    context['posicion_jug'] = posiciones_jugador
        
    return render(request, 'core/player_detail.html', context)


def clubs_list(request, page = 1):
    clubes = Club.objects.all()
    context = {}
    

    # Obtener el parámetro de consulta de búsqueda por nombre (si existe)
    query_nombre = request.GET.get('q')

    # Obtener el parámetro de consulta de búsqueda por país (si existe)
    query_pais = request.GET.get('pais')

    # Filtrar los clubes por nombre si se proporciona una búsqueda
    if query_nombre:
        clubes = clubes.filter(nombre__icontains=query_nombre)

    # Filtrar los clubes por país si se proporciona un país
    if query_pais:
        clubes = clubes.filter(pais=query_pais)

    # Obtener todas las nacionalidades de los clubes para el dropdown
    paises = Club.objects.values_list('pais', flat=True).distinct()
    print(query_pais)

    paginator = Paginator(clubes, 10)  # Muestra 10 clubes por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    # Pasar los datos paginados al contexto de la plantilla
    context['page_obj'] = page_obj
    context['paises'] = paises
    context['pais_seleccionado'] = query_pais
    return render(request, 'core/clubs_list.html', context)


def club_detail(request,club_id,page_number):
    context={}
    club=Club.objects.get(pk=club_id)
    context['club']=club
    context['page_number']=page_number
    return render(request, 'core/club_detail.html',context)

