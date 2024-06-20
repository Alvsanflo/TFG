import json

def generar_preguntas_desde_json(json_file):
    # Cargar los datos del archivo JSON con codificación utf-8
    with open(json_file, 'r', encoding='utf-8') as file:
        valores_de_mercado = json.load(file)

    # Filtrar los valores de mercado excluyendo los clubes "Desconocido" y nacionalidades vacías
    valores_de_mercado_filtrados = []
    for item in valores_de_mercado:
        valor = item['fields']  # Acceder a los campos específicos
        try:
            if valor['nombre_club'] != "Desconocido" and valor['nacionalidad_jugador'] != "" and valor['pais'] in ["ES1", "GB1", "IT1", "FR1", "DE1"]:
                valores_de_mercado_filtrados.append(valor)
        except KeyError as e:
            print(f"Missing key: {e} in record {valor}")
            continue

    preguntas_respuestas = {}
    preguntas_set = set()  # Conjunto para rastrear preguntas únicas

    for valor in valores_de_mercado_filtrados:
        # Generar la pregunta
        pregunta = f"¿Qué jugador ha jugado en {valor['nombre_club']} de {valor['nacionalidad_jugador']}?"
        
        # Asegurarse de que la pregunta sea única
        if pregunta in preguntas_set:
            continue
        
        # Agregar la pregunta al conjunto
        preguntas_set.add(pregunta)
        
        # Filtrar los jugadores que han estado en el club y tienen la nacionalidad correspondiente
        jugadores = [
            item['nombre_jugador'] for item in valores_de_mercado_filtrados
            if item['nombre_club'] == valor['nombre_club'] and item['nacionalidad_jugador'] == valor['nacionalidad_jugador']
        ]
        
        # Usar solo nombres únicos de jugadores
        respuestas = list(set(jugadores))
        
        # Agregar la pregunta y sus respuestas al diccionario
        preguntas_respuestas[pregunta] = respuestas

    # Guardar el diccionario como un archivo JSON
    with open('preguntas_respuestasV2.json', 'w', encoding='utf-8') as file:
        json.dump(preguntas_respuestas, file, ensure_ascii=False, indent=4)

    return preguntas_respuestas

# Llamar a la función para generar el archivo JSON de preguntas y respuestas
json_file = 'valoresdemercado_nombres.json'
preguntas_respuestas = generar_preguntas_desde_json(json_file)
