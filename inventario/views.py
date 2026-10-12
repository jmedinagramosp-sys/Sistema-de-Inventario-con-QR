from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

from . import etiquetas
from .models import Equipo


def equipo_publico(request, equipo_id):
    """Ficha que se abre al escanear el QR. Es pública: la plantilla solo muestra los
    datos de identificación; la parte técnica se muestra únicamente al personal con sesión."""
    equipo = get_object_or_404(Equipo.objects.select_related("sede", "categoria"), pk=equipo_id)
    return render(request, "inventario/publico.html", {"equipo": equipo})


def equipo_qr_imagen(request, equipo_id):
    """Imagen del QR. Solo contiene una URL, no datos del equipo, por eso es pública."""
    equipo = get_object_or_404(Equipo, pk=equipo_id)
    url = etiquetas.url_destino(equipo, etiquetas.url_base_del_sitio(request))
    return HttpResponse(etiquetas.generar_qr_png(url), content_type="image/png")


@staff_member_required
def equipo_etiqueta(request, equipo_id):
    """Vista HTML de la etiqueta (incluye serie y S.O.): solo para el personal."""
    equipo = get_object_or_404(Equipo.objects.select_related("sede"), pk=equipo_id)
    return render(request, "inventario/etiqueta.html", {"equipo": equipo})


@staff_member_required
def equipo_etiqueta_pdf(request, equipo_id):
    """Etiqueta de un equipo en PDF de 100x50 mm."""
    equipo = get_object_or_404(Equipo.objects.select_related("sede"), pk=equipo_id)
    pdf = etiquetas.generar_pdf_etiquetas([equipo], etiquetas.url_base_del_sitio(request))
    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="etiqueta_{equipo.numero_serie or equipo.id}.pdf"'
    return response
