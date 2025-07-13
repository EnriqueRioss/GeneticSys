from django import template

register = template.Library()

@register.filter(name='get_item')
def get_item(dictionary, key):
    """
    Permite acceder a un valor de un diccionario usando una variable como clave en las plantillas.
    Uso: {{ mi_diccionario|get_item:mi_variable_de_clave }}
    """
    return dictionary.get(key)