import json

# Cargar el JSON de datos_jugadores_temporada
with open('datos_jugadores_temporada.json', 'r', encoding='utf-8') as file:
    datos_jugadores_temporada = json.load(file)

# Cargar el JSON de estadisticas_por_temporada
with open('estadisticas_por_temporada.json', 'r', encoding='utf-8') as file:
    estadisticas_por_temporada = json.load(file)

# Fusionar los dos JSON
datos_completos = []

for jugador in datos_jugadores_temporada:
    jugador_id = jugador['fields']['jugador_id']
    temporada = jugador['fields']['temporada']
    
    # Verificar si hay una entrada correspondiente en estadisticas_por_temporada
    encontrado = False
    for estadistica in estadisticas_por_temporada:
        if estadistica['jugador_id'] == jugador_id and estadistica['temporada'] == temporada:
            jugador_completo = {
                "jugador_id": jugador_id,
                "temporada": temporada,
                "nombre_jugador": jugador['fields']['nombre_jugador'],
                "club_id": jugador['fields']['club_id'],
                "tarjetas_amarillas": estadistica['tarjetas_amarillas'],
                "tarjetas_rojas": estadistica['tarjetas_rojas'],
                "goles": estadistica['goles'],
                "asistencias": estadistica['asistencias'],
                "minutos_jugados": estadistica['minutos_jugados'],
                "valor_de_mercado": jugador['fields']['valor_de_mercado'],
                "fecha": jugador['fields']['fecha'],
                "pais": jugador['fields']['pais'],
                "edad_jugador": jugador['fields']['edad_jugador'],
                "posicion_jugador": jugador['fields']['posicion_jugador'],
                "posicion_especifica_jugador": jugador['fields']['posicion_especifica_jugador'],
                "nacionalidad_jugador": jugador['fields']['nacionalidad_jugador'],
                "nombre_club": jugador['fields']['nombre_club']
            }
            datos_completos.append(jugador_completo)
            encontrado = True
            break
    
    # Si no se encuentra una coincidencia, agregar una entrada con los campos vacíos
    if not encontrado:
        jugador_completo = {
            "jugador_id": jugador_id,
            "temporada": temporada,
            "nombre_jugador": jugador['fields']['nombre_jugador'],
            "club_id": jugador['fields']['club_id'],
            "tarjetas_amarillas": "",
            "tarjetas_rojas": "",
            "goles": "",
            "asistencias": "",
            "minutos_jugados": "",
            "valor_de_mercado": jugador['fields']['valor_de_mercado'],
            "fecha": jugador['fields']['fecha'],
            "pais": jugador['fields']['pais'],
            "edad_jugador": jugador['fields']['edad_jugador'],
            "posicion_jugador": jugador['fields']['posicion_jugador'],
            "posicion_especifica_jugador": jugador['fields']['posicion_especifica_jugador'],
            "nacionalidad_jugador": jugador['fields']['nacionalidad_jugador'],
            "nombre_club": jugador['fields']['nombre_club']
        }
        datos_completos.append(jugador_completo)

# Guardar el JSON fusionado
with open('datos_completos.json', 'w', encoding='utf-8') as file:
    json.dump(datos_completos, file, indent=4, ensure_ascii=False)
