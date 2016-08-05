# Using supervisord

## Assuming:

* You are running on Linux
* You have installed [supervisord](http://supervisord.org/)
* You have seen a shell prompt at least a few times in your life
* You have configured your stuff properly in `config.ini`
* You understand worker separation
* You can tie your own shoelaces

## The good stuff

Create directory `~/supervisor`, and `~/supervisor/procs.d`

Create file `~/supervisor/supervisord.conf`:

	; Sample supervisor config file.
	;
	; For more information on the config file, please see:
	; http://supervisord.org/configuration.html
	;
	; Notes:
	;  - Shell expansion ("~" or "$HOME") is not supported.  Environment
	;    variables can be expanded using this syntax: "%(ENV_HOME)s".
	;  - Comments must have a leading space: "a=b ;comment" not "a=b;comment".

	[unix_http_server]
	file=/tmp/supervisor.sock   ; (the path to the socket file)
	;chmod=0700                 ; socket file mode (default 0700)
	;chown=nobody:nogroup       ; socket file uid:gid owner
	;username=user              ; (default is no username (open server))
	;password=123               ; (default is no password (open server))

	;[inet_http_server]         ; inet (TCP) server disabled by default
	;port=127.0.0.1:9001		; (ip_address:port specifier, *:port for all iface)
	;username=user              ; (default is no username (open server))
	;password=123               ; (default is no password (open server))

	[supervisord]
	logfile=/tmp/supervisord.log ; (main log file;default $CWD/supervisord.log)
	logfile_maxbytes=50MB        ; (max main logfile bytes b4 rotation;default 50MB)
	logfile_backups=10           ; (num of main logfile rotation backups;default 10)
	loglevel=info                ; (log level;default info; others: debug,warn,trace)
	pidfile=/tmp/supervisord.pid ; (supervisord pidfile;default supervisord.pid)
	nodaemon=false               ; (start in foreground if true;default false)
	minfds=1024                  ; (min. avail startup file descriptors;default 1024)
	minprocs=200                 ; (min. avail process descriptors;default 200)
	;umask=022                   ; (process file creation umask;default 022)
	user=root                    ; (default is current user, required if root)
	;identifier=supervisor       ; (supervisord identifier, default is 'supervisor')
	directory=/opt/pogo/		 ; (default is not to cd during start)
	;nocleanup=true              ; (don't clean up tempfiles at start;default false)
	;childlogdir=/tmp            ; ('AUTO' child log dir, default $TEMP)
	;environment=KEY="value"     ; (key value pairs to add to environment)
	;strip_ansi=false            ; (strip ansi escape codes in logs; def. false)

	; the below section must remain in the config file for RPC
	; (supervisorctl/web interface) to work, additional interfaces may be
	; added by defining them in separate rpcinterface: sections
	[rpcinterface:supervisor]
	supervisor.rpcinterface_factory = supervisor.rpcinterface:make_main_rpcinterface

	[supervisorctl]
	serverurl=unix:///tmp/supervisor.sock ; use a unix:// URL  for a unix socket
	;serverurl=http://127.0.0.1:9001 ; use an http:// url to specify an inet socket
	;username=user               ; should be same as http_username if set
	;password=123                ; should be same as http_password if set
	;prompt=mysupervisor         ; cmd line prompt (default "supervisor")
	;history_file=~/.sc_history  ; use readline history if available

	; The below sample program section shows all possible program subsection values,
	; create one or more 'real' program: sections to be able to control them under
	; supervisor.

	;[program:theprogramname]
	;command=/bin/cat              ; the program (relative uses PATH, can take args)
	;process_name=%(program_name)s ; process_name expr (default %(program_name)s)
	;numprocs=1                    ; number of processes copies to start (def 1)
	;directory=/tmp                ; directory to cwd to before exec (def no cwd)
	;umask=022                     ; umask for process (default None)
	;priority=999                  ; the relative start priority (default 999)
	;autostart=true                ; start at supervisord start (default: true)
	;startsecs=1                   ; # of secs prog must stay up to be running (def. 1)
	;startretries=3                ; max # of serial start failures when starting (default 3)
	;autorestart=unexpected        ; when to restart if exited after running (def: unexpected)
	;exitcodes=0,2                 ; 'expected' exit codes used with autorestart (default 0,2)
	;stopsignal=QUIT               ; signal used to kill process (default TERM)
	;stopwaitsecs=10               ; max num secs to wait b4 SIGKILL (default 10)
	;stopasgroup=false             ; send stop signal to the UNIX process group (default false)
	;killasgroup=false             ; SIGKILL the UNIX process group (def false)
	;user=chrism                   ; setuid to this UNIX account to run the program
	;redirect_stderr=true          ; redirect proc stderr to stdout (default false)
	;stdout_logfile=/a/path        ; stdout log path, NONE for none; default AUTO
	;stdout_logfile_maxbytes=1MB   ; max # logfile bytes b4 rotation (default 50MB)
	;stdout_logfile_backups=10     ; # of stdout logfile backups (default 10)
	;stdout_capture_maxbytes=1MB   ; number of bytes in 'capturemode' (default 0)
	;stdout_events_enabled=false   ; emit events on stdout writes (default false)
	;stderr_logfile=/a/path        ; stderr log path, NONE for none; default AUTO
	;stderr_logfile_maxbytes=1MB   ; max # logfile bytes b4 rotation (default 50MB)
	;stderr_logfile_backups=10     ; # of stderr logfile backups (default 10)
	;stderr_capture_maxbytes=1MB   ; number of bytes in 'capturemode' (default 0)
	;stderr_events_enabled=false   ; emit events on stderr writes (default false)
	;environment=A="1",B="2"       ; process environment additions (def no adds)
	;serverurl=AUTO                ; override serverurl computation (childutils)

	; The below sample eventlistener section shows all possible
	; eventlistener subsection values, create one or more 'real'
	; eventlistener: sections to be able to handle event notifications
	; sent by supervisor.

	;[eventlistener:theeventlistenername]
	;command=/bin/eventlistener    ; the program (relative uses PATH, can take args)
	;process_name=%(program_name)s ; process_name expr (default %(program_name)s)
	;numprocs=1                    ; number of processes copies to start (def 1)
	;events=EVENT                  ; event notif. types to subscribe to (req'd)
	;buffer_size=10                ; event buffer queue size (default 10)
	;directory=/tmp                ; directory to cwd to before exec (def no cwd)
	;umask=022                     ; umask for process (default None)
	;priority=-1                   ; the relative start priority (default -1)
	;autostart=true                ; start at supervisord start (default: true)
	;startsecs=1                   ; # of secs prog must stay up to be running (def. 1)
	;startretries=3                ; max # of serial start failures when starting (default 3)
	;autorestart=unexpected        ; autorestart if exited after running (def: unexpected)
	;exitcodes=0,2                 ; 'expected' exit codes used with autorestart (default 0,2)
	;stopsignal=QUIT               ; signal used to kill process (default TERM)
	;stopwaitsecs=10               ; max num secs to wait b4 SIGKILL (default 10)
	;stopasgroup=false             ; send stop signal to the UNIX process group (default false)
	;killasgroup=false             ; SIGKILL the UNIX process group (def false)
	;user=chrism                   ; setuid to this UNIX account to run the program
	;redirect_stderr=false         ; redirect_stderr=true is not allowed for eventlisteners
	;stdout_logfile=/a/path        ; stdout log path, NONE for none; default AUTO
	;stdout_logfile_maxbytes=1MB   ; max # logfile bytes b4 rotation (default 50MB)
	;stdout_logfile_backups=10     ; # of stdout logfile backups (default 10)
	;stdout_events_enabled=false   ; emit events on stdout writes (default false)
	;stderr_logfile=/a/path        ; stderr log path, NONE for none; default AUTO
	;stderr_logfile_maxbytes=1MB   ; max # logfile bytes b4 rotation (default 50MB)
	;stderr_logfile_backups=10     ; # of stderr logfile backups (default 10)
	;stderr_events_enabled=false   ; emit events on stderr writes (default false)
	;environment=A="1",B="2"       ; process environment additions
	;serverurl=AUTO                ; override serverurl computation (childutils)

	; The below sample group section shows all possible group values,
	; create one or more 'real' group: sections to create "heterogeneous"
	; process groups.

	;[group:thegroupname]
	;programs=progname1,progname2  ; each refers to 'x' in [program:x] definitions
	;priority=999                  ; the relative start priority (default 999)

	; The [include] section can just contain the "files" setting.  This
	; setting can list multiple files (separated by whitespace or
	; newlines).  It can also contain wildcards.  The filenames are
	; interpreted as relative to this file.  Included files *cannot*
	; include files themselves.

	[program:webserver]
	command=/usr/bin/python ./runserver.py -os -C -t 20 -l "INITIAL LOCATION" -fl
	process_name=webserver
	numprocs=1
	directory=/opt/pogo/
	startsec=15
	startretries=3
	autorestart=true
	stopwaitsecs=5
	stdout_logfile=/tmp/supervisor_webserver.log
	stderr_logfile=/tmp/supervisor_webserver.log

	[include]
	files = procs.d/*.ini

In this file, change `user=`, `directory=` and `command=` to reflect your username, directory where your `runserver.py` is stored, and change the LOCATION of your webserver thread.

Create file `~/supervisor/sample.ini`:

	[program:workerWRK]
	command=/usr/bin/python ./runserver.py -ns -l "LOC"
	process_name=worker_WRK
	numprocs=1
	directory=/opt/pogo/
	startsec=15
	startretries=3
	autorestart=true
	stopwaitsecs=5
	stdout_logfile=/tmp/supervisor_workerWRK.log
	stderr_logfile=/tmp/supervisor_workerWRK.log

In this file, change the `directory=` line to point to the directory where your script is stored.

Create file `~/supervisor/gen-workers.sh`:

	#!/bin/bash
	#cleaning up directory
	rm -f procs.d/*.ini
	WORKER=0
	while read LINE; do
	  WORKER=$((WORKER+1))
	  cp sample.ini procs.d/worker_$WORKER.ini
	  sed -i'' "s/WRK/$WORKER/" procs.d/worker_$WORKER.ini
	  sed -i'' "s/LOC/$LINE/" procs.d/worker_$WORKER.ini
	done < coords.txt

Create file `~/supervisor/coords.txt`:

	44.4908702, 26.0084664
	44.4652468, 26.0084664
	44.4396234, 26.0084664
	44.4140000, 26.0084664
	44.3883766, 26.0084664
	44.5036861, 26.0395188
	44.4780627, 26.0395188
	44.4524393, 26.0395188
	44.4268159, 26.0395188
	44.4011925, 26.0395188
	44.5165104, 26.0705790
	44.4908870, 26.0705790
	44.4652636, 26.0705790
	44.4396402, 26.0705790
	44.4140168, 26.0705790
	44.3883934, 26.0705790
	44.3627700, 26.0705790
	44.5293263, 26.1016451
	44.5037029, 26.1016451
	44.4780795, 26.1016451
	44.4524561, 26.1016451
	44.4268327, 26.1016451
	44.4012093, 26.1016451
	44.3755859, 26.1016451
	44.5165104, 26.1327183
	44.4908870, 26.1327183
	44.4652636, 26.1327183
	44.4396402, 26.1327183
	44.4140168, 26.1327183
	44.3883934, 26.1327183
	44.3627700, 26.1327183
	44.5036861, 26.1637714
	44.4780627, 26.1637714
	44.4524393, 26.1637714
	44.4268159, 26.1637714
	44.4011925, 26.1637714
	44.3755691, 26.1637714
	44.4908702, 26.1948309
	44.4652468, 26.1948309
	44.4396234, 26.1948309
	44.4140000, 26.1948309

***Don't be dumb, use your ACTUAL coordinates, ONE PER LINE, NO EMPTY LINES!***

Then run the gen-workers.sh script

    cd ~/supervisor/
    bash ./gen-workers.sh

You should now have a bunch of .ini files in `~/supervisor/procs.d/`

You can now do:

    cd ~/supervisor
    supervisord -c supervisor



