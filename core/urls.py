from django.urls import path
from . import views
from django.urls import path, include
from core.views import *

urlpatterns = [
    path('', home, name='home'),
    path('logout/',logout_view, name = 'logout'),
    path('players_list/', players_list, name ='players_list'),
    path('players_list/', players_list, name ='players_list_paginated'),
    path('player_detail/<int:jugador_id>/<int:page_number>/', player_detail, name='player_detail'),
    path('clubs_list/', clubs_list, name = 'clubs_list'),
    path('clubs_list/', clubs_list, name ='clubs_list_paginated'),
    path('club_detail/<int:club_id>/<int:page_number>/', club_detail, name='club_detail'),
    path('login_ajax/', login_ajax, name='login_ajax'),
    path('comprobar_respuesta/', comprobar_respuesta, name='comprobar_respuesta'),
    path('iniciar_partida/', iniciar_partida, name='iniciar_partida'),
    path('register_ajax/', register_ajax, name='register_ajax'),
    path('agregar_favorito/<int:jugador_id>/', agregar_favorito, name='agregar_favorito'),
    path('eliminar_favorito/<int:jugador_id>/', eliminar_favorito, name='eliminar_favorito'),
    path('favoritos/', favoritos, name='favoritos'),
]
