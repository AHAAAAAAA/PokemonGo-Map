from .utils import get_pokemon_rarity, get_pokemon_name
from pogom.utils import get_args
from datetime import datetime

args = get_args()
#temporarily disabling because -o and -i is removed from 51f651228c00a96b86f5c38d1a2d53b32e5d9862
#IGNORE = None
#ONLY = None
#if args.ignore:
#    IGNORE =  [i.lower().strip() for i in args.ignore.split(',')]
#elif args.only:
#    ONLY = [i.lower().strip() for i in args.only.split(',')]


def printPokemon(id,lat,lng,itime):
    if args.display_in_console:
        pokemon_name = get_pokemon_name(id).lower()
        pokemon_rarity = get_pokemon_rarity(id).lower()
        pokemon_id = str(id)
        doPrint = True
        #if args.ignore:
        #    if pokemon_name in IGNORE or pokemon_id in IGNORE:
        #        doPrint = False
        #elif args.only:
        #    if pokemon_name not in ONLY and pokemon_id not in ONLY:
        #        doPrint = False
        if doPrint:
            timeLeft = itime-datetime.utcnow()
            print "======================================\n Name: %s\n Rarity: %s\n Coord: (%f,%f)\n ID: %s \n Remaining Time: %s\n======================================" % (
                pokemon_name.encode('utf-8'), pokemon_rarity.encode('utf-8'),lat,lng,pokemon_id,str(timeLeft))
