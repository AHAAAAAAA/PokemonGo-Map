'use strict';

// CHANGE ME
window.CONFIG = {
  latitude: 40.36915523640919
, longitude: -111.75098587678943
, gmaps_key: 'AIzaSyAZzeHhs-8JZ7i18MjFuM35dJHq70n3Hx4'
};

// Auto-detect language to use
window.document.documentElement.lang = 'en';
[ 'de', 'en', 'fr', 'pt_br', 'ru', 'zh_cn', 'zh_hk' ].some(function (lang) {
  if (window.navigator.language.match(lang)) {
    window.document.documentElement.lang = 'en';
    return true;
  }
});
