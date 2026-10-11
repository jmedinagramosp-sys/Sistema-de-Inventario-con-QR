document.addEventListener('DOMContentLoaded', function () {
    var panel = document.getElementById('changelist-filter');
    if (!panel) return;

    // Cuenta los filtros realmente activos (el primer chip de cada sección es "All")
    var activos = 0;
    panel.querySelectorAll('.filtro-seccion').forEach(function (seccion) {
        seccion.querySelectorAll('.chip').forEach(function (chip, i) {
            if (i > 0 && chip.classList.contains('chip-activo')) activos++;
        });
    });

    var titulo = panel.querySelector('h2');
    if (titulo) {
        titulo.textContent = 'Filtros Avanzados' + (activos ? ' (' + activos + ' activos)' : '');
    }
});