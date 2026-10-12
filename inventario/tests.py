import re
import uuid

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from . import etiquetas
from .models import Categoria, Equipo, Sede


def crear_equipo(**extra):
    sede = Sede.objects.create(nombre="Sede de prueba")
    categoria = Categoria.objects.create(nombre="PC de prueba")
    datos = dict(nombre="PC-01", sede=sede, categoria=categoria)
    datos.update(extra)
    return Equipo.objects.create(**datos)


class DestinoTests(TestCase):
    def test_destino_se_calcula_desde_el_grupo(self):
        equipo = crear_equipo(grupo_vigencia="B")
        self.assertEqual(equipo.destino_sugerido, "Migrar a Linux Mint")

    def test_destino_sigue_al_grupo_si_cambia(self):
        equipo = crear_equipo(grupo_vigencia="A")
        equipo.grupo_vigencia = "C"
        equipo.save()
        self.assertEqual(equipo.destino_sugerido, "Mantener en uso")

    def test_destino_manual_tiene_prioridad(self):
        equipo = crear_equipo(grupo_vigencia="A", destino_manual="Donar a la posta")
        self.assertEqual(equipo.destino_sugerido, "Donar a la posta")

    def test_sin_grupo_no_hay_destino(self):
        self.assertEqual(crear_equipo().destino_sugerido, "")


class QrTests(TestCase):
    """Los QR impresos viven años: este contrato no debe romperse sin darse cuenta."""

    def test_con_link_de_notion_el_qr_apunta_a_notion(self):
        equipo = crear_equipo(notion_url="https://notion.so/pc-01")
        self.assertEqual(etiquetas.url_destino(equipo, "https://x.com"), "https://notion.so/pc-01")

    def test_sin_notion_apunta_a_la_ficha_interna(self):
        equipo = crear_equipo()
        self.assertEqual(
            etiquetas.url_destino(equipo, "https://inventario.clinica.pe"),
            f"https://inventario.clinica.pe/equipo/{equipo.id}/",
        )

    @override_settings(SITE_URL="https://dominio-fijo.pe/")
    def test_site_url_manda_sobre_el_request(self):
        respuesta = self.client.get("/", HTTP_HOST="otro-host.test")
        self.assertEqual(etiquetas.url_base_del_sitio(respuesta.wsgi_request), "https://dominio-fijo.pe")

    def test_la_imagen_qr_es_png(self):
        equipo = crear_equipo()
        respuesta = self.client.get(equipo.get_url_qr_imagen())
        self.assertEqual(respuesta.status_code, 200)
        self.assertTrue(respuesta.content.startswith(b"\x89PNG"))


class PdfTests(TestCase):
    def test_una_pagina_por_equipo_y_tamano_100x50(self):
        equipos = [crear_equipo(nombre=f"PC-{i}") for i in range(3)]
        pdf = etiquetas.generar_pdf_etiquetas(equipos, "https://x.com")
        self.assertTrue(pdf.startswith(b"%PDF"))
        self.assertEqual(len(re.findall(rb"/Type /Page\b(?!s)", pdf)), 3)
        # 100 mm = 283.46 pt, 50 mm = 141.73 pt
        self.assertIn(b"283.46", pdf)
        self.assertIn(b"141.73", pdf)


class AccesoTests(TestCase):
    def setUp(self):
        self.equipo = crear_equipo(numero_serie="SN-123", cpu="Intel i5", grupo_vigencia="A")

    def test_ficha_publica_existe_y_responde(self):
        self.assertEqual(self.client.get(self.equipo.get_url_publica()).status_code, 200)

    def test_ficha_publica_con_id_inexistente_da_404(self):
        self.assertEqual(self.client.get(reverse("equipo_publico", args=[uuid.uuid4()])).status_code, 404)

    def test_ficha_publica_no_muestra_datos_internos(self):
        contenido = self.client.get(self.equipo.get_url_publica()).content.decode()
        for secreto in ("SN-123", "Intel i5", "Dar de baja"):
            self.assertNotIn(secreto, contenido)

    def test_personal_si_ve_la_ficha_tecnica(self):
        User = get_user_model()
        self.client.force_login(User.objects.create_user("sistemas", password="x", is_staff=True))
        contenido = self.client.get(self.equipo.get_url_publica()).content.decode()
        for dato in ("SN-123", "Intel i5", "Dar de baja"):
            self.assertIn(dato, contenido)

    def test_etiqueta_pdf_exige_sesion_de_personal(self):
        respuesta = self.client.get(self.equipo.get_url_etiqueta_pdf())
        self.assertEqual(respuesta.status_code, 302)  # redirige al login

    def test_etiqueta_pdf_para_personal(self):
        User = get_user_model()
        self.client.force_login(User.objects.create_user("sistemas", password="x", is_staff=True))
        respuesta = self.client.get(self.equipo.get_url_etiqueta_pdf())
        self.assertEqual(respuesta["Content-Type"], "application/pdf")


# El admin carga archivos estáticos con {% static %}. En producción usamos Whitenoise con manifiesto,
# que exige haber corrido collectstatic; en las pruebas usamos el almacenamiento simple.
ALMACENAMIENTO_SIMPLE = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}


@override_settings(STORAGES=ALMACENAMIENTO_SIMPLE)
class AdminAltaTests(TestCase):
    def test_pagina_de_alta_no_ofrece_etiqueta_ni_qr_de_un_equipo_sin_guardar(self):
        User = get_user_model()
        self.client.force_login(User.objects.create_superuser("admin", "a@a.pe", "x"))
        contenido = self.client.get(reverse("admin:inventario_equipo_add")).content.decode()
        self.assertNotIn("etiqueta.pdf", contenido)
        self.assertIn("Disponible al guardar el equipo", contenido)
        self.assertIn("Se genera al guardar el equipo", contenido)