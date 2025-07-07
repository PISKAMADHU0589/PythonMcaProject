import pyttsx3
import threading
import speech_recognition as sr
import datetime as dt
import time
import os
import cv2
import random
import wikipedia
from requests import get
import webbrowser
import pywhatkit as kit
import smtplib
import pyjokes
import pyautogui
import requests
from email.mime.multipart import MIMEMultipart, MIMEBase
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import re
import multiprocessing
from playsound import playsound
import winsound

camera_active = False 
# =========================================================
# Helper: parse 12‑hour spoken time to 24‑hour (hh, mm)
# =========================================================

def parse_time_input(time_str: str):
    s = time_str.lower().replace('.', '').replace(' ', '')
    m = re.match(r'^(\d{1,2})(:?)(\d{0,2})(am|pm)$', s)
    if not m:
        return None
    h12 = int(m.group(1))
    mnt = int(m.group(3)) if m.group(3) else 0
    mer = m.group(4)
    if not (1 <= h12 <= 12 and 0 <= mnt <= 59):
        return None
    h24 = h12 % 12 + (12 if mer == 'pm' else 0)
    return h24, mnt

# =========================================================
# Speech engine
# =========================================================
engine = pyttsx3.init('sapi5')
engine.setProperty('voice', engine.getProperty('voices')[1].id)

def speak(txt: str):
    print(txt)
    engine.say(txt)
    engine.runAndWait()
def news():
    main_url="http://newsapi.org/v2/top-headlines?sources=techcrunch&apiKey=9f97d37bce94460d9c60a4d1fe478b63"
    main_page=requests.get(main_url).json()
    #print mainpage
    articles=main_page["articles"]
    head=[]
    day=["first","second","third","fourth","fifth","sixth","seventh","eighth","ninth","tenth"]
    for ar in articles:
        head.append(ar["title"])
    for i in range(len(day)):
        #print(f"today's {day[i]} news is:" , head[i])
        speak(f"today's {day[i]} news is:  {head[i]}")

# =========================================================
# Voice capture
# =========================================================

def takecommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print('Listening...')  # <-- visibly shows the listening prompt
        r.pause_threshold = 1
        audio = r.listen(source, timeout=2, phrase_time_limit=5)
    try:
        query = r.recognize_google(audio, language='en-in')
        print(f'user said: {query}')
        return query.lower()
    except Exception:
        speak('Say that again please …')
        return 'none'

# =========================================================
# Alarm worker (must be defined before use!)
# =========================================================

def alarm_worker(target_ts: float):
    import time, os, random, winsound; from playsound import playsound; import pyttsx3
    time.sleep(max(0, target_ts - time.time()))
    eng = pyttsx3.init('sapi5'); eng.say("Wake up sir! It's time!"); eng.runAndWait()

    music_dir = 'D:\\songs'
    track = None
    if os.path.isdir(music_dir):
        for f in os.listdir(music_dir):
            if 'gangsta' in f.lower() and f.lower().endswith(('.mp3', '.wav')):
                track = os.path.join(music_dir, f); break
        if not track:
            songs = [os.path.join(music_dir, f) for f in os.listdir(music_dir) if f.lower().endswith(('.mp3', '.wav'))]
            if songs:
                track = random.choice(songs)
    if track:
        try:
            playsound(track)
        except Exception:
            for _ in range(3): winsound.Beep(440, 800)
    else:
        for _ in range(3): winsound.Beep(440, 800)

# =========================================================
# Misc helpers
# =========================================================

def open_camera():
    global camera_active
    camera_active = True
    cap = cv2.VideoCapture(0)
    while camera_active:
        ret, img = cap.read()
        if ret:
            cv2.imshow("Webcam", img)
            if cv2.waitKey(1) == 27:
                break
    cap.release()
    cv2.destroyAllWindows()
    camera_active = False


def wish():
    hr = dt.datetime.now().hour
    greet = 'Good morning' if hr < 12 else 'Good afternoon' if hr < 18 else 'Good evening'
    speak(f'{greet}, sir! I am Jarvis. I am here to help you.')
# =========================================================
# Wake-up Listener
# =========================================================

def listen_for_wake_word():
    while True:
        print("Waiting for wake word 'wake up jarvis'...")
        query = takecommand()
        if "wake up jarvis" in query:
            wish()
            main_loop()


