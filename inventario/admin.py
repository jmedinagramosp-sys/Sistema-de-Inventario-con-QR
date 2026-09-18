from django.contrib import admin
from django.utils.html import format_html

from .models import Categoria, Equipo, Sede

admin.site.site_header = "Inventario Clínico"
admin.site.site_title = "Inventario Clínico"
admin.site.index_title = "Panel de administración"
@admin.register(Sede)
class SedeAdmin(admin.ModelAdmin):
    list_display = ("nombre", "direccion", "color_hex")
    search_fields = ("nombre",)  # necesario para que funcione autocomplete_fields


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nombre",)
    search_fields = ("nombre",)  # necesario para que funcione autocomplete_fields


@admin.register(Equipo)
class EquipoAdmin(admin.ModelAdmin):
    list_display = (
        "nombre", "sede", "categoria", "grupo_vigencia", "estado", "fecha_registro", "ver_qr",
    )
    list_filter = ("sede", "categoria", "estado", "grupo_vigencia")
    search_fields = ("nombre", "numero_serie", "modelo")
    autocomplete_fields = ("sede", "categoria")
    readonly_fields = ("id", "fecha_registro", "vista_previa_qr", "enlace_etiqueta")

    fieldsets = (
        ("Información general", {
            "fields": ("nombre", "categoria", "sede", "ubicacion", "estado"),
        }),
        ("Ficha técnica (PCs y laptops)", {
            "fields": ("modelo", "cpu", "ram_gb", "sistema_operativo", "numero_serie"),
        }),
        ("Clasificación del parque de PCs", {
            "fields": ("grupo_vigencia", "destino_sugerido"),
            "description": "Deja \"Destino sugerido\" en blanco para que se autocomplete "
                            "según el grupo elegido, o escribe uno distinto si el caso lo amerita.",
        }),
        ("Estaciones médicas", {
            "fields": ("software_asociado",),
            "description": "Ej. Consola CareRay + PACS dicomPACS, MIR Spiro, EDAN SE-3, etc.",
        }),
        ("Identificación y QR", {
            "fields": ("id", "fecha_registro", "vista_previa_qr", "enlace_etiqueta"),
        }),
    )

    def ver_qr(self, obj):
        return format_html('<a href="{}" target="_blank">Ver QR</a>', obj.get_url_qr_imagen())

    ver_qr.short_description = "QR"

    def vista_previa_qr(self, obj):
        if obj.pk:
            return format_html('<img src="{}" width="140" />', obj.get_url_qr_imagen())
        return "Se genera al guardar el equipo"

    vista_previa_qr.short_description = "Código QR"

    def enlace_etiqueta(self, obj):
        if obj.pk:
            return format_html(
                '<a href="{}" target="_blank">Abrir etiqueta imprimible →</a>',
                obj.get_url_etiqueta(),
            )
        return "Disponible al guardar el equipo"

    enlace_etiqueta.short_description = "Etiqueta para el sticker"