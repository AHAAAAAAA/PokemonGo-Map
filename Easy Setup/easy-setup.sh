if [ "$EUID" -ne 0 ]
  then echo "Please run as root. You can also do: sudo !!"
  exit
fi

apt-get install python python-pip
pip install -r requirements.txt
pip install -r requirements.txt --upgrade
echo -n "Enter your Google API key here:"

read api

echo '{' >> ../config/credentials.json
echo "gmaps_key : $api" >> ../config/credentials.json
echo '}' >> ../config/credentials.json

echo All done!
sleep 5
