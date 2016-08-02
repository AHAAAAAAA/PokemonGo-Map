## Setting up

**Note:** This guide runs on Windows with Python and Git installed.

First, make a copy of [this Google Sheets page](https://docs.google.com/spreadsheets/d/1Uh4VITpCciSy8pRh9I7OZuNiM-LizyBJcU7WR8oi7yY/edit#gid=263691484). We'll come back to that later.

Now open a Terminal and clone the develop branch to a local directory:

```
git clone -b develop https://github.com/AHAAAAAAA/PokemonGo-Map.git
```

Go to Tools / Hex-Beehive-Generator:

```
cd PokemonGo-Map/Tools/Hex-Beehive-Generator/
```

Now generate coordinates with `location_generator.py`:

```
python location_generator.py -st stepsize -lp ringsize -lat yourstartinglathere -lon yourstartinglonghere  
```

For example:

```
python location_generator.py -st 5 -lp 4 -lat 39.949157 -lon -75.165297  
```

Now the terminal will output a list of coordinates. Copy this entire list of coordinates, and then head over to your saved copy of the Google Sheets page we made earlier.  

We are going to paste all of the coords you just copied, into the first section of colored spaces, starting with the Top Pink one (ctrl v will do it automagically!)  

Now, make a file named `beehive.bat` with the following content:

```  
:: Set PythonPath to where your Python is installed, Typically C:\Python27\Python.exe  
:: Set BranchPath to where you have the Pokemon Live Map folder  

SET PythonPath=  
SET BranchPath=  
SET Executable=runserver.py  

::GAPI is your google map api key  
::auth is the authentication service you are using. PTC or Google  
::Self explanatory, username of the chosen auth service  
::again.. do i need to explain? password of chosen auth  
::Threads default is 1, if you want more, change it here.. 1 is recommended until multithreading is fixed in windows.  
::locale is the language output in your terminal, default is EN (english)  


SET GAPI=  
SET auth=  
SET username=  
SET password=  
SET thread=-t 1  
SET locale=EN  


::kill all python processes  
taskkill /IM python.exe /F
echo Starting worker processes....


::title of this command window  
title Pokemon Go Map

::paste the second column of colors here, down to the last space of the color you wanted. Pink = 1 Leap, Purple - 2 Leaps, Blue = 3 Leaps, Green = 4 Leaps, and Yellow = 5 Leaps. The amount of workers required gets silly after 5 Leaps :P)  



::this part is the time it will pause till going back to the start again to restart the servers (edit the 1801 to change the delay in seconds)  

echo Waiting 30 minutes to restart all processes  
ping 127.0.0.1 -n 1801 > nul  

goto start  
pause  
```

Now that we have our .bat created, We need to adjust the Arguments section on the spreadsheet. If you used the command for location_generator.py with -st set to 10, you need to change each line in the spreadsheet to -st 10 as well.

Now, we are going to copy and paste the last column of the spreadsheet, based on colors, into the space above in the .bat file designated for the commands. Save the file, then double click the .bat to start the workers!