# Sistema de inventario con QR — Clínica Comas / San Miguel

Sistema de gestión de inventario para una clínica con múltiples sedes. Cada equipo registrado genera automáticamente un código QR único que, al escanearse, muestra a qué sede pertenece y su información básica — sin necesidad de instalar ninguna app.

## Problema que resuelve

En clínicas con varias sedes es común que equipos (monitores, laptops, mobiliario) terminen sin identificación clara de a qué sede pertenecen, o directamente olvidados sin registro. Este sistema resuelve eso con una etiqueta física de QR por equipo, vinculada a un panel de administración central.

## Cómo funciona

1. Un administrador registra el equipo (nombre, sede, categoría, ubicación) desde un panel de administración.
2. Al guardar, el sistema genera automáticamente un código QR único para ese equipo, sin guardar ningún archivo en disco.
3. Se imprime la etiqueta y se pega físicamente en el equipo.
4. Cualquier persona puede escanear el QR con la cámara de su celular y ver de inmediato a qué sede pertenece el equipo y su estado, sin necesidad de cuenta ni app instalada.

## Stack

- **Backend**: Django
- **Base de datos**: SQLite (desarrollo) / PostgreSQL (producción)
- **Generación de QR**: librería `qrcode` (Python), generado en memoria al momento de la petición
- **Frontend**: HTML + CSS (sin frameworks de JS)
- **Servidor de producción**: Gunicorn + Whitenoise
- **Despliegue**: Render

## Seguridad

- Credenciales y configuración sensible (`SECRET_KEY`, `DEBUG`, hosts permitidos) manejadas por variables de entorno, nunca en el código.
- Cabeceras de seguridad HTTP activas en producción (HSTS, cookies seguras, `X-Frame-Options`, redirección forzada a HTTPS).
- El código QR se genera dinámicamente en cada petición en vez de almacenarse como archivo, evitando dependencias de almacenamiento persistente.

## Instalación local

```bash
git clone https://github.com/tu-usuario/tu-repo.git
cd clinica-inventario

python -m venv venv
venv\Scripts\activate        # En Mac/Linux: source venv/bin/activate

pip install -r requirements.txt

cp .env.example .env
# Edita .env y coloca una SECRET_KEY propia

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```


Luego entra a `http://127.0.0.1:8000/admin/` para registrar sedes, categorías y equipos.

## Estructura del proyecto

## Estructura del proyecto

```
clinica-inventario/
├── config/                  # Configuración del proyecto Django
├── inventario/              # App principal
│   ├── models.py            # Sede, Categoria, Equipo
│   ├── admin.py             # Panel de administración con vista previa del QR
│   ├── views.py             # Vista pública y generación del QR al vuelo
│   └── templates/
│       └── inventario/
│           └── publico.html
└── requirements.txt
```
## Próximos pasos

- [ ] Historial de movimientos entre sedes
- [ ] API REST para una futura app móvil de escaneo
- [ ] Grupos y permisos diferenciados por rol (recepción, técnico, administrador)

## Contexto

Proyecto desarrollado durante mis prácticas de Ingeniería de Sistemas, a partir de un problema real observado en campo: Equipos sin identificación clara de sede a la que pertenece ni estado de uso.


