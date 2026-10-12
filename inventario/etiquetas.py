"""Generación de QR y etiquetas PDF (100x50 mm).

Este módulo no conoce vistas ni el admin: recibe un equipo y una URL base y devuelve
bytes. Así vista web y acción masiva del admin comparten exactamente el mismo código.
"""
from io import BytesIO

import qrcode
from django.conf import settings
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

ANCHO, ALTO = 100 * mm, 50 * mm


def url_base_del_sitio(request):
    """Dominio que se graba dentro de los QR.

    Se lee de SITE_URL (variable de entorno) y no del request a propósito: los stickers
    impresos viven años, y si el sistema cambia de hosting el dominio del QR debe ser una
    decisión explícita, no un efecto de desde dónde se descargó el PDF.
    """
    if settings.SITE_URL:
        return settings.SITE_URL.rstrip("/")
    return request.build_absolute_uri("/").rstrip("/")


def url_destino(equipo, url_base):
    """A dónde apunta el QR: a Notion si hay link; si no, a la ficha interna."""
    if equipo.notion_url:
        return equipo.notion_url
    return url_base + equipo.get_url_publica()


def generar_qr_png(url):
    qr = qrcode.QRCode(box_size=8, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    buffer = BytesIO()
    qr.make_image(fill_color="black", back_color="white").save(buffer, format="PNG")
    return buffer.getvalue()


def _fila(c, etiqueta, valor, y, x_valor):
    c.setFont("Helvetica-Bold", 9)
    c.drawString(4 * mm, y, etiqueta)
    c.setFont("Helvetica", 9)
    c.drawString(x_valor, y, valor)


def dibujar_etiqueta(c, equipo, url_base):
    """Dibuja una etiqueta en la página actual del canvas."""
    c.setLineWidth(0.5)
    c.rect(0, 0, ANCHO, ALTO)

    c.setFont("Helvetica-Bold", 13)
    c.drawString(4 * mm, ALTO - 8 * mm, "S&M")

    _fila(c, "P.C:", (equipo.numero_serie or equipo.nombre)[:22], ALTO - 16 * mm, 14 * mm)
    _fila(c, "S.O:", (equipo.sistema_operativo or "-")[:22], ALTO - 23 * mm, 14 * mm)
    _fila(c, "Sede:", equipo.sede.nombre[:20], ALTO - 30 * mm, 16 * mm)

    qr = ImageReader(BytesIO(generar_qr_png(url_destino(equipo, url_base))))
    lado = 30 * mm
    c.drawImage(qr, ANCHO - lado - 4 * mm, (ALTO - lado) / 2, lado, lado)


def generar_pdf_etiquetas(equipos, url_base):
    """PDF con una etiqueta por página, para uno o varios equipos."""
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=(ANCHO, ALTO))
    for i, equipo in enumerate(equipos):
        if i > 0:
            c.showPage()
            c.setPageSize((ANCHO, ALTO))
        dibujar_etiqueta(c, equipo, url_base)
    c.save()
    return buffer.getvalue()
