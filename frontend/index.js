/* LoDCORE · Página principal (index.js)
   - Perfiles como pestañas accesibles (flechas, Inicio/Fin) con enlace directo: #perfil-ciudadania, #perfil-gestion, #perfil-inversion.
   - Desplazamiento suave a los apartados de la propia página.
   - Detección inteligente de entorno: enlaces APEX en producción o navegación local en demo.
   Sin JavaScript todos los perfiles se muestran uno debajo de otro. */
(function () {
  'use strict';

  function iniciar() {
    var raiz = document.getElementById('lodcore-home');
    if (!raiz) return;

    var tabs = Array.prototype.slice.call(raiz.querySelectorAll('[role="tab"]'));
    var paneles = Array.prototype.slice.call(raiz.querySelectorAll('[role="tabpanel"]'));
    var reducir = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    // ---------- Detección de entorno (APEX vs Local) ----------
    var esApex = (typeof window.apex !== 'undefined') || (window.location.search.indexOf('p=') !== -1);
    if (!esApex) {
      // Si estamos en entorno local / demo, adaptar enlaces APEX para que funcionen con un clic
      var enlaces = Array.prototype.slice.call(raiz.querySelectorAll('a[href^="f?p="]'));
      enlaces.forEach(function (enlace) {
        var href = enlace.getAttribute('href');
        if (href.indexOf('mapa') !== -1) {
          enlace.setAttribute('href', 'mapa/mapa.html');
        } else if (href.indexOf('PERFIL_CIUDADANIA') !== -1) {
          enlace.setAttribute('href', '#perfil-ciudadania');
        } else if (href.indexOf('PERFIL_GESTION') !== -1) {
          enlace.setAttribute('href', '#perfil-gestion');
        } else if (href.indexOf('PERFIL_INVERSION') !== -1) {
          enlace.setAttribute('href', '#perfil-inversion');
        } else if (href.indexOf('simulador') !== -1) {
          enlace.setAttribute('href', '#perfiles');
        }
      });
    }

    // ---------- Pestañas de perfil ----------
    function activar(tab, enfocar) {
      tabs.forEach(function (t) {
        var activa = (t === tab);
        t.setAttribute('aria-selected', activa ? 'true' : 'false');
        t.setAttribute('tabindex', activa ? '0' : '-1');
      });
      paneles.forEach(function (p) {
        p.hidden = (p.id !== tab.getAttribute('aria-controls'));
      });
      if (enfocar) tab.focus();
    }

    if (tabs.length) {
      raiz.classList.add('has-js');
      var inicial = tabs.filter(function (t) { return t.getAttribute('aria-selected') === 'true'; })[0] || tabs[0];
      activar(inicial, false);

      tabs.forEach(function (tab, i) {
        tab.addEventListener('click', function () { activar(tab, false); });
        tab.addEventListener('keydown', function (e) {
          var destino = null;
          if (e.key === 'ArrowRight' || e.key === 'ArrowDown') destino = tabs[(i + 1) % tabs.length];
          else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') destino = tabs[(i - 1 + tabs.length) % tabs.length];
          else if (e.key === 'Home') destino = tabs[0];
          else if (e.key === 'End') destino = tabs[tabs.length - 1];
          if (destino) { e.preventDefault(); activar(destino, true); }
        });
      });
    }

    // Enlace directo a un perfil (#perfil-gestion, ...)
    function perfilDesdeHash() {
      var id = (window.location.hash || '').replace('#', '');
      var tab = tabs.filter(function (t) { return t.getAttribute('aria-controls') === id; })[0];
      if (!tab) return false;
      activar(tab, false);
      var seccion = document.getElementById('perfiles');
      if (seccion) seccion.scrollIntoView({ behavior: reducir ? 'auto' : 'smooth', block: 'start' });
      return true;
    }
    window.addEventListener('hashchange', perfilDesdeHash);
    perfilDesdeHash();

    // ---------- Desplazamiento suave a los apartados de la página ----------
    raiz.addEventListener('click', function (e) {
      var a = e.target.closest ? e.target.closest('a[href^="#"]') : null;
      if (!a) return;
      var id = a.getAttribute('href').slice(1);
      var destino = id ? document.getElementById(id) : null;
      if (!destino) return;
      e.preventDefault();
      destino.scrollIntoView({ behavior: reducir ? 'auto' : 'smooth', block: 'start' });
      if (window.history && history.replaceState) history.replaceState(null, '', '#' + id);
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', iniciar);
  } else {
    iniciar();
  }
})();
