module.exports = function(grunt) {

  grunt.initConfig({
    pkg: grunt.file.readJSON('package.json'),

    sass: {
  		dist: {
  			files: {
  			  'static/css/main.css' : 'static/sass/main.scss'
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
    uglify: {
      options: {
        banner: '/*\n <%= pkg.name %> <%= grunt.template.today("yyyy-mm-dd") %> \n*/\n'
      },
      build: {
        files: {
          'static/dist/js/app.min.js': 'static/js/app.js'
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
        tasks: ['uglify']
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
          'static/dist/css/app.min.css': 'static/css/main.css'
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

  grunt.registerTask('default', ['jshint', 'sass', 'cssmin', 'uglify', 'watch']);

};
