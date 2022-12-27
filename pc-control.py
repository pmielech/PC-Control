import sys
from google.cloud import speech
import speech_recognition as rec
import os
import shlex

comm = -1
empty_message = 0
global recorded
global audio
global response
run = 0
state_machine = 0
folder_container = ""
go_to_id = 0
dev_input = sys.argv

curr_path = os.getcwd()
help_dict = {"Help": "Prints this additional information below.",
             "Go to": "Enables GO TO MODE. This command allows user to move between directories in current path.\n"
                      "Command at launch prints folder content."
                      "First recorded words, after waking this command, will be recognised as program direction.\n"
                      "Warning! Currently, the program supports a maximum directory name consisting of two words",
             "List all": "Prints out the content of the current path, where the user is located.",
             "Make folder": "Enables MAKE FOLDER mode. This command allows user to create directory in the current "
                            "path.\n"
                            "First recorded words, after waking this command, will be recognised as program direction.",
             "Where am I": "Prints the user currents path and prints content of the current directory.",
             "Go back": "The command moves up one directory.",
             "Exit": "Command closes the program"
             }
command_dict = {"exit": 0, "help": 1, "go to": 2, "list all": 3, "make folder": 4, "where am i": 5, "go back": 6,
                "open file": 7,
                }
config = speech.RecognitionConfig(enable_automatic_punctuation=True, language_code='en-US')
try:
    client = speech.SpeechClient.from_service_account_json('pc-ctrl-key.json')
    run = 1
except FileNotFoundError:
    print("~Failed to read google account json~")
    sys.exit()


def open_default():
    global folder_container
    global curr_path
    global response
    global comm
    file_id = 0
    ready_to_go = 0
    print(f'\033[93m' + "~Open file~" + '\033[0m')
    list_all_comm(False)
    record_data()
    get_response()
    response = response.strip().split()
    try:
        for idx, file in enumerate(folder_container):
            if len(response) > 1:
                if response[0] in file.lower():
                    if response[1] in file.lower():
                        ready_to_go = 1
                        file_id = idx
                        break
            elif len(response) == 1:
                if response[0] in file.lower():
                    ready_to_go = 1
                    file_id = idx
                    break
            else:
                print("Sorry, can't find that file")
                return
        if ready_to_go != 0:
            os.system("open " + shlex.quote(folder_container[file_id]))
            return
        print("Sorry can't find that file in this directory")
        return
    except Exception as e:
        print(e)
        return


def record_data():
    global recorded
    with rec.Microphone() as source:
        print('Listening...', end=' ')
        recorded = rec.Recognizer().listen(source)
    convert_to_wav()


def convert_to_wav():
    global audio
    recorded_wav = rec.AudioData.get_wav_data(recorded)
    audio = speech.RecognitionAudio(content=recorded_wav)


def list_all_comm(mode: bool):
    global folder_container
    folder_container = os.listdir()
    if mode:
        print(f'\033[93m' + "~LIST ALL~" + '\033[0m')
    print("Current folder: {}".format(curr_path))
    print("Contains: {}".format(folder_container))


def get_response():
    global response
    global empty_message
    try:
        received_response = client.recognize(config=config, audio=audio)
    except Exception as e:
        print(e)
        sys.exit()
    try:
        response = ("{}".format(received_response.results[0].alternatives[0].transcript)).lower().rstrip("!.?")
        empty_message = 0
    except IndexError:
        print("Empty message")
        empty_message = 1
        response = ""
        return
    print(f'\033[92m' + response + '\033[0m')


def convert_to_numeric():
    # TODO
    pass


def safe_word():
    # TODO
    pass


def current_directory_comm():
    print(f'\033[93m' + "~CURRENT DIRECTORY~" + '\033[0m')
    print(curr_path)


def recognize_comm():
    global response
    global comm
    global empty_message
    if empty_message == 1:
        return
    elif response in command_dict.keys():
        comm = command_dict.get(response)
    else:
        print("Sorry, can't do that")
        comm = -1
        return


def go_back_comm():
    global curr_path
    global response
    global comm
    print(f'\033[93m' + "~GO BACK~" + '\033[0m')
    try:
        os.chdir("..")
        print("Moved up one directory")
        curr_path = os.getcwd()
    except Exception as e:
        print("Can't change directory due to: ")
        print(e)
        return
    print("Current path: {}".format(curr_path))


def go_to_comm():
    global curr_path
    global response
    global comm
    global folder_container
    global go_to_id
    ready_to_go = 0
    print(f'\033[93m' + "~GO TO MODE~" + '\033[0m')
    print("Current path: {}".format(curr_path))
    list_all_comm(False)
    if len(dev_input) > 1:
        response = "test path"
    else:
        record_data()
        get_response()
    try:
        response = response.strip().split()
        for idx, file in enumerate(folder_container):
            if len(response) > 1:
                if response[0] in file.lower():
                    if response[1] in file.lower():
                        ready_to_go = 1
                        go_to_id = idx
                        break
            elif len(response) == 1:
                if response[0] in file.lower():
                    ready_to_go = 1
                    go_to_id = idx
                    break
            else:
                print("Sorry, can't find that folder")
                return
        if ready_to_go == 0:
            print("Sorry, can't find that folder.")
            return
        else:
            if os.path.exists(os.path.join(curr_path, folder_container[go_to_id])):
                curr_path = os.path.join(curr_path, folder_container[go_to_id])
                print("Going to {}".format(curr_path))
                os.chdir(curr_path)
            else:
                print("Sorry directory doesn't exist")
    except Exception as e:
        print(e)


def make_folder_comm():
    global curr_path
    global response
    global comm
    print(f'\033[93m' + "~MAKE FOLDER~"'\033[0m')
    print("Current path: {}".format(curr_path))
    print("Contains: {}".format(os.listdir()))
    record_data()
    get_response()
    try:
        if os.path.exists(os.path.join(curr_path, response)):
            print("Path already exists.")
            return
        else:
            temp_path = os.path.join(curr_path, response)
            os.mkdir(temp_path)
            print("Directory created")
            print("Current path contains: {}".format(os.listdir()))

    except Exception as e:
        print(e)
        return


def print_help():
    print(f'\033[93m' + "~HELP~"'\033[0m')
    help_string = "Available commands: "
    print(f'\033[93m' + help_string.rstrip(", ") + '\033[0m')
    for command in help_dict:
        print(f'\033[93m' + "{}: {}\n".format(command, help_dict.get(command)) + '\033[0m')


def execute_comm():
    global comm
    global empty_message
    if empty_message == 1 or comm == -1:
        return
    elif comm == 0:
        print("Exiting...")
        sys.exit()
    elif comm == 1:
        print_help()
        return
    elif comm == 2:
        go_to_comm()
        return
    elif comm == 3:
        list_all_comm(True)
        return
    elif comm == 4:
        make_folder_comm()
        return
    elif comm == 5:
        current_directory_comm()
        return
    elif comm == 6:
        go_back_comm()
        return
    elif comm == 7:
        open_default()
        return
    else:
        print("Can't recognize, repeat the command.")
        return


while run == 1:
    if len(dev_input) > 1:
        comm = 2
    else:
        record_data()
        get_response()
        recognize_comm()

    execute_comm()
