'use strict';

(function() {
  function isDarkMode() {
    var t = document.documentElement.getAttribute('data-theme');
    if (t === 'dark') return true;
    if (t === 'light') return false;
    return window.matchMedia('(prefers-color-scheme: dark)').matches;
  }

  var origInit = tinyMCE.init;
  tinyMCE.init = function(config) {
    if (isDarkMode()) {
      config.skin = 'oxide-dark';
      config.content_css = 'dark';
    }
    return origInit.call(this, config);
  };
})();
