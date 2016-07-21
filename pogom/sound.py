import wave
import pyaudio
import threading

from pogom.utils import get_args
from .utils import get_pokemon_name

args = get_args()
is_playing = False

def play_audio(id):
    global is_playing
    if args.play_sound and not is_playing:
        pokemon_name = get_pokemon_name(id)
        pokemon_id = str(id)
        play = True
        if args.ignore:
            if pokemon_name in args.ignore or pokemon_id in args.ignore:
                play = False
        elif args.only:
            if pokemon_name not in args.only and pokemon_id not in args.only:
                play = False
        if play:
            my_thread = threading.Thread(target=play)
            my_thread.start()

def play():
    global is_playing
    chunk = 206
    wf = wave.open('a.wav', 'rb')
    p = pyaudio.PyAudio()
    stream = p.open(
        format = p.get_format_from_width(wf.getsampwidth()),
        channels = wf.getnchannels(),
        rate = wf.getframerate(),
        output = True)
    data = wf.readframes(chunk)
    while data != '':
        is_playing = True
        stream.write(data)
        data = wf.readframes(chunk)
    stream.stop_stream()
    stream.close()
    p.terminate()
    is_playing = False
