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

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=150)
    categoria = models.ForeignKey(
        Categoria, on_delete=models.PROTECT, related_name="equipos"
    )
    sede = models.ForeignKey(
        Sede, on_delete=models.PROTECT, related_name="equipos"
    )
    ubicacion = models.CharField(
        max_length=150, blank=True, help_text="Ej. Piso 2 · Consultorio 3"
    )
    estado = models.CharField(
        max_length=4, choices=Estado.choices, default=Estado.OPERATIVO
    )
    fecha_registro = models.DateTimeField(auto_now_add=True)

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
