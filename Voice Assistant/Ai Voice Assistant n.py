#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pyttsx3
import speech_recognition as sr
import datetime
import webbrowser
import wikipedia
import os
import subprocess
import tkinter as tk
from tkinter import scrolledtext
import threading
import logging
import psutil
import requests
import pywhatkit as kit
import pyautogui
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
def speak(audio):
    logging.info(f"Assistant: {audio}")
    engine.say(audio)
    engine.runAndWait()

def greet():
    hour = int(datetime.datetime.now().hour)
    if hour >= 0 and hour < 12:
        speak("Good Morning!")
    elif hour >= 12 and hour < 18:
        speak("Good Afternoon!")
    else:
        speak("Good Evening!")
    speak("Welcome, I am your personal assistant")

def voice_command():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        log_text("Listening...")
        r.pause_threshold = 1
        audio = r.listen(source)
    try:
        log_text("Recognizing...")
        query = r.recognize_google(audio, language='en-in')
        log_text(f"User said: {query}\n")
    except sr.UnknownValueError:
        speak("Sorry, I did not understand that.")
        log_text("Sorry, I did not understand that.")
        return "None"
    except sr.RequestError:
        speak("Sorry, my speech service is down.")
        log_text("Sorry, my speech service is down.")
        return "None"
    return query.lower()

def get_weather(city):
    api_key = '13d6f372052b76fdc44bd6057ffb9dfc'
    base_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    response = requests.get(base_url)
    data = response.json()
    if data["cod"] != "404":
        weather_desc = data["weather"][0]["description"]
        temp = data["main"]["temp"]
        speak(f"The temperature in {city} is {temp} degrees Celsius with {weather_desc}.")
        log_text(f"Weather in {city}: {temp}°C, {weather_desc}")
    else:
        speak("City not found.")
        log_text("City not found.")

def set_alarm(alarm_time):
    try:
        speak("Setting an alarm.")
        os.startfile("ms-clock:")

        time.sleep(3)
        pyautogui.click(x=100, y=200)  
        time.sleep(1)

        pyautogui.typewrite(alarm_time, interval=0.25)

        pyautogui.press('enter')
        time.sleep(1)

        speak(f"Alarm set for {alarm_time}.")
        log_text(f"Alarm set for {alarm_time}")
    except Exception as e:
        speak("Sorry, I couldn't set the alarm.")
        log_text(f"Error setting alarm: {e}")

    pyautogui.click(x=100, y=200)  
    time.sleep(1)
    alarm_hour, alarm_minute, period = parse_time(alarm_time)

    hour_button = pyautogui.locateOnScreen('hour_button.png', confidence=0.8)
    if hour_button:
        pyautogui.click(hour_button)
        pyautogui.typewrite(alarm_hour)
    else:
        speak("Could not find the hour setting.")
        return

    minute_button = pyautogui.locateOnScreen('minute_button.png', confidence=0.8)
    if minute_button:
        pyautogui.click(minute_button)
        pyautogui.typewrite(alarm_minute)
    else:
        speak("Could not find the minute setting.")
        return

    period_button = pyautogui.locateOnScreen('period_button.png', confidence=0.8)
    if period_button:
        pyautogui.click(period_button)
        pyautogui.typewrite(period)
    else:
        speak("Could not find the period setting.")
        return

    save_button = pyautogui.locateOnScreen('save_button.png', confidence=0.8)
    if save_button:
        pyautogui.click(save_button)
    else:
        speak("Could not find the Save button.")
        return

    speak(f"Alarm set for {alarm_time}.")
    log_text(f"Alarm set for {alarm_time}")


def take_note():
    speak("What would you like to note?")
    note = voice_command()
    if note == "None":
        return
    with open("notes.txt", "a") as f:
        f.write(note + "\n")
    speak("Note added.")
    log_text(f"Note added: {note}")

def read_notes():
    try:
        with open("notes.txt", "r") as f:
            notes = f.read()
        if notes:
            speak("Here are your notes.")
            log_text(notes)
            speak(notes)
        else:
            speak("You have no notes.")
    except FileNotFoundError:
        speak("You have no notes.")

def tell_joke():
    url = "https://official-joke-api.appspot.com/random_joke"
    response = requests.get(url)
    joke = response.json()
    speak(joke['setup'])
    speak(joke['punchline'])
    log_text(f"Joke: {joke['setup']} - {joke['punchline']}")

def play_youtube_video(video_name):
    speak(f"Playing {video_name} on YouTube.")
    log_text(f"Playing YouTube video: {video_name}")
    kit.playonyt(video_name)

