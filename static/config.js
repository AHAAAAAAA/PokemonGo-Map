'use strict';

// CHANGE ME
window.CONFIG = {
  latitude: 40.2338438
, longitude: -111.65853370000002
, gmaps_key: 'AIzaSyB0Dqa90ZCmlwh7oPHkgfr2-cMMkufLBQE'
, requireLogin: true
};

// Auto-detect language to use
window.document.documentElement.lang = 'en';
[ 'de', 'en', 'fr', 'pt_br', 'ru', 'zh_cn', 'zh_hk' ].some(function (lang) {
  if (window.navigator.language.match(lang)) {
    window.document.documentElement.lang = lang;
    return true;
  }
});
