from io import BytesIO

import qrcode
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from .models import Equipo


def equipo_publico(request, equipo_id):
    """La página web interna: sigue existiendo como respaldo para equipos sin link de Notion."""
    equipo = get_object_or_404(Equipo, pk=equipo_id)
    return render(request, "inventario/publico.html", {"equipo": equipo})


def equipo_etiqueta(request, equipo_id):
    """Vista HTML pensada para imprimirse junto al QR en el sticker físico."""
    equipo = get_object_or_404(Equipo, pk=equipo_id)
    return render(request, "inventario/etiqueta.html", {"equipo": equipo})


def _url_destino(equipo, request):
    """A dónde debe apuntar el QR: Notion si hay link, si no, la página interna."""
    if equipo.notion_url:
        return equipo.notion_url
    return request.build_absolute_uri(equipo.get_url_publica())


def _generar_imagen_qr(url):
    qr = qrcode.QRCode(box_size=8, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer


def _dibujar_etiqueta(c, equipo, request):
    """Dibuja una etiqueta de 100x50mm en la posición actual del canvas."""
    ANCHO, ALTO = 100 * mm, 50 * mm

    c.setLineWidth(0.5)
    c.rect(0, 0, ANCHO, ALTO)

    # Encabezado
    c.setFont("Helvetica-Bold", 13)
    c.drawString(4 * mm, ALTO - 8 * mm, "S&M")

    # Datos básicos, a la izquierda
    c.setFont("Helvetica-Bold", 9)
    c.drawString(4 * mm, ALTO - 16 * mm, "P.C:")
    c.setFont("Helvetica", 9)
    codigo = equipo.numero_serie if equipo.numero_serie else equipo.nombre
    c.drawString(14 * mm, ALTO - 16 * mm, codigo[:22])

    c.setFont("Helvetica-Bold", 9)
    c.drawString(4 * mm, ALTO - 23 * mm, "S.O:")
    c.setFont("Helvetica", 9)
    c.drawString(14 * mm, ALTO - 23 * mm, (equipo.sistema_operativo or "-")[:22])

    c.setFont("Helvetica-Bold", 9)
    c.drawString(4 * mm, ALTO - 30 * mm, "Sede:")
    c.setFont("Helvetica", 9)
    c.drawString(16 * mm, ALTO - 30 * mm, equipo.sede.nombre[:20])

    # QR, a la derecha
    qr_buffer = _generar_imagen_qr(_url_destino(equipo, request))
    qr_img = ImageReader(qr_buffer)
    lado = 30 * mm
    c.drawImage(qr_img, ANCHO - lado - 4 * mm, (ALTO - lado) / 2, lado, lado)


def equipo_etiqueta_pdf(request, equipo_id):
    """Descarga la etiqueta de un solo equipo como PDF de 100x50mm exactos."""
    equipo = get_object_or_404(Equipo, pk=equipo_id)

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=(100 * mm, 50 * mm))
    _dibujar_etiqueta(c, equipo, request)
    c.save()
    buffer.seek(0)

    nombre_archivo = f"etiqueta_{equipo.numero_serie or equipo.id}.pdf"
    response = HttpResponse(buffer.getvalue(), content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{nombre_archivo}"'
    return response


def equipo_qr_imagen(request, equipo_id):
    """Genera la imagen QR en memoria. Si el equipo tiene un link de Notion cargado,
    el QR apunta directo ahí; si no, apunta a la página pública interna.
    """
    equipo = get_object_or_404(Equipo, pk=equipo_id)
    buffer = _generar_imagen_qr(_url_destino(equipo, request))
    return HttpResponse(buffer.getvalue(), content_type="image/png")