'use strict';

// CHANGE ME
window.CONFIG = {
  latitude: {{lat}}
, longitude: {{lat}}
, gmaps_key: '{{ gmaps_key }}'
};

// Auto-detect language to use
window.document.documentElement.lang = '{{lang}}';
[ 'de', 'en', 'fr', 'pt_br', 'ru', 'zh_cn', 'zh_hk' ].some(function (lang) {
  if (window.navigator.language.match(lang)) {
    window.document.documentElement.lang = 'en';
    return true;
  }
});
