import tkinter as tk
from tkinter import messagebox
import speech_recognition as sr
import pyttsx3
from transformers import pipeline
import os
import webbrowser
import datetime

# Initialize speech engine
engine = pyttsx3.init()
engine.setProperty('rate', 160)

def speak(text):
    response_label.config(text="VocaMind: " + text)
    engine.say(text)
    engine.runAndWait()

# Hugging Face zero-shot classifier
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

labels = [
    "open word", 
    "open notepad", 
    "play music", 
    "play movie",
    "open youtube", 
    "open file explorer", 
    "open browser", 
    "greeting", 
    "exit", 
    "tell a joke",
    "show time",
    "search the web",
    "take screenshot"
]

# Listen & recognize user command
def listen_and_recognize():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        status_label.config(text="🎤 Listening...")
        root.update()
        try:
            audio = recognizer.listen(source, timeout=5)
        except sr.WaitTimeoutError:
            speak("No speech detected. Try again.")
            return ""
    try:
        command = recognizer.recognize_google(audio)
        command_label.config(text="You said: " + command)
        return command.lower()
    except sr.UnknownValueError:
        speak("Sorry, I didn't understand.")
        return ""
    except sr.RequestError:
        speak("Speech recognition service failed.")
        return ""

# Load the Hugging Face LLM model
llm = pipeline("text-generation", model="distilgpt2")

# def generate_llm_response(prompt):
#     result = llm(prompt, max_new_tokens=100, do_sample=True)
#     response = result[0]["generated_text"].replace(prompt, "").strip()
#     return response

def generate_llm_response(prompt):
    result = llm(prompt, max_new_tokens=100, do_sample=True, temperature=0.7)
    generated = result[0]["generated_text"]
    
    # Remove the prompt from the response
    response = generated.replace(prompt, "").strip()

    # Remove repeated lines or truncations
    lines = response.split("\n")
    unique_lines = []
    for line in lines:
        if line.strip() not in unique_lines:
            unique_lines.append(line.strip())
    
    clean_response = " ".join(unique_lines)
    return clean_response


# Perform system actions
def perform_action(intent):
    try:
        if intent == "open word":
            os.system("start winword")
            speak("Opening Microsoft Word.")
        elif intent == "open notepad":
            os.system("notepad")
            speak("Opening Notepad.")
        elif intent == "play music":
            music_path = "C:\\Users\\acer\\Documents\\Brototype\\Week31\\vocamind\\Kadha-Thudarum.mp3"
            os.system(f'start "" "{music_path}"')
            speak("Playing music.")
        elif intent == "play movie":
            speak("Feature coming soon. Movie player not linked.")
        elif intent == "open youtube":
            webbrowser.open("https://www.youtube.com")
            speak("Opening YouTube.")
        elif intent == "open file explorer":
            os.system("explorer")
            speak("Opening File Explorer.")
        elif intent == "open browser":
            webbrowser.open("https://www.google.com")
            speak("Opening browser.")
        elif intent == "greeting":
            speak("Hello! How can I assist you today?")
        elif intent == "exit":
            speak("Goodbye!")
            root.quit()
        elif intent == "tell a joke":
            speak("Why did the computer go to therapy? Because it had too many bytes of emotional baggage.")
        elif intent == "show time":
            now = datetime.datetime.now().strftime("%H:%M")
            speak(f"The current time is {now}.")
        elif intent == "search the web":
            speak("What should I search for?")
            query = listen_and_recognize()
            if query:
                webbrowser.open(f"https://www.google.com/search?q={query}")
                speak(f"Searching for {query}")
        elif intent == "take screenshot":
            speak("Taking a screenshot.")
            os.system("snippingtool /clip")
        else:
            speak("Sorry, I can't perform that action yet.")
    except Exception as e:
        speak(f"Something went wrong: {str(e)}")

# Main interaction
def handle_command():
    query = listen_and_recognize()
    if query:
        result = classifier(query, labels)
        best_intent = result["labels"][0]
        intent_label.config(text=f"Intent detected: {best_intent}")
        perform_action(best_intent)

# LLM
def ask_llm():
    query = listen_and_recognize()
    if query:
        command_label.config(text="You said: " + query)
        response = generate_llm_response("User asked: " + query)
        speak(response)

# ---------------------- GUI -------------------------
root = tk.Tk()
root.title("VocaMind - Voice Assistant")
root.geometry("500x400")
root.configure(bg="#f2f2f2")

tk.Label(root, text="🎙️ VocaMind Voice Assistant", font=("Arial", 20, "bold"), bg="#f2f2f2").pack(pady=10)

status_label = tk.Label(root, text="Press Start to speak...", font=("Arial", 12), bg="#f2f2f2")
status_label.pack()

command_label = tk.Label(root, text="", font=("Arial", 12), fg="blue", bg="#f2f2f2")
command_label.pack(pady=5)

intent_label = tk.Label(root, text="", font=("Arial", 12), fg="green", bg="#f2f2f2")
intent_label.pack(pady=5)

response_label = tk.Label(root, text="", font=("Arial", 12), wraplength=450, bg="#f2f2f2")
response_label.pack(pady=10)

tk.Button(root, text="🎧 Start Listening", font=("Arial", 14), command=handle_command, bg="#4CAF50", fg="white").pack(pady=20)

tk.Button(root, text="❌ Exit", font=("Arial", 12), command=root.quit, bg="#d32f2f", fg="white").pack()
# tk.Button(root, text="🧠 Ask VocaMind (LLM)", font=("Arial", 12), command=ask_llm, bg="#2196F3", fg="white").pack(pady=10)
root.mainloop()
