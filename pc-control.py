import sys

from google.cloud import speech
import speech_recognition as rec
import os

global comm
comm = -1
global recorded
global audio
global response
run = 0
state_machine = 0

curr_path = os.getcwd()
commands_dict = {"exit": 0, "help": 1, "go to": 2, "list all": 3, "make folder": 4, "current path": 5}
config = speech.RecognitionConfig(sample_rate_hertz=44100, enable_automatic_punctuation=True, language_code='en-US')
try:
    client = speech.SpeechClient.from_service_account_json('pc-ctrl-key.json')
    run = 1
except FileNotFoundError:
    print("~Failed to read google account json~")
    sys.exit()


def record_data():
    global recorded
    with rec.Microphone() as source:
        print("Listening...\n", end="")
        recorded = rec.Recognizer().listen(source)
    convert_to_wav()


def convert_to_wav():
    global audio
    recorded_wav = rec.AudioData.get_wav_data(recorded)
    audio = speech.RecognitionAudio(content=recorded_wav)


def list_all_comm():
    print(f'\033[93m' + "~List all~" + '\033[0m')
    print("Current folder: {}".format(curr_path))
    print("Contains: {}".format(os.listdir()))


def get_response():
    global response
    try:
        received_response = client.recognize(config=config, audio=audio)
    except:
        print("Failed get the response")
        sys.exit()
    try:
        response = ("{}".format(received_response.results[0].alternatives[0].transcript)).lower().rstrip("!.?")
    except IndexError:
        print("Empty message")
        return
    print(f'\033[92m' + response + '\033[0m')


def recognize_comm():
    global response
    global comm
    if response in commands_dict.keys():
        comm = commands_dict.get(response)
    else:
        print("Sorry, can't do that")
        comm = -1
        return


def go_to_comm():
    global curr_path
    global response
    global comm
    print(f'\033[93m' + "~GO TO MODE~" + '\033[0m')
    print("Current path: {}".format(curr_path))
    record_data()
    get_response()
    try:
        if os.path.exists(os.path.join(curr_path, response)):
            curr_path = os.path.join(curr_path, response)
            print("Going to {}".format(curr_path))
            os.chdir(curr_path)
        else:
            print("Sorry directory doesn't exist")
    except Exception as e:
        print(e)


def print_help():
    print(f'\033[93m' + "~HELP~"'\033[0m')
    help_string = "Available commands: "
    for command in commands_dict:
        help_string += command + ', '
    print(f'\033[93m' + help_string.rstrip(", ") + '\033[0m')


def execute_comm():
    global comm
    if comm == 0:
        print("Exiting...")
        sys.exit()
    elif comm == 1:
        print_help()
        return
    elif comm == 2:
        go_to_comm()
        return
    elif comm == 3:
        list_all_comm()
        return


while run == 1:
    record_data()
    get_response()
    recognize_comm()
    execute_comm()
