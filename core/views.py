from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, Http404
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
import random
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from datetime import date
from django.utils.timezone import now

# Create your views here.

def home(request):
    context = {}

    if request.user.is_authenticated:
        # Obtener o crear el objeto JuegoUsuario asociado al usuario actual
        juego_usuario, created = JuegoUsuario.objects.get_or_create(usuario=request.user)

        # Verificar si hay partida iniciada hoy
        if juego_usuario.partida_iniciada == now().date():
            # Partida iniciada hoy
            if juego_usuario.partida_completada == now().date():
                # Partida completada hoy
                context['mensaje_finalizacion'] = "¡Felicidades, has respondido todas las preguntas correctamente!. Vuelve mañana para jugar de nuevo."
            else:
                # Partida iniciada pero no completada
                context['mostrar_descripcion_iniciar'] = False

                if 'preguntas_juego' in request.session:
                    preguntas_juego = request.session['preguntas_juego']
                    pregunta_actual = request.session.get('pregunta_actual', 0)

                    if pregunta_actual >= len(preguntas_juego):
                        # Todas las preguntas han sido respondidas correctamente
                        context['mensaje_finalizacion'] = "¡Felicidades, has respondido todas las preguntas correctamente!"
                        juego_usuario.partida_completada = now().date()
                        juego_usuario.save()
                    else:
                        pregunta_actual_texto, respuestas_correctas = preguntas_juego[pregunta_actual]
                        context['pregunta_actual'] = pregunta_actual_texto

                        if request.method == 'POST':
                            respuesta_usuario = request.POST.get('respuesta', '').strip().lower()
                            respuestas_correctas = [respuesta.strip().lower() for respuesta in respuestas_correctas]

                            if respuesta_usuario in respuestas_correctas:
                                request.session['pregunta_actual'] += 1
                                pregunta_actual += 1
                                if pregunta_actual >= len(preguntas_juego):
                                    # Se han respondido todas las preguntas correctamente
                                    context['mensaje_finalizacion'] = "¡Felicidades, has respondido todas las preguntas correctamente!"
                                    juego_usuario.partida_completada = now().date()
                                    juego_usuario.save()
                                else:
                                    pregunta_actual_texto, respuestas_correctas = preguntas_juego[pregunta_actual]
                                    context['pregunta_actual'] = pregunta_actual_texto
                            else:
                                context['mensaje_error'] = "Respuesta incorrecta. Inténtalo de nuevo."

                else:
                    # Si no hay preguntas en la sesión, cargarlas y comenzar desde la primera pregunta
                    with open('preguntas_respuestasV2.json', 'r', encoding='utf-8') as file:
                        preguntas = json.load(file)
                    preguntas_seleccionadas = random.sample(list(preguntas.items()), 8)

                    request.session['preguntas_juego'] = preguntas_seleccionadas
                    request.session['pregunta_actual'] = 0
                    pregunta_actual_texto, respuestas_correctas = preguntas_seleccionadas[0]
                    context['pregunta_actual'] = pregunta_actual_texto

        else:
            # No hay partida iniciada hoy
            context['mostrar_descripcion_iniciar'] = True

            # Limpiar sesión de preguntas si se inicia nueva partida
            if 'preguntas_juego' in request.session:
                del request.session['preguntas_juego']
                del request.session['pregunta_actual']

    # Obtener los jugadores más valiosos y los mejores clubes
    jugadores = Jugador.objects.all()
    jugadores = jugadores.annotate(
        valor_mercado_actual_coalesce=Coalesce('valor_mercado_actual', Value(-1), output_field=IntegerField())
    )
    jugadores_mas_valiosos = jugadores.order_by('-valor_mercado_actual_coalesce')[:5]

    mejores_clubes = Club.objects.filter(pk__in=[418, 27, 281, 46, 131])
    jugadores_juego = Jugador.objects.values_list('nombre', flat=True).distinct()
    context.update({
        'jugadores_mas_valiosos': jugadores_mas_valiosos,
        'mejores_clubes': mejores_clubes,
        'jugadores_juego': jugadores_juego,
        'today': date.today()
    })

    # Renderizar la página home.html con el contexto adecuado
    return render(request, 'core/home.html', context)
