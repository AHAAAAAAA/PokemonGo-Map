App Development
#######################

.. note:: This article is about contributing to the development codebase. For contributing to the map itself see :doc:`contributing`.

.. warning::

  These instructions will help you get started contributing code to the **develop** branch.
  If you just want to **use the map** you should not use **develop**.
  `Download a release <https://github.com/AHAAAAAAA/PokemonGo-Map/releases>`_ instead.

Development requires several tools to get the job done. Python, obviously, needs to be installed. We also utilize NodeJS and Grunt for front-end tasks.

Node and Grunt
***********************

Grunt is a tool to automatically run tasks against the code. We use grunt to transform the Javascript and CSS before it's run, and bundle it up for distribution.

If you want to change the Javascript or CSS, you must install and run Grunt to see your changes

Installing Node
====================

Download Node from the official site and install it. Version 4 or 6 will both work.

https://nodejs.org/en/

Installing ``grunt``
====================

After Node is installed, go into the project directory from the command-line, as usual.

Then run this command

``npm install -g grunt``

This installs a "global" copy of grunt on your machine. You also need a local copy for the project. Run:

``npm install``

This will install everything the ``package.json`` lists; a local copy of grunt, a lot of plug-ins, etc.

Running ``grunt``
===================

After Grunt is installed successfully, you need to run it when you change Javascript or CSS.

Simply type

``grunt``

on the command-line. This runs a default grunt "task" that performs a number of subtasks, like transforming JS with Babel, minifying, linting, and copying (see `Gruntfile.js <https://github.com/AHAAAAAAA/PokemonGo-Map/blob/develop/Gruntfile.js>`_)

grunt-watch
====================

We've configured Grunt to run a "watch" task by default. Grunt will sit in the background continually re-running its tasks any time a Javascript or CSS file changes. You can leave this Watch task running while you code, to avoid the need to continually re-run Grunt every time you make a change.  You can stop grunt-watch with CTRL+C.

The "/dist" directory
***********************

Files in the "static/dist/" subdirectories should not be edited. These will be automatically overwritten by Grunt.

To make your changes you want to edit e.g. ``static/js/map.js``
