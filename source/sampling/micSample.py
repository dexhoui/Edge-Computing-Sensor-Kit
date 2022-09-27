import sys
import datetime
import micDriver as au

audio_path = "../dataset/rawdata/audio/"
if sys.argv[1] == 'open':
    audio_path = audio_path +"open/"
elif sys.argv[1] == 'close':
    audio_path = audio_path + "close/"
elif sys.argv[1] == 'rotate':
    audio_path = audio_path + "rotate/"
elif sys.argv[1] == 'left':
    audio_path = audio_path + "left/"
elif sys.argv[1] == 'right':
    audio_path = audio_path + "right/"
elif sys.argv[1] == 'bottom':
    audio_path = audio_path + "bottom/"
elif sys.argv[1] == 'mr_bottom':
    audio_path = audio_path + "mr_bottom/"
elif sys.argv[1] == 'mr_left':
    audio_path = audio_path + "mr_left/"
elif sys.argv[1] == 'mr_right':
    audio_path = audio_path + "mr_right/"


if __name__ == "__main__":
    au.sound_collect(audio_path, 10)