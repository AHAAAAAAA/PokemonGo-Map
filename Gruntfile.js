module.exports = function(grunt) {

  grunt.initConfig({
    pkg: grunt.file.readJSON('package.json'),

    sass: {
      dist: {
        files: {
          'static/dist/css/app.built.css': [
            'static/sass/main.scss',
            'static/sass/pokemon-sprite.scss'
          ],
          'static/dist/css/mobile.built.css': 'static/sass/mobile.scss'
        }
      }
    },
    jshint: {
      files: ['Gruntfile.js', 'js/*.js', '!js/vendor/**/*.js'],
      options: {
        reporter: require('jshint-stylish'),
        globals: {
          jQuery: true,
          console: true,
          module: true,
          document: true
        }
      }
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
          'static/dist/js/mobile.built.js': 'static/js/mobile.js',
          'static/dist/js/stats.built.js': 'static/js/stats.js'
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
          'static/dist/js/mobile.min.js': 'static/dist/js/mobile.built.js',
          'static/dist/js/stats.min.js': 'static/dist/js/stats.built.js'
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
        tasks: ['js-lint', 'js-build']
      },
      css: {
        files: '**/*.scss',
        options: { livereload: true },
        tasks: ['css-build']
      }
    },
    cssmin: {
      options: {
        banner: '/*\n <%= pkg.name %> <%= grunt.template.today("yyyy-mm-dd") %> \n*/\n'
      },
      build: {
        files: {
          'static/dist/css/app.min.css': 'static/dist/css/app.built.css',
          'static/dist/css/mobile.min.css': 'static/dist/css/mobile.built.css'
        }
      }
    }
  });

  grunt.loadNpmTasks('grunt-contrib-uglify');
  grunt.loadNpmTasks('grunt-contrib-jshint');
  grunt.loadNpmTasks('grunt-contrib-watch');
  grunt.loadNpmTasks('grunt-sass');
  grunt.loadNpmTasks('grunt-contrib-copy');
  grunt.loadNpmTasks('grunt-contrib-clean');
  grunt.loadNpmTasks('grunt-contrib-cssmin');
  grunt.loadNpmTasks('grunt-usemin');
  grunt.loadNpmTasks('grunt-contrib-concat');
  grunt.loadNpmTasks('grunt-html-validation');
  grunt.loadNpmTasks('grunt-babel');

  grunt.registerTask('js-build', ['babel', 'uglify']);
  grunt.registerTask('css-build', ['sass', 'cssmin']);
  grunt.registerTask('js-lint', ['jshint']);

  grunt.registerTask('build', ['clean', 'js-build', 'css-build']);
  grunt.registerTask('lint', ['js-lint']);
  grunt.registerTask('default', ['lint', 'build', 'watch']);

};
