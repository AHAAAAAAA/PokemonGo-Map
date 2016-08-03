#!/bin/bash

# Name of coords file
coords="coords.txt"

# Webserver Location
initloc="Dallas, TX"
# Account name without numbers
pre="accountname"

# Variables
worker=0
acct1=0
numacct=5
pass="yourpasshere"
auth="ptc"
st=5
sd=4
ld=1
directory='/path/to/your/runserver/directory/'

# Check to see if supervisor folder/subfolder exists if not make it
if [ ! -d ~/supervisor ]; then
  mkdir -p supervisor/procs.d
fi

# Copy supervisor files to ~/supervisor
if [ ! -f ~/supervisor/supervisord.conf ]; then
  cp supervisord.conf ~/supervisor/supervisord.conf
  sed -i "s,DIRECTORY,$directory," "$HOME/supervisor/supervisord.conf"
fi

if [ ! -f ~/supervisor/template.ini ]; then
  cp template.ini ~/supervisor/template.ini
fi

# Change Directory to ~/supervisor
cd "$HOME/supervisor" || exit 1

# Cleaning up directory
rm -f procs.d/*.ini

# Epicly complex loop
while read -r line; do
  ((worker++))
  printf -v n %02d $worker
  cp template.ini "procs.d/worker_$n.ini"
  user=$(for (( i = 1; i <= numacct; i++ )) do
           echo -n "-u ACCT$i "
         done)
  sed -i "s/WRK/$n/" "procs.d/worker_$n.ini"
  sed -i "s/LOC/$line/" "procs.d/worker_$n.ini"
  sed -i "s/USER/$user/" "procs.d/worker_$n.ini"
  sed -i "s/AUTH/$auth/" "procs.d/worker_$n.ini"
  sed -i "s/PASS/$pass/" "procs.d/worker_$n.ini"
  sed -i "s/ST/$st/" "procs.d/worker_$n.ini"
  sed -i "s/LD/$ld/" "procs.d/worker_$n.ini"
  sed -i "s/SD/$sd/" "procs.d/worker_$n.ini"
  sed -i "s,DIRECTORY,$directory," "procs.d/worker_$n.ini"
  for (( i = 1; i <= numacct; i++ )) do
    sed -i "s/ACCT$i/$pre$((acct1+i))/" "procs.d/worker_$n.ini"
  done
  ((acct1+=numacct))
done < $coords

cp supervisord.conf ~/supervisor/supervisord.conf
sed -i "s,DIRECTORY,$directory," "$HOME/supervisor/supervisord.conf"
sed -i "s/LOC/$initloc/" "$HOME/supervisor/supervisord.conf"
