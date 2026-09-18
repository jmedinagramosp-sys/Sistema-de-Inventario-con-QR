from django import template
from django.contrib.admin.models import ADDITION, CHANGE, DELETION

register = template.Library()


@register.filter
def accion_verbo(action_flag):
    return {
        ADDITION: "ha añadido",
        CHANGE: "ha editado",
        DELETION: "ha eliminado",
    }.get(action_flag, "ha modificado")


@register.filter
def accion_clase(action_flag):
    return {
        ADDITION: "add",
        CHANGE: "change",
        DELETION: "delete",
    }.get(action_flag, "change")


@register.filter
def accion_icono(action_flag):
    return {
        ADDITION: "+",
        CHANGE: "✎",
        DELETION: "–",
    }.get(action_flag, "•")