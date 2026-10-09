from io import BytesIO

from django.contrib import admin
from django.http import HttpResponse
from django.utils.html import format_html
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

from .models import Categoria, Equipo, Sede
from .views import _dibujar_etiqueta


@admin.register(Sede)
class SedeAdmin(admin.ModelAdmin):
    list_display = ("nombre", "direccion", "color_hex")
    search_fields = ("nombre",)


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nombre",)
    search_fields = ("nombre",)


@admin.action(description="Descargar etiquetas PDF de los equipos seleccionados")
def descargar_etiquetas_pdf(modeladmin, request, queryset):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=(100 * mm, 50 * mm))
    for i, equipo in enumerate(queryset):
        if i > 0:
            c.showPage()
            c.setPageSize((100 * mm, 50 * mm))
        _dibujar_etiqueta(c, equipo, request)
    c.save()
    buffer.seek(0)

    response = HttpResponse(buffer.getvalue(), content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="etiquetas.pdf"'
    return response


@admin.register(Equipo)
class EquipoAdmin(admin.ModelAdmin):
    list_display = (
        "nombre", "sede", "categoria", "tiene_notion", "estado", "fecha_registro", "ver_qr",
    )
    list_filter = ("sede", "categoria", "estado", "grupo_vigencia")
    search_fields = ("nombre", "numero_serie", "modelo")
    autocomplete_fields = ("sede", "categoria")
    readonly_fields = ("id", "fecha_registro", "vista_previa_qr", "enlace_etiqueta")
    actions = [descargar_etiquetas_pdf]

    fieldsets = (
        ("Información general", {
            "fields": ("nombre", "categoria", "sede", "ubicacion", "estado"),
        }),
        ("Notion", {
            "fields": ("notion_url",),
            "description": "Si pegas el link de Notion aquí, el QR de este equipo redirige "
                            "directo a esa página en vez de a la ficha interna.",
        }),
        ("Ficha técnica (PCs y laptops)", {
            "fields": ("modelo", "cpu", "ram_gb", "sistema_operativo", "numero_serie"),
        }),
        ("Clasificación del parque de PCs", {
            "fields": ("grupo_vigencia", "destino_sugerido"),
        }),
        ("Estaciones médicas", {
            "fields": ("software_asociado",),
        }),
        ("Identificación y QR", {
            "fields": ("id", "fecha_registro", "vista_previa_qr", "enlace_etiqueta"),
        }),
    )

    def tiene_notion(self, obj):
        return bool(obj.notion_url)

    tiene_notion.boolean = True
    tiene_notion.short_description = "Notion"

    def ver_qr(self, obj):
        return format_html('<a href="{}" target="_blank">Ver QR</a>', obj.get_url_qr_imagen())

    ver_qr.short_description = "QR"

    def vista_previa_qr(self, obj):
        if obj.pk:
            destino = obj.notion_url if obj.notion_url else "la página interna del sistema"
            return format_html(
                '<img src="{}" width="140" /><br><small>Este QR redirige a: {}</small>',
                obj.get_url_qr_imagen(), destino,
            )
        return "Se genera al guardar el equipo"

    vista_previa_qr.short_description = "Código QR"

    def enlace_etiqueta(self, obj):
        if obj.pk:
            return format_html(
                '<a href="{}" target="_blank">Ver etiqueta (HTML)</a> &nbsp;·&nbsp; '
                '<a href="{}">Descargar PDF 100x50mm ⬇</a>',
                obj.get_url_etiqueta(),
                "/equipo/%s/etiqueta.pdf" % obj.id,
            )
        return "Disponible al guardar el equipo"

    enlace_etiqueta.short_description = "Etiqueta para el sticker"

