from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from core.models import Jugador, Club, JuegoUsuario, ValoresDeMercado
from datetime import date, datetime
import json
import random
from django.utils.timezone import now

class HomeViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.url = reverse('home')
        self.user = User.objects.create_user(username='testuser', password='testpassword')

    def test_home_view_unauthenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/home.html')

    def test_home_view_authenticated(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/home.html')
        self.assertIn('jugadores_mas_valiosos', response.context)
        self.assertIn('mejores_clubes', response.context)
        self.assertIn('jugadores_juego', response.context)

class PlayerListViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.club = Club.objects.create(
            nombre='Club 1',
            pais='España',
            capacidad_estadio=50000,
            tamaño_plantilla=25
        )
        self.jugador1 = Jugador.objects.create(
            nombre='Jugador 1',
            clubId=self.club.id,
            club=self.club.nombre,
            posicion='Delantero',
            nacionalidad='España',
            valor_mercado_actual=100,
            ultimo_año=2023
        )
        self.jugador2 = Jugador.objects.create(
            nombre='Jugador 2',
            clubId=self.club.id,
            club=self.club.nombre,
            posicion='Defensa',
            nacionalidad='Argentina',
            valor_mercado_actual=50,
            ultimo_año=2023
        )

    def test_players_list_view(self):
        response = self.client.get(reverse('players_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/players_list.html')
        self.assertContains(response, self.jugador1.nombre)
        self.assertContains(response, self.jugador2.nombre)

    def test_player_list_search_by_nationality(self):
        response = self.client.get(reverse('players_list') + '?nacionalidad=España')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.jugador1.nombre)
        self.assertNotContains(response, self.jugador2.nombre)

    def test_player_list_search_by_position(self):
        response = self.client.get(reverse('players_list') + '?posicion=Defensa')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.jugador2.nombre)
        self.assertNotContains(response, self.jugador1.nombre)

class PlayerModelTest(TestCase):

    def setUp(self):
        self.club = Club.objects.create(
            nombre='Club 1',
            pais='España',
            capacidad_estadio=50000,
            tamaño_plantilla=25
        )
        self.jugador = Jugador.objects.create(
            nombre='Jugador 1',
            clubId=self.club.id,
            club=self.club.nombre,
            posicion='Delantero',
            nacionalidad='España',
            valor_mercado_actual=100,
            ultimo_año=2023
        )

    def test_jugador_creation(self):
        self.assertEqual(self.jugador.nombre, 'Jugador 1')
        self.assertEqual(self.jugador.club, 'Club 1')
        self.assertEqual(self.jugador.posicion, 'Delantero')

    def test_jugador_str(self):
        self.assertEqual(str(self.jugador), 'Jugador 1')

class ClubModelTest(TestCase):

    def setUp(self):
        self.club = Club.objects.create(
            nombre='Club 1',
            pais='España',
            capacidad_estadio=50000,
            tamaño_plantilla=25
        )

    def test_club_creation(self):
        self.assertEqual(self.club.nombre, 'Club 1')
        self.assertEqual(self.club.pais, 'España')

    def test_club_str(self):
        self.assertEqual(str(self.club), 'Club 1')

class PlayerDetailViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        # Crear un jugador con los campos necesarios
        self.jugador = Jugador.objects.create(
            nombre='Jugador 1',
            nacionalidad='España',
            posicion='Delantero',
            valor_mercado_actual=100,
            ultimo_año=2023  # Asignar un valor para último año
        )
        self.url = reverse('player_detail', args=[self.jugador.pk, 1])
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')

    def test_player_detail_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/player_detail.html')
        self.assertIn('jugador', response.context)
        self.assertEqual(response.context['jugador'].nombre, 'Jugador 1')
        self.assertIn('page_number', response.context)
        self.assertEqual(str(response.context['page_number']), '1')  # Convertir a cadena para la comparación
        self.assertIn('en_favoritos', response.context)
        self.assertFalse(response.context['en_favoritos'])  # Verificar que no esté en favoritos por defecto

    def tearDown(self):
        self.client.logout()


class ComprobarRespuestaViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        with open('preguntas_respuestasV2.json', 'w', encoding='utf-8') as file:
            json.dump({"Pregunta 1": "Respuesta 1"}, file)

    def test_comprobar_respuesta_correcta(self):
        response = self.client.post(reverse('comprobar_respuesta'), {'pregunta': 'Pregunta 1', 'respuesta': 'Respuesta 1'})
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'resultado': 'Correcto'})

    def test_comprobar_respuesta_incorrecta(self):
        response = self.client.post(reverse('comprobar_respuesta'), {'pregunta': 'Pregunta 1', 'respuesta': 'Respuesta Incorrecta'})
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'resultado': 'Incorrecto'})

    def test_comprobar_respuesta_missing_data(self):
        response = self.client.post(reverse('comprobar_respuesta'))
        self.assertEqual(response.status_code, 400)

class LoginAjaxViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.url = reverse('login_ajax')
        self.user = User.objects.create_user(username='testuser', password='testpassword')

    def test_login_ajax_view(self):
        response = self.client.post(self.url, {'username': 'testuser', 'password': 'testpassword'})
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'success': True, 'redirect_url': '/'})

    def test_login_ajax_view_invalid_credentials(self):
        response = self.client.post(self.url, {'username': 'testuser', 'password': 'wrongpassword'})
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'success': False, 'error_message': 'Nombre de usuario o contraseña incorrectos.'})

class RegisterAjaxViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.url = reverse('register_ajax')

    def test_register_ajax_view(self):
        response = self.client.post(self.url, {'username': 'newuser', 'password1': 'newpassword', 'password2': 'newpassword'})
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'success': True, 'redirect_url': '/'})

    def test_register_ajax_view_password_mismatch(self):
        response = self.client.post(self.url, {'username': 'newuser', 'password1': 'newpassword', 'password2': 'differentpassword'})
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'success': False, 'error_message': 'Las contraseñas no coinciden.'})


class AgregarFavoritoViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        # Creamos un jugador conforme al modelo Jugador
        self.jugador = Jugador.objects.create(
            nombre='Jugador 1', 
            nacionalidad='España', 
            posicion='Delantero', 
            valor_mercado_actual=100,
            ultimo_año=2023  # Añadimos un valor para el campo requerido ultimo_año
        )
        # Creamos un usuario de prueba
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        # Iniciamos sesión con el usuario de prueba
        self.client.login(username='testuser', password='testpassword')

    def test_agregar_favorito_view(self):
        # Realizamos una solicitud POST para agregar el jugador a favoritos
        response = self.client.post(reverse('agregar_favorito', args=[self.jugador.pk]))

        # Verificamos el código de estado de la respuesta
        self.assertEqual(response.status_code, 200)

        # Verificamos que la respuesta JSON indique éxito
        self.assertJSONEqual(response.content, {'success': True})

        # Actualizamos el usuario desde la base de datos para obtener los favoritos actualizados
        self.user.refresh_from_db()

        # Verificamos que el jugador se ha agregado a la lista de favoritos del usuario
        self.assertIn(str(self.jugador.pk), self.user.favoritos)

    def tearDown(self):
        # Cerramos sesión al finalizar la prueba para limpiar el estado de autenticación
        self.client.logout()

class ClubsListViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        # Crear clubs con todos los campos requeridos
        self.club1 = Club.objects.create(nombre='Club 1', pais='España', capacidad_estadio=50000, tamaño_plantilla=25)
        self.club2 = Club.objects.create(nombre='Club 2', pais='Argentina', capacidad_estadio=40000, tamaño_plantilla=30)

    def test_clubs_list_view(self):
        response = self.client.get(reverse('clubs_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/clubs_list.html')
        self.assertContains(response, self.club1.nombre)
        self.assertContains(response, self.club2.nombre)

    def test_clubs_list_filter_by_name(self):
        response = self.client.get(reverse('clubs_list'), {'q': 'Club 1'})
        self.assertContains(response, self.club1.nombre)
        self.assertNotContains(response, self.club2.nombre)

    def test_clubs_list_filter_by_pais(self):
        response = self.client.get(reverse('clubs_list'), {'pais': 'España'})
        self.assertContains(response, self.club1.nombre)
        self.assertNotContains(response, self.club2.nombre)

class ClubDetailViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.club = Club.objects.create(nombre='Club 1', pais='España', capacidad_estadio=50000, tamaño_plantilla=25)

    def test_club_detail_view(self):
        response = self.client.get(reverse('club_detail', args=[self.club.id, 1]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/club_detail.html')
        self.assertContains(response, self.club.nombre)

class FavoritosViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        # Crear un jugador con el campo 'ultimo_año' especificado
        self.jugador = Jugador.objects.create(
            nombre='Jugador 1',
            nacionalidad='España',
            posicion='Delantero',
            valor_mercado_actual=100,
            ultimo_año=2023  # Asegurar que 'ultimo_año' tenga un valor válido
        )
        # Agregar el jugador a la lista de favoritos del usuario
        self.user.favoritos[str(self.jugador.id)] = self.jugador.nombre
        self.user.save()
        self.client.login(username='testuser', password='testpassword')

    def test_favoritos_view(self):
        response = self.client.get(reverse('favoritos'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/favoritos.html')
        self.assertContains(response, self.jugador.nombre)

class JuegoUsuarioModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.juego_usuario = JuegoUsuario.objects.create(
            usuario=self.user,
            partida_iniciada=datetime.now(),
            partida_completada=None
        )

    def test_juego_usuario_creation(self):
        self.assertEqual(self.juego_usuario.usuario.username, 'testuser')
        self.assertIsNotNone(self.juego_usuario.partida_iniciada)
        self.assertIsNone(self.juego_usuario.partida_completada)