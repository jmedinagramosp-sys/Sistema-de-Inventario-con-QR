from django.db import migrations


def crear_datos_iniciales(apps, schema_editor):
    Sede = apps.get_model("inventario", "Sede")
    Categoria = apps.get_model("inventario", "Categoria")

    Sede.objects.get_or_create(nombre="Clínica Comas", defaults={"color_hex": "#14464A"})
    Sede.objects.get_or_create(nombre="Clínica San Miguel", defaults={"color_hex": "#9C7A3C"})

    categorias = [
        "PC de escritorio",
        "Laptop",
        "Estación médica",
        "Mobiliario",
        "Red",
    ]
    for nombre in categorias:
        Categoria.objects.get_or_create(nombre=nombre)


def revertir(apps, schema_editor):
    # No se borran datos al revertir, para no perder equipos ya vinculados.
    pass


class Migration(migrations.Migration):

    dependencies = [
        # Ajusta este número al de tu última migración existente si es distinto
        ("inventario", "0002_remove_equipo_codigo_qr"),
    ]

    operations = [
        migrations.RunPython(crear_datos_iniciales, revertir),
    ]