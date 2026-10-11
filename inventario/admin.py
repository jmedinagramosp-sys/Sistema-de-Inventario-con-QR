from io import BytesIO

from django.contrib import admin
from django.db.models import Count, Q
from django.http import HttpResponse
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

from .models import Categoria, Equipo, Sede
from .views import _dibujar_etiqueta

admin.site.site_header = "Gestión de Inventario de Equipos"
admin.site.site_title = "Inventario de Equipos"
admin.site.index_title = "Panel de administración"

_SVG = (
    '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" '
    'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">%s</svg>'
)
ICONO_QR = mark_safe(_SVG % (
    '<rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/>'
    '<rect x="3" y="14" width="7" height="7" rx="1"/><path d="M14 14h3v3h-3zM20 14v3M14 20h3M20 20h1"/>'
))
ICONO_LAPIZ = mark_safe(_SVG % (
    '<path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4Z"/>'
))
ICONO_BASURA = mark_safe(_SVG % (
    '<path d="M3 6h18"/><path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>'
    '<path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/>'
    '<line x1="10" y1="11" x2="10" y2="17"/><line x1="14" y1="11" x2="14" y2="17"/>'
))


def _kpis():
    """Totales para las tarjetas de resumen (panel principal y lista de equipos)."""
    return Equipo.objects.aggregate(
        total=Count("id"),
        operativos=Count("id", filter=Q(estado=Equipo.Estado.OPERATIVO)),
        revision=Count("id", filter=Q(estado=Equipo.Estado.REVISION)),
        baja=Count("id", filter=Q(estado=Equipo.Estado.BAJA)),
    )


def _datos_panel():
    """Datos que muestra el panel principal: tarjetas y equipos por sede."""
    sedes = list(Sede.objects.annotate(n=Count("equipos")).order_by("-n", "nombre"))
    maximo = max([sede.n for sede in sedes], default=0)
    por_sede = [
        {
            "nombre": sede.nombre,
            "total": sede.n,
            "porcentaje": round(sede.n * 100 / maximo) if maximo else 0,
        }
        for sede in sedes
    ]
    return {"kpis": _kpis(), "por_sede": por_sede}


# Se agregan esos datos a la página de inicio del admin
_index_original = admin.site.index


def _index_con_datos(request, extra_context=None):
    extra_context = {**(extra_context or {}), **_datos_panel()}
    return _index_original(request, extra_context)


admin.site.index = _index_con_datos


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
        "nombre", "sede", "categoria", "tiene_notion", "estado",
        "fecha_registro", "ver_qr", "acciones",
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

    def changelist_view(self, request, extra_context=None):
        """Agrega los totales que se muestran en las tarjetas de arriba de la lista."""
        extra_context = extra_context or {}
        extra_context["kpis"] = _kpis()
        return super().changelist_view(request, extra_context=extra_context)

    def tiene_notion(self, obj):
        return bool(obj.notion_url)

    tiene_notion.boolean = True
    tiene_notion.short_description = "Notion"

    def ver_qr(self, obj):
        return format_html(
            '<a class="icono-accion" href="{}" target="_blank" title="Ver QR">{}</a>',
            obj.get_url_qr_imagen(), ICONO_QR,
        )

    ver_qr.short_description = "QR"

    def acciones(self, obj):
        editar = reverse("admin:inventario_equipo_change", args=[obj.pk])
        borrar = reverse("admin:inventario_equipo_delete", args=[obj.pk])
        return format_html(
            '<a class="icono-accion" href="{}" title="Editar">{}</a>'
            '<a class="icono-accion icono-borrar" href="{}" title="Eliminar">{}</a>',
            editar, ICONO_LAPIZ, borrar, ICONO_BASURA,
        )

    acciones.short_description = ""

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

