// Nombre del tipo de elemento de la página actual, según la clase que Django pone en <body>
function nombreDelElemento() {
    var nombres = {
        'model-equipo': 'equipo',
        'model-categoria': 'categoría',
        'model-sede': 'sede',
        'model-group': 'grupo',
        'model-user': 'usuario'
    };
    for (var clase in nombres) {
        if (document.body.classList.contains(clase)) return nombres[clase];
    }
    return 'elemento';
}

// Aviso flotante, independiente del diseño de la página
function mostrarAviso(texto) {
    var previo = document.getElementById('aviso-seleccion');
    if (previo) previo.remove();

    var aviso = document.createElement('div');
    aviso.id = 'aviso-seleccion';
    aviso.setAttribute('role', 'alert');
    aviso.textContent = texto;
    aviso.style.cssText = 'position:fixed;top:24px;left:50%;transform:translateX(-50%);z-index:9999;' +
        'background:#2F4A63;color:#fff;padding:12px 22px;border-radius:999px;font-size:14px;font-weight:500;' +
        'box-shadow:0 8px 24px rgba(31,45,58,.25);transition:opacity .3s;';
    document.body.appendChild(aviso);

    setTimeout(function () { aviso.style.opacity = '0'; }, 2500);
    setTimeout(function () { aviso.remove(); }, 2900);
}

document.addEventListener('DOMContentLoaded', function () {
    var actionsDiv = document.querySelector('#changelist-form .actions');
    if (!actionsDiv) return;

    var select = actionsDiv.querySelector('select[name="action"]');
    if (!select) return;

    var goBtn = actionsDiv.querySelector('button[type="submit"], input[type="submit"]');

    select.style.display = 'none';
    if (goBtn) goBtn.style.display = 'none';

    // Íconos SVG de línea fina (estilo outline), no emojis del sistema operativo
    var SVG_BASURERO = '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18"/><path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/><line x1="10" y1="11" x2="10" y2="17"/><line x1="14" y1="11" x2="14" y2="17"/></svg>';

    var SVG_ETIQUETA = '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20.59 13.41 11 3.83A2 2 0 0 0 9.59 3.24L3.83 3.83A2 2 0 0 0 3.24 9.59L12.83 19.17a2 2 0 0 0 2.83 0l4.93-4.93a2 2 0 0 0 0-2.83Z"/><circle cx="7.5" cy="7.5" r="1.5"/></svg>';

    var SVG_RAYO = '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>';

    var iconos = {
        'delete_selected': { svg: SVG_BASURERO, clase: 'accion-borrar' },
        'descargar_etiquetas_pdf': { svg: SVG_ETIQUETA, clase: 'accion-pdf' },
    };

    var toolbar = document.createElement('div');
    toolbar.className = 'acciones-iconos';

    Array.prototype.forEach.call(select.options, function (opt) {
        if (!opt.value) return;

        var cfg = iconos[opt.value] || { svg: SVG_RAYO, clase: 'accion-generica' };

        var btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'action-icon-btn ' + cfg.clase;
        btn.title = opt.textContent.trim();
        btn.innerHTML = cfg.svg;

        btn.addEventListener('click', function () {
            // Django no avisa nada si se envía el formulario sin selección: lo validamos aquí.
            var marcados = document.querySelectorAll('#changelist-form input.action-select:checked');
            var todosLosResultados = document.querySelector('#changelist-form input[name="select_across"][value="1"]');
            if (marcados.length === 0 && !todosLosResultados) {
                mostrarAviso('Selecciona al menos 1 ' + nombreDelElemento() + '.');
                return;
            }
            select.value = opt.value;
            var form = select.closest('form');
            if (form) form.submit();
        });

        toolbar.appendChild(btn);
    });

    actionsDiv.insertBefore(toolbar, actionsDiv.firstChild);
});