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
  			files: ['**/*.js', '!node_modules/**/*.js'],
  			options: { livereload: true }
  		},
  		css: {
  			files: '**/*.scss',
  			options: { livereload: true },
  			tasks: ['sass','cssmin']
  		}
    },
    cssmin: {
  	  target: {
    		files: [{
    		  expand: true,
    		  cwd: 'css',
    		  src: ['main.css', '!*.min.css'],
    		  dest: 'static/css',
    		  ext: '.min.css'
    		}]
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
  grunt.loadNpmTasks('grunt-contrib-connect');
  grunt.loadNpmTasks('grunt-usemin');
  grunt.loadNpmTasks('grunt-unused');
  grunt.loadNpmTasks('grunt-contrib-concat');
  grunt.loadNpmTasks('grunt-html-validation');

  grunt.registerTask('default', ['sass','cssmin','watch']);

};
