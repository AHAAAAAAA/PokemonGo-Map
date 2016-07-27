module.exports = function(grunt) {

  grunt.initConfig({
    pkg: grunt.file.readJSON('package.json'),

    sass: {
      dist: {
        files: {
          'static/dist/css/app.css': [
            'static/sass/main.scss',
            'static/sass/pokemon-sprite.scss'
          ]
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
          'static/dist/js/app.js': 'static/js/app.js',
          'static/dist/js/map.js': 'static/map.js' // Todo: move map.js into the js folder
        }
      }
    },
    uglify: {
      options: {
        banner: '/*\n <%= pkg.name %> <%= grunt.template.today("yyyy-mm-dd") %> \n*/\n',
        sourceMap: true
      },
      build: {
        files: {
          'static/dist/js/app.min.js': 'static/dist/js/app.js',
          'static/dist/js/map.min.js': 'static/dist/js/map.js'
        }
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
        tasks: ['babel', 'uglify']
      },
      css: {
        files: '**/*.scss',
        options: { livereload: true },
        tasks: ['sass', 'cssmin']
      }
    },
    cssmin: {
      options: {
        banner: '/*\n <%= pkg.name %> <%= grunt.template.today("yyyy-mm-dd") %> \n*/\n'
      },
      build: {
        files: {
          'static/dist/css/app.min.css': 'static/dist/css/app.css'
        }
      }
    },
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

  grunt.registerTask('build', ['jshint', 'sass', 'cssmin', 'babel', 'uglify']);
  grunt.registerTask('default', ['build', 'watch']);

};
