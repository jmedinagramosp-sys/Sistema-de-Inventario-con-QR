import uuid

from django.db import models
from django.urls import reverse


class Sede(models.Model):
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=200, blank=True)
    color_hex = models.CharField(
        max_length=7,
        default="#14464A",
        help_text="Color de identificación de la sede, ej. #14464A",
    )

    class Meta:
        verbose_name = "Sede"
        verbose_name_plural = "Sedes"

    def __str__(self):
        return self.nombre


class Categoria(models.Model):
    nombre = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"

    def __str__(self):
        return self.nombre


class Equipo(models.Model):
    class Estado(models.TextChoices):
        OPERATIVO = "OK", "Operativo"
        REVISION = "REV", "En revisión"
        BAJA = "BAJA", "De baja"

    class GrupoVigencia(models.TextChoices):
        A = "A", "Grupo A — Obsoleto (va a baja/reemplazo)"
        B = "B", "Grupo B — Funcional (candidato a Linux Mint)"
        C = "C", "Grupo C — Vigente (se mantiene)"

    DESTINOS_SUGERIDOS = {
        GrupoVigencia.A: "Dar de baja / reemplazar",
        GrupoVigencia.B: "Migrar a Linux Mint",
        GrupoVigencia.C: "Mantener en uso",
    }

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=150)
    categoria = models.ForeignKey(
        Categoria, on_delete=models.PROTECT, related_name="equipos"
    )
    sede = models.ForeignKey(
        Sede, on_delete=models.PROTECT, related_name="equipos"
    )
    ubicacion = models.CharField(
        max_length=150, blank=True, help_text="Área/ubicación, ej. Piso 2 · Consultorio 3"
    )
    estado = models.CharField(
        max_length=4, choices=Estado.choices, default=Estado.OPERATIVO
    )
    fecha_registro = models.DateTimeField(auto_now_add=True)

    # --- Link de Notion: si existe, el QR apunta aquí en vez de a la página interna ---
    notion_url = models.URLField(
        max_length=300,
        blank=True,
        verbose_name="Link de Notion",
        help_text="Pega aquí el 'Copy link' de la página de Notion de este equipo. "
                   "Si lo dejas vacío, el QR usará la página interna del sistema.",
    )

    # --- Ficha técnica (aplica principalmente a PCs/laptops) ---
    modelo = models.CharField(max_length=150, blank=True, help_text="Ej. Dell Optiplex 3020")
    cpu = models.CharField(max_length=150, blank=True, help_text="Ej. Intel i5 10ª generación")
    ram_gb = models.PositiveIntegerField(blank=True, null=True, verbose_name="RAM (GB)")
    sistema_operativo = models.CharField(max_length=100, blank=True, help_text="Ej. Windows 10, Linux Mint")
    numero_serie = models.CharField(
        max_length=100, blank=True, verbose_name="N° de serie (referencial)",
        help_text="Dato de referencia del fabricante — no es el identificador oficial, ese es el QR/código del sistema",
    )

    # --- Clasificación de vigencia del parque de PCs ---
    grupo_vigencia = models.CharField(
        max_length=1,
        choices=GrupoVigencia.choices,
        blank=True,
        help_text="Clasificación según antigüedad y capacidad (solo aplica a PCs)",
    )
    destino_manual = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Destino (manual)",
        help_text="Solo si este equipo es un caso particular. Si lo dejas vacío, "
                  "el destino se calcula solo según el grupo de vigencia.",
    )

    # --- Estaciones médicas (rayos X, espirometría, ECG, etc.) ---
    software_asociado = models.CharField(
        max_length=200,
        blank=True,
        help_text="Ej. Consola CareRay + PACS dicomPACS",
    )

    class Meta:
        verbose_name = "Equipo"
        verbose_name_plural = "Equipos"
        ordering = ["-fecha_registro"]

    def __str__(self):
        return f"{self.nombre} ({self.sede.nombre})"

    def get_url_publica(self):
        return reverse("equipo_publico", args=[self.id])

    def get_url_qr_imagen(self):
        return reverse("equipo_qr_imagen", args=[self.id])

    def get_url_etiqueta(self):
        return reverse("equipo_etiqueta", args=[self.id])

    def get_url_etiqueta_pdf(self):
        return reverse("equipo_etiqueta_pdf", args=[self.id])

    @property
    def destino_sugerido(self):
        """Destino a mostrar. Se calcula cada vez a partir del grupo, así nunca queda
        desactualizado si el grupo cambia; el valor manual solo lo reemplaza si existe."""
        if self.destino_manual:
            return self.destino_manual
        return self.DESTINOS_SUGERIDOS.get(self.grupo_vigencia, "")
