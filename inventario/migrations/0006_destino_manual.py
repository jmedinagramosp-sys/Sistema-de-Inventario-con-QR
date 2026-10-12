from django.db import migrations, models

DESTINOS = {
    "A": "Dar de baja / reemplazar",
    "B": "Migrar a Linux Mint",
    "C": "Mantener en uso",
}


def conservar_destinos_manuales(apps, schema_editor):
    """Solo se conservan como 'manual' los destinos que NO coinciden con el automático;
    así los casos particulares no se pierden y los valores viejos del sistema se recalculan."""
    Equipo = apps.get_model("inventario", "Equipo")
    for equipo in Equipo.objects.exclude(destino_sugerido=""):
        if equipo.destino_sugerido != DESTINOS.get(equipo.grupo_vigencia, ""):
            equipo.destino_manual = equipo.destino_sugerido
            equipo.save(update_fields=["destino_manual"])


class Migration(migrations.Migration):

    dependencies = [
        ("inventario", "0005_equipo_notion_url_alter_equipo_numero_serie"),
    ]

    operations = [
        migrations.AddField(
            model_name="equipo",
            name="destino_manual",
            field=models.CharField(
                blank=True, max_length=150, verbose_name="Destino (manual)",
                help_text="Solo si este equipo es un caso particular. Si lo dejas vacío, "
                          "el destino se calcula solo según el grupo de vigencia.",
            ),
        ),
        migrations.RunPython(conservar_destinos_manuales, migrations.RunPython.noop),
        migrations.RemoveField(model_name="equipo", name="destino_sugerido"),
    ]
