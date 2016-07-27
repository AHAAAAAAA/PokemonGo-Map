ps ax | grep runserver | grep -v 'grep runserver' | awk '{print $1}' | xargs kill