def execute_command(command):
    if 'hello' in command:
        speak('Hi, how can I help you?')
    elif 'wikipedia' in command and 'search on' not in command:
        speak("Searching Wikipedia...")
        command = command.replace("wikipedia", "")
        try:
            results = wikipedia.summary(command, sentences=5)
            speak("According to Wikipedia")
            log_text(results)
            speak(results)
        except wikipedia.exceptions.DisambiguationError as e:
            speak("There are multiple results for this query, please be more specific.")
            log_text(f"DisambiguationError: {e.options}")
        except wikipedia.exceptions.PageError:
            speak("Sorry, I could not find any results for your query.")
            log_text("PageError: No results found.")
    elif 'search on wikipedia' in command:
        query = command.replace('search on wikipedia', '').strip()
        if query:
            speak(f"Searching for {query} on Wikipedia...")
            log_text(f"Searching for {query} on Wikipedia...")
            webbrowser.open(f"https://en.wikipedia.org/wiki/{query}")
        else:
            speak("Please specify what you want to search on Wikipedia.")
            log_text("Please specify what you want to search on Wikipedia.")
    elif 'open notepad' in command:
        speak('Opening Notepad...')
        path = "c:\\windows\\system32\\notepad.exe"
        os.startfile(path)
    elif 'close notepad' in command:
        speak('Closing Notepad...')
        os.system('taskkill /F /IM notepad.exe')
    elif 'open youtube' in command:
        speak("Opening YouTube...")
        webbrowser.open("https://www.youtube.com/")
    elif 'close youtube' in command:
        close_browser_tab("youtube")
    elif 'open google' in command:
        speak("Opening Google...")
        webbrowser.open("https://www.google.co.in/")
    elif 'play music' in command:
        speak('Opening Spotify...')
        try:
            subprocess.run(['start', 'spotify:'], shell=True)
        except Exception as e:
            speak("Sorry, I am unable to open Spotify.")
            log_text(f"Error: {e}")
    elif 'open mail' in command:
        speak("Opening Mail...")
        webbrowser.open("https://mail.google.com/mail/u/0/#inbox")
    elif 'open whatsapp' in command:
        speak("Opening WhatsApp...")
        webbrowser.open("https://web.whatsapp.com/")
    elif 'close' in command:
        activity = command.replace('close', '').strip()
        if close_application(activity):
            speak(f'Closing {activity}')
        else:
            speak(f'Could not find {activity} to close.')
    elif 'exit' in command:
        speak("Thanks for giving me your time. Have a nice day!")
        return False
    elif 'weather in' in command:
        city = command.replace('weather in', '').strip()
        get_weather(city)
    elif 'set an alarm for' in command:
        alarm_time = command.replace('set an alarm for', '').strip()
        set_alarm(alarm_time)
    elif 'take a note' in command or 'note this down' in command:
        take_note()
    elif 'read my notes' in command:
        read_notes()
    elif 'tell me a joke' in command:
        tell_joke()
    elif 'play' in command and 'on youtube' in command:
        video_name = command.replace('play', '').replace('on youtube', '').strip()
        play_youtube_video(video_name)
    else:
        speak("Sorry, I didn't catch that. Can you repeat?")
    return True

def close_application(app_name):
    for proc in psutil.process_iter(['name']):
        if app_name.lower() in proc.info['name'].lower():
            proc.kill()
            return True
    return False

def close_browser_tab(site_name):
    for proc in psutil.process_iter(['name']):
        if proc.info['name'].lower() in ['chrome.exe', 'firefox.exe', 'msedge.exe']:
            if any(site_name.lower() in cmd for cmd in proc.cmdline()):
                proc.kill()
                return True
    return False

def start_listening():
    command = voice_command()
    if command == "None":
        return
    execute_command(command)

def start_listening_thread():
    threading.Thread(target=start_listening).start()

def log_text(text):
    logging.info(text)
    response_area.config(state=tk.NORMAL)
    response_area.insert(tk.END, text + "\n")
    response_area.yview(tk.END)
    response_area.config(state=tk.DISABLED)

if __name__ == '__main__':
    try:
        engine = pyttsx3.init('sapi5')
        voices = engine.getProperty('voices')
        engine.setProperty('voice', voices[1].id)
        root = tk.Tk()
        root.title("Personal Assistant")

        frame = tk.Frame(root)
        frame.pack(pady=20)

        listen_button = tk.Button(frame, text="Listen", command=start_listening_thread, bg="black", fg="white", font=("Helvetica", 16), height=3, width=10)
        listen_button.pack(pady=10)

        response_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=50, height=15, font=("Helvetica", 14))
        response_area.pack(padx=10, pady=10)
        response_area.config(state=tk.DISABLED)

        greet()
        root.mainloop()

    except Exception as ex:
        logging.error(f"An error occurred: {ex}")

    finally:
        logging.info("Thank you. Bye. Have a nice day.")

