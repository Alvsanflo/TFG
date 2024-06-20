from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Jugador(models.Model):
    nombre = models.CharField(max_length=100)
    clubId = models.IntegerField(default=None)
    club = models.CharField(max_length=100)  
    posicion = models.CharField(max_length=100)
    posicion_especifica = models.CharField(max_length=100,null=True, blank=True)
    nacionalidad = models.CharField(max_length=100,null=True, blank=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    pie_bueno = models.CharField(max_length=12,null=True, blank=True) 
    valor_mercado_actual = models.DecimalField(max_digits=12, decimal_places=2,null=True, blank=True)
    valor_mercado_maximo = models.DecimalField(max_digits=12, decimal_places=2,null=True, blank=True) 
    ultimo_año = models.IntegerField(default=None)
    altura = models.CharField(max_length=100,null=True, blank=True)
    agente = models.CharField(max_length=100,null=True, blank=True)
    imagen = models.ImageField(upload_to='jugadores/', blank=True, null=True)

    def __str__(self):
        return self.nombre


class Club(models.Model):
    nombre = models.CharField(max_length=100)
    pais = models.CharField(max_length=100, blank=True, null=True)
    imagen_escudo = models.ImageField(upload_to='escudos/',null=True, blank=True)
    nombre_estadio = models.CharField(max_length=100, null=True, blank=True)
    edad_promedia_plantilla = models.DecimalField(max_digits=12, decimal_places = 2, null=True, blank=True)
    capacidad_estadio = models.PositiveIntegerField(default=None)
    tamaño_plantilla = models.IntegerField(default=None)

    def __str__(self):
        return self.nombre

class ValoresDeMercado(models.Model):
    jugador_id = models.IntegerField( blank=True, null=True)
    fecha = models.DateField( blank=True, null=True)
    valor_de_mercado = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    club_id = models.IntegerField( blank=True, null=True)
    pais = models.CharField(max_length=10, blank=True, null=True)
    nombre_jugador = models.CharField(max_length=100, blank=True, null=True)
    edad_jugador = models.IntegerField( blank=True, null=True)
    posicion_jugador = models.CharField(max_length=50, blank=True, null=True)
    posicion_especifica_jugador = models.CharField(max_length=50, blank=True, null=True)
    nacionalidad_jugador = models.CharField(max_length=100, blank=True, null=True)
    nombre_club = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.nombre_jugador} - {self.valor_de_mercado}"
    
class JuegoUsuario(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    partida_iniciada = models.DateField(null=True, blank=True)
    partida_completada = models.DateField(null=True, blank=True)
    
User.add_to_class('favoritos', models.JSONField(default=dict, blank=True))