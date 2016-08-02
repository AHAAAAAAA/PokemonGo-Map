# Command Line Usage and Arguments


```
runserver.py [-h] [-se] [-a AUTH_SERVICE] [-u USERNAME] [-p PASSWORD]
                     [-l LOCATION] [-c] [-fl] [-k GMAPS_KEY]
                     [-H HOST] [-P PORT] [-m] [-ns] [-C]
                     [-st STEP_LIMIT] [-sd SCAN_DELAY] [-np] [-ng] [-nk]
                     [-dc] [-L LOCALE] [-d] [-D DB] [-t NUM_THREADS]
```

## Arguments

`-h` - shows help message.  
`-se` - Reads config.ini (deprecated in new versions)
### Authentication
`-a AUTH_SERVICE` - Auth Service (ptc or google).  
`-u USERNAME` - Username (Email if using google).  
`-p PASSWORD` - Password.  

### Location
`-l LOCATION` - Location, can be an address or coordinates.  
`-c` - Coordinates transformer for China.  
`-fl` - Toggles the search bar, uses a 'fixed' location.  
`-k` GMAPS_KEY - Google Maps Javascript API Key.  

### Server
`-H HOST` - Set web server listening host.  
`-P PORT` - Set web server listening port.  
`-m` - Mock mode. Starts the web server but not the background thread.  
`-ns` - No-Server Mode. Starts the searcher but not the Webserver.  
`-C` - Enable CORS on web server.  

### Search settings
`-st STEP_LIMIT` - Steps, the amount of 'steps' the scan will make.  
`-sd SCAN_DELAY` - Time delay before beginning new scan.  
`-np` - Disables Pokemon from the map (including parsing them into local db).  
`-ng` - Disables Gyms from the map (including parsing them into local db).  
`-nk` - Disables PokeStops from the map (including parsing them into local db).  

### Other
`-dc` - Display Found Pokemon in Console.  
`-L LOCALE` - Locale for Pokemon names: default en, checklocale folder for more options.  
`-d` - Debug Mode.  
`-D DB`  - Change the name of the database file, default is `pogom.db`.  
`-t` - Number of threads, default is set to 1.  