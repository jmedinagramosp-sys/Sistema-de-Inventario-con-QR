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
            select.value = opt.value;
            var form = select.closest('form');
            if (form) form.submit();
        });

        toolbar.appendChild(btn);
    });

    actionsDiv.insertBefore(toolbar, actionsDiv.firstChild);
});