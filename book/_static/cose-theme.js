/* Synchronize CoSE color-scheme meta tag with Sphinx Book Theme light/dark state */
(function () {
  "use strict";
  function ensureMeta() {
    var meta = document.querySelector('meta[name="color-scheme"]');
    if (!meta) {
      meta = document.createElement("meta");
      meta.name = "color-scheme";
      meta.content = "light dark";
      document.head.appendChild(meta);
    }
    return meta;
  }

  function syncScheme() {
    var meta = ensureMeta();
    var t = document.documentElement.getAttribute("data-theme");
    if (t === "dark" || t === "light") {
      meta.content = t;
    } else {
      meta.content = "light dark";
    }
  }

  syncScheme();
  var obs = new MutationObserver(syncScheme);
  obs.observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme"] });
})();