@login_required
def iniciar_partida(request):
    # Obtener el usuario actual que está autenticado
    usuario_actual = request.user

    try:
        # Obtener o crear el objeto JuegoUsuario asociado al usuario actual
        juego_usuario, created = JuegoUsuario.objects.get_or_create(usuario=usuario_actual)

        # Guardar la fecha de hoy como partida iniciada
        juego_usuario.partida_iniciada = date.today()
        juego_usuario.save()

        # Añadir datos necesarios al context para mostrar el minijuego
        context = {
            'juego_usuario': juego_usuario,
            # Añadir más datos si son necesarios para el minijuego
        }

        # Renderizar la plantilla del minijuego con el contexto
        return render(request, 'home', context)

    except Exception as e:
        # Manejar cualquier excepción que pueda ocurrir durante el proceso
        print(f"Error al iniciar la partida: {e}")
        # Puedes redirigir a una página de error o simplemente a la página home
        return redirect('home')

def comprobar_respuesta(request):
    if request.method == 'POST':
        # Obtener la pregunta y la respuesta del usuario desde la solicitud POST
        pregunta = request.POST.get('pregunta')
        respuesta_usuario = request.POST.get('respuesta')
        print(pregunta)
        print(respuesta_usuario)

        if not pregunta or not respuesta_usuario:
            return JsonResponse({'error': 'Datos de pregunta o respuesta no proporcionados'}, status=400)

        # Cargar las preguntas y respuestas desde el archivo JSON
        with open('preguntas_respuestasV2.json', 'r', encoding='utf-8') as file:
            preguntas_respuestas = json.load(file)

        # Obtener la respuesta correcta del diccionario y convertirla a minúsculas si existe
        respuesta_correcta = preguntas_respuestas.get(pregunta, '').lower()

        # Convertir la respuesta del usuario a minúsculas para compararla
        respuesta_usuario = respuesta_usuario.lower()

        # Comprobar si la respuesta del usuario es correcta
        if respuesta_usuario == respuesta_correcta:
            resultado = 'Correcto'
        else:
            resultado = 'Incorrecto'

        # Devolver el resultado como una respuesta JSON
        return JsonResponse({'resultado': resultado})
    else:
        # Devolver un error si la solicitud no es POST
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
def login_ajax(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({'success': True, 'redirect_url': '/'})  # Redirigir a la página 'home'
        else:
            return JsonResponse({'success': False, 'error_message': 'Nombre de usuario o contraseña incorrectos.'})

    return JsonResponse({'success': False, 'error_message': 'Método no permitido.'})

def logout_view(request):
    logout(request)
    return redirect('home')

def register_ajax(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            return JsonResponse({'success': False, 'error_message': 'Las contraseñas no coinciden.'})
        
        # Crear el usuario
        try:
            user = User.objects.create_user(username=username, password=password1)
        except:
            return JsonResponse({'success': False, 'error_message': 'Error al crear el usuario.'})
        
        # Iniciar sesión después del registro
        login(request, user)

        return JsonResponse({'success': True, 'redirect_url': '/'})  # Redirigir al inicio

    return JsonResponse({'success': False, 'error_message': 'Método no permitido.'})

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

    usuario = request.user  # Obtener el usuario autenticado

    en_favoritos = False
    if request.user.is_authenticated:
        usuario = request.user
        en_favoritos = jugador_id in usuario.favoritos
    context['en_favoritos'] = en_favoritos

    valores_mercado = list(ValoresDeMercado.objects.filter(jugador_id=jugador_id).order_by('fecha').values())
    for valor in valores_mercado:
        valor['fecha'] = valor['fecha'].strftime('%Y-%m-%d')
        
    context['valores_mercado'] = json.dumps(valores_mercado, cls=DjangoJSONEncoder)
    posiciones_jugador = {
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

@login_required
def agregar_favorito(request, jugador_id):
    jugador = get_object_or_404(Jugador, id=jugador_id)
    user = request.user

    # Asegurarse de que el jugador no esté ya en la lista de favoritos
    if str(jugador.id) not in user.favoritos:
        user.favoritos[str(jugador.id)] = jugador.nombre
        user.save()
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False})

@login_required
def eliminar_favorito(request, jugador_id):
    jugador = get_object_or_404(Jugador, id=jugador_id)
    user = request.user

    # Asegurarse de que el jugador esté en la lista de favoritos antes de eliminar
    if str(jugador.id) in user.favoritos:
        del user.favoritos[str(jugador.id)]
        user.save()
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False})

@login_required
def lista_favoritos(request):
    usuario = request.user  # Obtener el usuario autenticado

    favoritos = usuario.favoritos

    context = {
        'favoritos': favoritos
    }

    return render(request, 'tu_template.html', context)
