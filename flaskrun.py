import argparse


def flask_argparse(app, default_host="127.0.0.1",
             default_port="5000"):
    """
    Takes a flask.Flask instance and runs it. Parses
    command-line flags to configure the app.
    """

    # Set up the command-line options
    parser = argparse.ArgumentParser()

    parser.add_argument("-H", "--host",
                        help="Hostname of the Flask app " +
                             "[default %s]" % default_host,
                        default=default_host)
    parser.add_argument("-P", "--port",
                        help="Port for the Flask app " +
                             "[default %s]" % default_port,
                        default=default_port)

    parser.add_argument("-u", "--username", help="PTC Username", required=True)
    parser.add_argument("-p", "--password", help="PTC Password", required=True)
    parser.add_argument("-l", "--location", help="Location", required=True)
    parser.add_argument("-st", "--step_limit", help="Steps", required=True)
    parser.add_argument("-d", "--debug", help="Debug Mode", action='store_true')

    parser.set_defaults(DEBUG=True)

    # Two options useful for debugging purposes, but
    # a bit dangerous so not exposed in the help message.
    parser.add_argument("--profile",
                        action="store_true", dest="profile",
                        help="Enable werkzeug profiler")

    app.args = parser.parse_args()

    # If the user selects the profiling option, then we need
    # to do a little extra setup
    if app.args.profile:
        from werkzeug.contrib.profiler import ProfilerMiddleware

        app.config['PROFILE'] = True
        app.wsgi_app = ProfilerMiddleware(app.wsgi_app,
                                          restrictions=[30])
        app.args.debug = True
