@echo off
C:\Python27\python get-pip.py
cd ..
C:\Python27\Scripts\pip install -r requirements.txt
C:\Python27\Scripts\pip install -r requirements.txt --upgrade
rename credentials.example.json credentials.json
set /p API= Enter your Google API key here:

    (
    echo {
    echo "gmaps_key" : "%API%"
    echo }
    ) > credentials.json