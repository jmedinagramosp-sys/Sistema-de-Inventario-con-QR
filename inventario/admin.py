from django.contrib import admin
from django.utils.html import format_html

from .models import Categoria, Equipo, Sede


@admin.register(Sede)
class SedeAdmin(admin.ModelAdmin):
    list_display = ("nombre", "direccion", "color_hex")


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nombre",)


@admin.register(Equipo)
class EquipoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "sede", "categoria", "estado", "fecha_registro", "ver_qr")
    list_filter = ("sede", "categoria", "estado")
    search_fields = ("nombre",)
    readonly_fields = ("id", "fecha_registro", "vista_previa_qr")
    fields = (
        "nombre",
        "categoria",
        "sede",
        "ubicacion",
        "estado",
        "id",
        "fecha_registro",
        "vista_previa_qr",
    )

    def ver_qr(self, obj):
        return format_html('<a href="{}" target="_blank">Ver QR</a>', obj.get_url_qr_imagen())

    ver_qr.short_description = "QR"

    def vista_previa_qr(self, obj):
        if obj.pk:
            return format_html('<img src="{}" width="140" />', obj.get_url_qr_imagen())
        return "Se genera al guardar el equipo"

    vista_previa_qr.short_description = "Código QR"
