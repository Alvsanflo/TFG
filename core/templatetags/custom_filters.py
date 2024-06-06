from django import template

register = template.Library()

@register.filter
def format_valor_mercado(valor_mercado):
    """
    Formatea el valor de mercado agregando un punto cada tres dígitos.
    Si el valor termina con dos ceros, elimina el punto adicional al final.
    """
    # Convierte el valor a cadena y reversa para facilitar la inserción de puntos
    valor_str = str(valor_mercado)[::-1]
    
    # Inserta un punto cada tres dígitos
    formatted_valor = '.'.join([valor_str[i:i+3] for i in range(0, len(valor_str), 3)])
    
    # Revierte nuevamente para obtener el formato correcto
    formatted_valor = formatted_valor[::-1]
    
    # Elimina el punto adicional al final si el valor termina con dos ceros
    if formatted_valor.endswith(".00"):
        formatted_valor = formatted_valor[:-3]
    
    # Elimina el punto final si el valor es un número entero
    if formatted_valor.endswith("."):
        formatted_valor = formatted_valor[:-1]
    
    return formatted_valor 

@register.filter
def format_altura(altura):
    if altura is not None:
        try:
            altura_numerica = float(altura)
            altura_metros = altura_numerica / 100
            return "{:.2f}".format(altura_metros)
        except ValueError:
            return altura  # Devolver la cadena original si no se puede convertir a número
    else:
        return ""

@register.filter
def format_espectadores(numero):
    numero_str = str(numero)  # Convierte el número a una cadena
    partes = []
    while numero_str:
        partes.insert(0, numero_str[-3:])  # Agrega los últimos 3 dígitos al principio de la lista de partes
        numero_str = numero_str[:-3]  # Elimina los últimos 3 dígitos
    return '.'.join(partes)  # Une las partes con un punto como separador