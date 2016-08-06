module.exports = function(grunt) {

  // load plugins as needed instead of up front
  require('jit-grunt')(grunt);

  grunt.initConfig({
    pkg: grunt.file.readJSON('package.json'),

    sass: {
      dist: {
        files: {
          'static/dist/css/app.built.css': [
            'static/sass/main.scss',
            'static/sass/pokemon-sprite.scss'
          ],
          'static/dist/css/mobile.built.css': 'static/sass/mobile.scss',
          'static/dist/css/statistics.built.css': 'static/css/statistics.css'
        }
      }
    },
    eslint: {
      src: ['static/js/*.js', '!js/vendor/**/*.js']
    },
    babel: {
      options: {
        sourceMap: true,
        presets: ['es2015']
      },
      dist: {
        files: {
          'static/dist/js/app.built.js': 'static/js/app.js',
          'static/dist/js/map.built.js': 'static/js/map.js',
          'static/dist/js/beehive.built.js': 'static/js/beehive.js',
          'static/dist/js/mobile.built.js': 'static/js/mobile.js',
          'static/dist/js/stats.built.js': 'static/js/stats.js',
          'static/dist/js/statistics.built.js': 'static/js/statistics.js'
        }
      }
    },
    uglify: {
      options: {
        banner: '/*\n <%= pkg.name %> <%= grunt.template.today("yyyy-mm-dd") %> \n*/\n',
        sourceMap: true,
        compress: {
          unused: false
        }
      },
      build: {
        files: {
          'static/dist/js/app.min.js': 'static/dist/js/app.built.js',
          'static/dist/js/map.min.js': 'static/dist/js/map.built.js',
          'static/dist/js/beehive.min.js': 'static/dist/js/beehive.built.js',
          'static/dist/js/mobile.min.js': 'static/dist/js/mobile.built.js',
          'static/dist/js/stats.min.js': 'static/dist/js/stats.built.js',
          'static/dist/js/statistics.min.js': 'static/dist/js/statistics.built.js'
        }
      }
    },
    minjson: {
      build: {
        files: {
          'static/dist/data/pokemon.min.json': 'static/data/pokemon.json',
          'static/dist/data/mapstyle.min.json': 'static/data/mapstyle.json',
          'static/dist/locales/de.min.json': 'static/locales/de.json',
          'static/dist/locales/fr.min.json': 'static/locales/fr.json',
          'static/dist/locales/pt_br.min.json': 'static/locales/pt_br.json',
          'static/dist/locales/ru.min.json': 'static/locales/ru.json',
          'static/dist/locales/zh_cn.min.json': 'static/locales/zh_cn.json',
          'static/dist/locales/zh_hk.min.json': 'static/locales/zh_hk.json'
        }
      }
    },
    clean: {
      build: {
        src: 'static/dist'
      }
    },
    watch: {
      options: {
        interval: 1000,
        spawn: true
      },
      src: {
        files: ['**/*.html'],
        options: { livereload: true }
      },
      js: {
        files: ['**/*.js', '!node_modules/**/*.js', '!static/dist/**/*.js'],
        options: { livereload: true },
        tasks: ['newer:eslint', 'newer:babel', 'newer:uglify']
      },
      json: {
        files: ['**/*.json', '!static/dist/**/*.json', '!package.json'],
        options: { livereload: true },
        tasks: ['newer:minjson']
      },
      css: {
        files: '**/*.scss',
        options: { livereload: true },
        tasks: ['newer:sass', 'newer:cssmin']
      }
    },
    cssmin: {
      options: {
        banner: '/*\n <%= pkg.name %> <%= grunt.template.today("yyyy-mm-dd") %> \n*/\n'
      },
      build: {
        files: {
          'static/dist/css/app.min.css': 'static/dist/css/app.built.css',
          'static/dist/css/mobile.min.css': 'static/dist/css/mobile.built.css',
          'static/dist/css/statistics.min.css': 'static/dist/css/statistics.built.css'
        }
      }
    }
  });

  grunt.registerTask('js-build', ['babel', 'uglify']);
  grunt.registerTask('css-build', ['sass', 'cssmin']);
  grunt.registerTask('js-lint', ['eslint']);

  grunt.registerTask('build', ['clean', 'js-build', 'css-build', 'minjson']);
  grunt.registerTask('lint', ['js-lint']);
  grunt.registerTask('default', ['build', 'watch']);

};