# =========================================================
# Main loop
# =========================================================
def main_loop():
    global camera_active
    exit_phrases = ['no thanks you can sleep', 'no thanks', 'you can sleep', 'exit', 'quit']
    while True:
        query = takecommand()
        if query == 'none':
            continue

        while True:  # inner loop processes follow‑ups without restarting mic prompt chain
            handled = False

            # ---------- Exit check ----------
            if any(p in query for p in exit_phrases):
                speak('Thanks for using me sir, have a good day')
                quit()

            # ---------- Alarm ----------
            if 'set alarm' in query:
                speak('At what time should I set the alarm?')
                t_raw = takecommand()
                tm = parse_time_input(t_raw)
                if tm:
                    h, m = tm
                    now = dt.datetime.now()
                    tgt = now.replace(hour=h, minute=m, second=0, microsecond=0)
                    if tgt <= now:
                        tgt += dt.timedelta(days=1)
                    multiprocessing.Process(target=alarm_worker, args=(tgt.timestamp(),), daemon=False).start()
                    speak(f'Alarm set for {tgt.strftime("%I:%M %p")}')
                else:
                    speak('Time not understood.')
                handled = True

            # ---------- Notepad ----------
            elif 'open notepad' in query:
                os.startfile('C:\\Windows\\notepad.exe'); handled = True
            elif "open command prompt" in query:
             os.system("start cmd")
            elif "open camera" in query:
                if not camera_active:
                    threading.Thread(target=open_camera).start()
                    speak("Camera opened.")
                else:
                    speak("Camera is already running.")
                handled = True

            elif "close camera" in query:
                if camera_active:
                    camera_active = False
                    speak("Camera is now closed.")
                else:
                    speak("Camera is not currently open.")
                handled = True


            elif "tell me news" in query:
                speak("please wait sir, fetching the latest news")
                news()


            elif 'close notepad' in query:
                os.system('taskkill /f /im notepad.exe'); speak('okay sir closing notepad'); handled = True
            elif "send email" in query:
                speak("To whom should I send the email? Please say the username or full email address.")
                to_input = takecommand().lower().replace(" ", "")  # Remove spaces

        # Append @gmail.com if not present
                if "@" not in to_input:
                    to_email = to_input + "@gmail.com"
                else:
                    to_email = to_input

                speak(f"Email will be sent to {to_email}. What should I say in the email?")
                content = takecommand().lower()

        # Optional: Check if user wants to attach a file
                speak("Do you want to attach a file? Say yes or no.")
                attach_reply = takecommand().lower()

                msg = MIMEMultipart()
                msg["From"] = "madhupiska1002@gmail.com"
                msg["To"] = to_email
                msg["Subject"] = "Voice Email from Jarvis"
                msg.attach(MIMEText(content, "plain"))

                if "yes" in attach_reply:
                    speak("Please enter the full file path in the shell.")
                    file_location = input("Enter file path here: ")
                    try:
                        filename = os.path.basename(file_location)
                        attachment = open(file_location, "rb")
                        part = MIMEBase("application", "octet-stream")
                        part.set_payload(attachment.read())
                        encoders.encode_base64(part)
                        part.add_header("Content-Disposition", f"attachment; filename={filename}")
                        msg.attach(part)
                    except Exception as e:
                        speak("File attachment failed. Sending email without attachment.")

                try:
                    server = smtplib.SMTP("smtp.gmail.com", 587)
                    server.starttls()
                    server.login("madhupiska1002@gmail.com", "qjpk gqcp kyrl rcyw")  # Use your app password
                    server.sendmail("madhupiska1002@gmail.com", to_email, msg.as_string())
                    server.quit()
                    speak(f"Email has been sent to {to_email}")
                except Exception as e:
                    speak("Sorry, I could not send the email.")



            # ---------- WhatsApp ----------
            elif 'send whatsapp message' in query:
                speak('Please say the 10‑digit mobile number.'); num = ''.join(filter(str.isdigit, takecommand()))
                if len(num) == 10:
                    phone = '+91' + num
                    speak('What should I say?'); msg = takecommand()
                    speak('Sending your WhatsApp message now...')
                    try:
                        kit.sendwhatmsg_instantly(phone, msg, wait_time=10, tab_close=True)
                        time.sleep(10)
                        speak('WhatsApp message sent successfully!')
                    except Exception:
                        speak('Failed to send the WhatsApp message.')
                else:
                    speak('Invalid number.')
                handled = True
            elif "open whatsapp web" in query:
                webbrowser.open("https://web.whatsapp.com/")
            elif "wikipedia" in query:
                speak("searching wikipedia...")
                query = query.replace("according to wikipedia", "").strip()
                results = wikipedia.summary(query, sentences=2)
                speak("According to wikipedia")
                speak(results)
                print(results)

            elif "open github" in query:
                webbrowser.open("www.github.com")
            elif "open google" in query:
                speak("what should i search on google sir")
                cm=takecommand().lower()
                webbrowser.open(f"{cm}")    
            elif "play my favourite song on youtube" in query:
                kit.playonyt("star boy")

            # ---------- Additional commands (music, IP, jokes, etc.) ----------
            elif 'play music' in query:
                music_dir = 'D:\\songs'
                if os.path.isdir(music_dir):
                    songs = os.listdir(music_dir)
                    if songs:
                        os.startfile(os.path.join(music_dir, random.choice(songs)))
                        handled = True
            elif 'what is my ip' in query or 'what is my ip address' in query:
                try:
                    speak(f'{get("https://api.ipify.org").text} is your IP Address')
                except Exception:
                    speak('Unable to fetch IP.')
                handled = True
            elif 'tell me a joke' in query:
                speak(pyjokes.get_joke()); handled = True
            elif 'open youtube' in query:
                webbrowser.open('https://www.youtube.com'); handled = True
            elif 'open instagram' in query:
                webbrowser.open('https://www.instagram.com'); handled = True
            # ... add any other command blocks needed ...
            elif "switch the window" in query:
                pyautogui.keyDown("alt")
                pyautogui.press("tab")
                time.sleep(1)
                pyautogui.keyUp("alt")
            elif "sleep the system" in query:
                os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
            elif "restart the system" in query:
                os.system("shutdown/r/t/5")
            elif "shutdown the system" in query:
                os.system("shutdown/s/t/5")
            if handled:
                speak('Do you have any other work?')
                query = takecommand()
                if query == 'none':
                    break  # return to outer loop for fresh prompt
                continue  # inner loop processes the new query immediately
            else:
                break  # command not matched; re‑enter outer loop to listen a new command 
if __name__ == '__main__':
    multiprocessing.freeze_support()
    listen_for_wake_word()
