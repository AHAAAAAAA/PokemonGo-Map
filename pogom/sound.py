import wave
import pyaudio
import threading

from pogom.utils import get_args

args = get_args()
is_playing = False

def play():
    global is_playing
    if args.play_sound and not is_playing:
        my_thread = threading.Thread(target=play_audio)
        my_thread.start()

def play_audio():
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
