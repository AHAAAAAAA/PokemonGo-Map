from .utils import get_pokemon_name
from pogom.utils import get_args
import datetime

args = get_args()
#temporarily disabling because -o and -i is removed from 51f651228c00a96b86f5c38d1a2d53b32e5d9862
#IGNORE = None
#ONLY = None
#if args.ignore:
#    IGNORE =  [i.lower().strip() for i in args.ignore.split(',')]
#elif args.only:
#    ONLY = [i.lower().strip() for i in args.only.split(',')]

def pokeData(id,lat,lng,despawntime):
    if args.datatext:
        pokemon_name = get_pokemon_name(id).lower()
        pokemon_id = str(id)
        data = True
        if data:
            spawntime = datetime.datetime.now() - datetime.timedelta(seconds=(900 - despawntime))
            desptime = datetime.datetime.now() + datetime.timedelta(seconds=despawntime)
            datafile = args.datatext
            with open(datafile, "a") as myfile:
                myfile.write("%s,%s,%s,%s,%s,%s,%s\n" % (pokemon_name.encode('utf-8').title(), lat, lng, spawntime.strftime("%H:%M"), spawntime.strftime("%a"), spawntime.strftime("%b %d,%Y"), desptime.strftime("%H:%M")))
            def uniquelines(lineslist):
                unique = {}
                result = []
                for item in lineslist:
                    if item.strip() in unique: continue
                    unique[item.strip()] = 1
                    result.append(item)
                return result
            file1 = open(datafile,"r")
            filelines = file1.readlines()
            file1.close()
            output = open(datafile,"w")
            output.writelines(uniquelines(filelines))
            output.close()

def printPokemon(id,lat,lng,itime):
    if args.display_in_console:
        pokemon_name = get_pokemon_name(id).lower()
        pokemon_id = str(id)
        doPrint = True
        #if args.ignore:
        #    if pokemon_name in IGNORE or pokemon_id in IGNORE:
        #        doPrint = False
        #elif args.only:
        #    if pokemon_name not in ONLY and pokemon_id not in ONLY:
        #        doPrint = False
        if doPrint:
            timeLeft = itime-datetime.datetime.utcnow()
            print "======================================\n Name: %s\n Coord: (%f,%f)\n ID: %s \n Remaining Time: %s\n======================================" % (
                pokemon_name.encode('utf-8'),lat,lng,pokemon_id,str(timeLeft))
