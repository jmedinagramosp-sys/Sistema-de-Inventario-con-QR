from io import BytesIO

import qrcode
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

from .models import Equipo


def equipo_publico(request, equipo_id):
    """La página web completa: incluye ficha técnica, fechas, clasificación, etc."""
    equipo = get_object_or_404(Equipo, pk=equipo_id)
    return render(request, "inventario/publico.html", {"equipo": equipo})


def equipo_etiqueta(request, equipo_id):
    """Vista pensada para imprimirse junto al QR en el sticker físico:
    solo lo esencial (sede, modelo, sistema operativo), nada más.
    """
    equipo = get_object_or_404(Equipo, pk=equipo_id)
    return render(request, "inventario/etiqueta.html", {"equipo": equipo})


def equipo_qr_imagen(request, equipo_id):
    """Genera la imagen QR en memoria, sin guardar ningún archivo en disco."""
    equipo = get_object_or_404(Equipo, pk=equipo_id)
    url = request.build_absolute_uri(equipo.get_url_publica())

    qr = qrcode.QRCode(box_size=8, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return HttpResponse(buffer.getvalue(), content_type="image/png")