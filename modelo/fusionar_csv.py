import json

def fusionar_json(lista_json1, lista_json2):
    # Convertir las listas de JSON a un solo diccionario usando "pk" como clave
    dict_json1 = {item["pk"]: item for item in lista_json1}
    dict_json2 = {item["pk"]: item for item in lista_json2}

    # Fusionar los campos de los segundos JSON en los primeros
    for pk, json2 in dict_json2.items():
        if pk in dict_json1:
            dict_json1[pk]["fields"].update(json2["fields"])
        else:
            dict_json1[pk] = json2

    # Convertir el diccionario de JSON fusionados nuevamente a una lista
    lista_json_fusionados = list(dict_json1.values())

    return lista_json_fusionados

# Cargar las listas de JSON originales desde archivos
with open('jugadores.json', 'r', encoding='utf-8') as file:
    datos1 = json.load(file)

with open('jugadoresCLUBID.json', 'r', encoding='utf-8') as file:
    datos2 = json.load(file)

# Fusionar las listas de JSON
datos_fusionados = fusionar_json(datos1, datos2)

# Guardar la lista de JSON fusionados en un nuevo archivo
with open('jugadoresDefinitivo.json', 'w', encoding='utf-8') as file:
    json.dump(datos_fusionados, file, indent=4,ensure_ascii=False)
