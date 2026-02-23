import pyttsx3
import base64
import requests
import musicLibrary
import webbrowser
import os
import subprocess as sp
from datetime import datetime
import speech_recognition as sr
import keyboard
from decouple import config
from random import choice
import psutil
import pyjokes
import pyautogui
import time
import json
import speedtest
import screen_brightness_control as sbc
import pywhatkit as kit
import eel
import threading
import pythoncom
from gtts import gTTS
import playsound
from deep_translator import GoogleTranslator
import asyncio
import edge_tts
import pygame
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
import ctypes
import cv2
import numpy as np
import pyautogui # For Screenshot capability
from online import find_my_ip,search_on_google,search_on_wikipidia,youtube,weather_forecast,send_email,get_random_fact,get_dictionary_meaning,get_ai_response,get_groq_response,get_latest_news,get_joke,get_advice

def take_screenshot():
    try:
        if not os.path.exists("Screenshots"):
            os.makedirs("Screenshots")
        path = f"Screenshots/Jarvis_Screen_{int(time.time())}.png"
        pyautogui.screenshot(path)
        return path
    except: return None

def volume_up():
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, pythoncom.CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    current_vol = volume.GetMasterVolumeLevelScalar()
    volume.SetMasterVolumeLevelScalar(min(current_vol + 0.1, 1.0), None)

def volume_down():
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, pythoncom.CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    current_vol = volume.GetMasterVolumeLevelScalar()
    volume.SetMasterVolumeLevelScalar(max(current_vol - 0.1, 0.0), None)

def volume_mute():
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, pythoncom.CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    volume.SetMute(1, None)

def set_brightness(level):
    try:
        sbc.set_brightness(level)
        return True
    except: return False

# Will be initialized in the logic thread
engine = None
from conv import random_text
USER = config("USER")
HOSTNAME = config("BOT")
NEWS = config('NEWS')
# Initialize Eel
eel.init('web')

# AI Data Management
LAST_AI_TIME = 0
COOLDOWN_PERIOD = 60 # Seconds between AI queries for Free Tier
chat_history = []  # Neural Memory: Stores recent conversation exchanges

def speak(text):
    print(f"\n[JARVIS]: {text}")
    eel.addLog(f"JARVIS: {text}")
    eel.updateStatus("Speaking...")
    
    # NEURAL VOICE (Online - High Quality)
    VOICE = "en-GB-ThomasNeural" # Professional British Accent (Jarvis-like)
    OUTPUT_FILE = "jarvis_voice.mp3"
    
    async def generate_speech():
        communicate = edge_tts.Communicate(text, VOICE)
        await communicate.save(OUTPUT_FILE)

    try:
        # Run async generation
        asyncio.run(generate_speech())
        
        # Play using pygame (more stable than playsound)
        pygame.mixer.init()
        pygame.mixer.music.load(OUTPUT_FILE)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        pygame.mixer.music.unload()
        
    except Exception as e:
        print(f"Neural Voice Error: {e}. Falling back to SAPI5.")
        # FALLBACK (Offline - Standard Quality)
        global engine
        if engine:
            engine.say(text)
            engine.runAndWait()

    eel.updateStatus("Online")

def speak_hindi(text):
    print(f"\n[JARVIS (Hindi)]: {text}")
    tts = gTTS(text=text, lang='hi')
    filename = "hindi_voice.mp3"
    tts.save(filename)
    playsound.playsound(filename)
    os.remove(filename)

def speak_punjabi(text):
    print(f"\n[JARVIS (Punjabi)]: {text}")
    tts = gTTS(text=text, lang='pa')
    filename = "punjabi_voice.mp3"
    tts.save(filename)
    playsound.playsound(filename)
    os.remove(filename)

def speak_multilingual(text, lang_code):
    """Generic function to translate and speak in any language."""
    try:
        translated = GoogleTranslator(source='auto', target=lang_code).translate(text)
        print(f"\n[JARVIS ({lang_code})]: {translated}")
        tts = gTTS(text=translated, lang=lang_code)
        filename = f"{lang_code}_voice.mp3"
        tts.save(filename)
        playsound.playsound(filename)
        os.remove(filename)
    except Exception as e:
        print(f"Translation Error: {e}")
        speak(text) # Fallback to English

# System Status Functions
def get_battery_status():
    battery = psutil.sensors_battery()
    percent = battery.percent
    if battery.power_plugged:
        status = "Charging"
    else:
        status = "Discharging"
    return f"Battery is at {percent} percent and is currently {status}."

def get_system_stats():
    cpu_usage = psutil.cpu_percent()
    ram_usage = psutil.virtual_memory().percent
    return f"CPU utilization is at {cpu_usage} percent, and memory usage is at {ram_usage} percent."

def take_screenshot():
    speak("Please name the screenshot file sir.")
    name = take_command().lower()
    if name != "none":
        # Create folder if it doesn't exist
        if not os.path.exists("Screenshots"):
            os.makedirs("Screenshots")
            
        speak("Taking screenshot in 3 seconds sir. Please switch to the desired window.")
        time.sleep(3)
        img = pyautogui.screenshot()
        # Save path inside the folder
        save_path = os.path.join("Screenshots", f"{name}.png")
        img.save(save_path)
        speak(f"Screenshot saved in the screenshots folder as {name} dot P N G.")
    else:
        speak("I didn't catch the name, task cancelled.")

def internet_speed():
    speak("Testing internet speed sir. Please wait a moment.")
    try:
        # We use a custom User-Agent to avoid the '403 Forbidden' error
        st = speedtest.Speedtest(secure=True)
        st.get_best_server()
        download = st.download() / 1_000_000  # Convert to Mbps
        upload = st.upload() / 1_000_000
        speak(f"Sir, our download speed is {download:.2f} Mbps and upload speed is {upload:.2f} Mbps.")
    except Exception as e:
        print(f"Error: {e}")
        speak("Sir, I encountered a security block while checking the speed. I'll attempt to bypass it next time.")

def volume_control(action):
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    if action == "mute":
        volume.SetMute(1, None)
        speak("System muted, sir.")
    elif action == "unmute":
        volume.SetMute(0, None)
        speak("System unmuted.")
    elif action == "up":
        current_volume = volume.GetMasterVolumeLevelScalar()
        volume.SetMasterVolumeLevelScalar(min(1.0, current_volume + 0.1), None)
        speak("Volume increased.")
    elif action == "down":
        current_volume = volume.GetMasterVolumeLevelScalar()
        volume.SetMasterVolumeLevelScalar(max(0.0, current_volume - 0.1), None)
        speak("Volume decreased.")

def nasa_astronomy():
    speak("Connecting to NASA's archives sir.")
    # Using a public API for NASA APOD
    try:
        api_url = "https://api.nasa.gov/planetary/apod?api_key=DEMO_KEY"
        response = requests.get(api_url).json()
        title = response.get("title", "Unknown")
        explanation = response.get("explanation", "")
        img_url = response.get("url", "")
        
        speak(f"Today's featured image is titled {title}.")
        speak("I am displaying the cosmic marvel on your screen now.")
        webbrowser.open(img_url)
        # Shorten explanation to avoid too much talking
        short_exp = explanation[:200] + "..."
        speak(f"Historical data states: {short_exp}")
    except Exception as e:
        speak("Sir, I'm unable to reach NASA's servers at the moment.")

def lock_system():
    speak("Locking down the system, sir.")
    ctypes.windll.user32.LockWorkStation()

def pc_power(command):
    if "shutdown" in command:
        speak("Sir, shutting down all systems. Are you sure?")
        confirm = take_command().lower()
        if "yes" in confirm or "do it" in confirm:
            speak("Goodbye sir. Terminating all processes.")
            os.system("shutdown /s /t 1")
    elif "restart" in command:
        speak("Restarting the central processing unit.")
        os.system("shutdown /r /t 1")
    elif "sleep" in command:
        speak("Putting the system into low power mode.")
        os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")

def brightness_control(query):
    try:
        if "increase" in query:
            current = sbc.get_brightness()[0]
            sbc.set_brightness(min(100, current + 20))
            speak("Brightness increased by 20 percent.")
        elif "decrease" in query:
            current = sbc.get_brightness()[0]
            sbc.set_brightness(max(0, current - 20))
            speak("Brightness decreased by 20 percent.")
        elif "max" in query:
            sbc.set_brightness(100)
            speak("Brightness set to maximum capacity.")
    except Exception as e:
        speak("Sir, I couldn't adjust the optical sensors.")

def tell_time():
    time_now = datetime.now().strftime("%I:%M %p")
    speak(f"Sir, the current time is {time_now}")

def tell_date():
    date_now = datetime.now().strftime("%A, %B %d, %Y")
    speak(f"Today is {date_now}")

def send_whatsapp():
    speak("Who should I message sir? Please speak the name as saved in your contacts.")
    # Note: pywhatkit requires a recipient and message. 
    # For now we'll ask for phone number to be precise.
    speak("Please enter the mobile number in the console for precision.")
    number = input("Enter Number with Country Code: ")
    speak("What is the message?")
    message = take_command()
    speak("Dispatching message via Cloud services...")
    kit.sendwhatmsg_instantly(number, message)
    speak("Message has been queued for delivery.")

def write_note():
    speak("What should I write down, sir?")
    note_content = take_command()
    if note_content != "none":
        with open("notes.txt", "a") as f:
            f.write(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] : {note_content}")
        speak("I've recorded that in your notes, sir.")
    else:
        speak("I didn't hear the note content.")

def manage_memory(action):
    memory_file = "memory.json"
    if action == "save":
        speak("What information should I commit to my shared memory, sir?")
        info = take_command().lower()
        if info != "none":
            speak("And what label should I give this memory?")
            label = take_command().lower()
            
            try:
                with open(memory_file, "r") as f:
                    data = json.load(f)
            except:
                data = {}
                
            data[label] = info
            with open(memory_file, "w") as f:
                json.dump(data, f)
            speak(f"Memory recorded under the label {label}, sir.")
            
    elif action == "recall":
        speak("Which memory label should I recall?")
        label = take_command().lower()
        try:
            with open(memory_file, "r") as f:
                data = json.load(f)
            if label in data:
                speak(f"Historical records for {label} state: {data[label]}")
            else:
                speak(f"I have no records for the label {label}, sir.")
        except:
            speak("My memory banks are currently empty, sir.")

def verify_face():
    import mediapipe as mp
    from mediapipe.tasks import python
    global CAMERA_BUSY
    CAMERA_BUSY = True
    time.sleep(1.5) # Wait for sensory thread to release cam
    
    from mediapipe.tasks.python import vision
    import json
    import numpy as np
    
    speak("Initializing visual security protocol. Please look directly at the camera.")
    
    model_path = 'face_landmarker.task'
    sig_path = 'user_face_signature.json'
    
    if not os.path.exists(model_path) or not os.path.exists(sig_path):
        speak("Sir, your neural signature files are missing. Please run the training script first.")
        return False

    with open(sig_path, 'r') as f:
        stored_sig = np.array(json.load(f))

    BaseOptions = mp.tasks.BaseOptions
    FaceLandmarker = mp.tasks.vision.FaceLandmarker
    FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
    VisionRunningMode = mp.tasks.vision.RunningMode

    options = FaceLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=model_path),
        running_mode=VisionRunningMode.VIDEO)

    cap = cv2.VideoCapture(0)
    # Optimized resolution for the new circular HUD
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    authenticated = False
    start_time = time.time()
    match_count = 0
    required = 12 # Slightly more stability required for security
    
    def get_sig(landmarks):
        def dist(p1, p2):
            return np.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2 + (p1.z - p2.z)**2)
        lx = dist(landmarks[33], landmarks[133])
        rx = dist(landmarks[362], landmarks[263])
        ed = dist(landmarks[133], landmarks[362])
        nw = dist(landmarks[61], landmarks[291])
        fh = dist(landmarks[10], landmarks[152])
        fw = dist(landmarks[234], landmarks[454])
        return np.array([ed/fw, lx/fw, nw/fw, fh/fw, dist(landmarks[1], landmarks[152])/fh, dist(landmarks[33], landmarks[263])/fw])

    eel.toggleSecurityScan(True)
    eel.sleep(1.2) # Wait for cinematic 3D expansion
    print("[SYSTEM]: INITIATING NEURAL RECOGNITION...")

    with FaceLandmarker.create_from_options(options) as landmarker:
        while time.time() - start_time < 20: # Slightly longer timeout
            ret, frame = cap.read()
            if not ret: break
            
            frame = cv2.flip(frame, 1)
            h, w, _ = frame.shape
            
            # Neural Blue Filter for the "AI" look
            frame[:, :, 0] = cv2.add(frame[:, :, 0], 50) # Boost blue channel
            
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            timestamp_ms = int(time.time() * 1000)
            result = landmarker.detect_for_video(mp_image, timestamp_ms)
            
            status = "SCANNING BIOMETRICS..."
            indicator_color = (0, 229, 255) # Cyan
            
            if result.face_landmarks:
                current_sig = get_sig(result.face_landmarks[0])
                diff = np.mean(np.abs(current_sig - stored_sig))
                
                # Visual Feedback: Draw the complex mesh points (The "Jarvis Look")
                # Selecting key structural points (Forehead, Eyes, Nose, Mouth, Jawline)
                indices = [10, 152, 33, 133, 362, 263, 1, 61, 291, 234, 454, 5, 4, 168, 197, 195, 19, 94]
                for idx in indices:
                    pt = result.face_landmarks[0][idx]
                    cv2.circle(frame, (int(pt.x * w), int(pt.y * h)), 2, indicator_color, -1)
                
                # Dynamic Threshold Check (Relaxed to 0.055 for better capture)
                if diff < 0.055:
                    match_count += 1
                    indicator_color = (0, 255, 136) # Neon Green
                    status = f"IDENTITY VERIFIED: {int((match_count/required)*100)}%"
                    # Draw connection lines between eyes and nose for "processing" feel
                    p1 = result.face_landmarks[0][33]
                    p2 = result.face_landmarks[0][362]
                    cv2.line(frame, (int(p1.x*w), int(p1.y*h)), (int(p2.x*w), int(p2.y*h)), indicator_color, 1)
                else:
                    match_count = max(0, match_count - 1)
                    status = "ANALYZING STRUCTURE..."
                
            # Update Web HUD
            eel.setScanStatus(status)
            
            # Streaming to Eel
            _, buffer = cv2.imencode('.jpg', frame)
            jpg_as_text = base64.b64encode(buffer).decode('utf-8')
            eel.updateScanView(jpg_as_text)
            
            if match_count >= required:
                authenticated = True
                break
            
            eel.sleep(0.01)

    cap.release()
    cv2.destroyAllWindows()
    
    # Save a security log snapshot
    try:
        if not os.path.exists("security_logs"):
            os.makedirs("security_logs")
        log_name = f"security_logs/{'SUCCESS' if authenticated else 'FAILED'}_{int(time.time())}.jpg"
        cv2.imwrite(log_name, frame)
        eel.addTerminalLine(f"SECURITY AUDIT: Snapshot saved as {log_name}")
    except Exception as e:
        eel.addTerminalLine(f"LOG ERROR: Could not save security snapshot. {e}")
    
    if authenticated:
        eel.setScanStatus("ACCESS GRANTED")
        eel.sleep(1) # Show success for a second
        eel.toggleSecurityScan(False)
        speak(f"Identity confirmed. Welcome back, {USER}.")
        CAMERA_BUSY = False
        return True
    else:
        eel.setScanStatus("ACCESS DENIED")
        eel.sleep(1.5)
        eel.toggleSecurityScan(False)
        speak("Biometric mismatch. Identity could not be verified, sir.")
        CAMERA_BUSY = False
        return False

def take_photo():
    global CAMERA_BUSY
    CAMERA_BUSY = True
    time.sleep(1.2)
    import cv2
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    if ret:
        file_name = f"snapshot_{int(time.time())}.jpg"
        cv2.imwrite(file_name, frame)
        speak("Photo captured and saved to your directory, sir.")
        eel.showNotification("Visual Snapshot Saved", "success")
    cap.release()
    cv2.destroyAllWindows()
    CAMERA_BUSY = False

def empty_recycle_bin():
    import winshell
    try:
        winshell.recycle_bin().empty(confirm=False, show_progress=False, sound=True)
        speak("Recycle bin has been purged, sir.")
        eel.showNotification("System Cleanup Complete", "success")
    except Exception as e:
        speak("Sir, the recycle bin is already empty or there was an access error.")
        eel.addTerminalLine(f"Cleanup Error: {e}")

def system_scan():
    import psutil
    import platform
    import shutil
    
    speak("Initiating deep system scan. Accessing hardware layers.")
    eel.showNotification("System Scan in Progress", "alert")
    eel.setOrbState("processing")
    
    # Cinematic technical steps
    scan_steps = [
        ("CPU REGISTRIES", f"{psutil.cpu_count()} CORES - {platform.processor()}"),
        ("MEMORY BANKS", f"{round(psutil.virtual_memory().total / (1024**3), 2)}GB TOTAL - ALL SECTORS NOMINAL"),
        ("DATA REPOSITORIES", f"{shutil.disk_usage('/').free // (1024**3)}GB AVAILABLE ON PRIMARY DRIVE"),
        ("NEURAL NETWORK", "LATENCY 12MS - ENCRYPTION LAYER STABLE"),
        ("SENSORY ARRAY", "3D GEOMETRIC BIOMETRICS ONLINE"),
        ("OS ARCHITECTURE", f"{platform.system()} {platform.release()} - KERNEL INTEGRITY VERIFIED")
    ]
    
    for label, result in scan_steps:
        eel.addTerminalLine(f"SCANNING {label}...")
        time.sleep(0.7)
        eel.addTerminalLine(f"   [RESULT]: {result}")
        time.sleep(0.3)
        
    eel.setOrbState("default")
    eel.showNotification("Deep Scan Complete", "success")
    speak("Sir, the deep system scan is complete. All hardware and neural components are operating at peak efficiency.")

def self_destruct():
    speak("Sir, are you absolutely sure? This cannot be undone.")
    confirm = take_command().lower()
    if "yes" in confirm or "do it" in confirm:
        speak("Initiating self-destruct sequence.")
        speak("Security protocols overridden.")
        speak("Releasing all safety valves.")
        for i in range(5, 0, -1):
            speak(str(i))
            time.sleep(1)
        speak("Just kidding sir! Your hardware is safe. I would never abandon you.")
    else:
        speak("Self-destruct sequence aborted. Thank goodness for that, sir.")

#Greeting 
def greet_me():
    hour = datetime.now().hour
    if (hour >= 0) and (hour < 12):
        speak(f"Good Morning, {USER}")
    elif (hour >= 12) and (hour < 16):
        speak(f"Good Afternoon, {USER}")
    elif (hour >= 16) and (hour < 24):
        speak(f"Good Evening, {USER}")
    
    print("-" * 50)
    print(">>> INITIALIZING ALL SYSTEMS...")
    print(">>> RECONSTRUCTING USER INTERFACE...")
    print(">>> ESTABLISHING SECURE CONNECTION...")
    print("-" * 50)
    speak("I am back online sir. All systems are operational.")
Listening=False
#start and pause keys defining
def start_listening():
    global Listening
    Listening=True
    print("Started Listening")

def Pause_Listening():
    global Listening
    Listening=False
    print("Listening Paused")


keyboard.add_hotkey('ctrl+alt+s',start_listening)    
keyboard.add_hotkey('ctrl+alt+p',Pause_Listening) 


#command taking
MIC_BUSY = False

def take_command():
    global MIC_BUSY
    MIC_BUSY = True
    time.sleep(0.3) # Allow audio sync to yield
    
    r=sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        eel.updateStatus("Listening...")
        eel.setOrbActive(True)
        r.adjust_for_ambient_noise(source, duration=0.5)
        r.pause_threshold = 1
        # Increased phrase_time_limit for longer AI queries
        audio = r.listen(source, phrase_time_limit=8)
    try:
        print("Recognizing.....")
        eel.updateStatus("Scanning...")
        eel.addTerminalLine("Processing Neural Voice Data...")
        query = r.recognize_google(audio, language="en-in")
        print(f"User said: {query}\n")
        eel.addLog(f"User: {query}")
        eel.addTerminalLine(f"RECOGNIZED: {query}")
        eel.setLastCommand(query)
    except Exception:
        query = 'None'
        eel.addTerminalLine("Noise pattern detected. Unrecognized command.")
    
    eel.setOrbActive(False)
    MIC_BUSY = False
    return query

def update_ui_vitals():
    print("Vitals thread started.")
    while True:
        try:
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent
            battery = psutil.sensors_battery()
            bat_percent = battery.percent if battery else 0
            eel.updateVitals(cpu, ram, bat_percent)
        except:
            pass
        time.sleep(2)

CAMERA_BUSY = False

def sensory_processing_thread():
    global CAMERA_BUSY, Listening
    import cv2 
    import time
    import base64
    
    # Absolute reliability: OpenCV Haar Cascades for Face Detection
    cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    face_cascade = cv2.CascadeClassifier(cascade_path)
    
    cap = cv2.VideoCapture(0)
    last_presence_time = time.time()
    stealth_active = False
    
    print("Project Ghost: Vision Hub Initialized (Presence Detection Only).")
    
    while True:
        if CAMERA_BUSY:
            if cap.isOpened(): cap.release()
            time.sleep(1)
            continue
            
        if not cap.isOpened(): cap.open(0)
            
        ret, frame = cap.read()
        if not ret:
            time.sleep(0.1)
            continue
            
        # 1. Project Ghost: Presence Logic (Local)
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            
            status_text = "PRESENCE DETECTED" if len(faces) > 0 else "NO USER DETECTED"
            
            if len(faces) > 0:
                last_presence_time = time.time()
                if stealth_active:
                    eel.setStealthMode(False)
                    stealth_active = False
            else:
                if time.time() - last_presence_time > 30 and not stealth_active and Listening:
                    eel.setStealthMode(True)
                    stealth_active = True
        except: 
            status_text = "SENSORY ERROR"

        # 2. Neural Link: Stream live feed to HUD
        try:
            # Flip and resize for the 16:9 camera-panel
            stream_frame = cv2.resize(cv2.flip(frame, 1), (320, 180))
            _, buffer = cv2.imencode('.jpg', stream_frame, [cv2.IMWRITE_JPEG_QUALITY, 55])
            base64_frame = base64.b64encode(buffer).decode('utf-8')
            eel.updateCameraFeed(base64_frame)
            eel.updateGesture(status_text)
        except: pass

        time.sleep(0.01)

def audio_reactive_thread():
    import sounddevice as sd
    import numpy as np
    
    print("Synapse Audio Sync started.")
    
    def audio_callback(indata, frames, time_info, status):
        global MIC_BUSY
        if MIC_BUSY:
            return
        # Calculate RMS (Root Mean Square) for intensity
        rms = np.sqrt(np.mean(indata**2))
        intensity = min(100, int(rms * 500)) # Gain adjusted for sounddevice (floats 0.0-1.0)
        eel.updateAudioIntensity(intensity)
    
    try:
        with sd.InputStream(callback=audio_callback, channels=1, samplerate=44100):
            while True:
                time.sleep(0.1)
    except Exception as e:
        print(f"Audio Reactive Error: {e}")

def start_jarvis_logic():
    global Listening, engine, LAST_AI_TIME, chat_history
    try:
        print("Logic thread started.")
        # Initialize COM for this thread (Crucial for SAPI5)
        pythoncom.CoInitialize()
        eel.addTerminalLine("SYSTEM BOOT: ACCESSING VOLATILE MEMORY...")
        # Initialize pyttsx3 in this thread for SAPI5 compatibility
        engine = pyttsx3.init('sapi5')
        engine.setProperty("volume", 1.5)
        engine.setProperty("rate", 170)
        voices = engine.getProperty("voices")
        engine.setProperty("voice", voices[1].id)
        
        time.sleep(2)
        greet_me()
        eel.addTerminalLine("ALL SYSTEMS NOMINAL. AWAITING WAKE WORD.")
        #opening aplications
        while True:
            try:
                if not Listening:
                    # Passive listening mode
                    query = take_command().lower()
                    
                    # Debugging: show what Jarvis hears in the terminal during wake-up phase
                    if query != "none":
                        eel.addTerminalLine(f"PASSIVE DETECTED: {query}")
                        
                    if "wake up" in query or "jarvis" in query:
                        eel.addTerminalLine("WAKE WORD DETECTED: INITIALIZING BIOMETRIC SCAN")
                        # Mandatory Biometric Scan
                        if verify_face():
                            Listening = True
                            eel.addTerminalLine("AUTH SUCCESS: JARVIS IS ONLINE")
                        else:
                            speak("Access denied. Systems remaining in standby.")
                            eel.addTerminalLine("AUTH FAILED: UNAUTHORIZED SUBJECT")
                        continue
                    time.sleep(0.1)
                
                if Listening:
                    query = take_command().lower()
                    
                    # Allow user to put Jarvis back to sleep
                    if "go to sleep" in query or "sleep" in query:
                        speak("Understood sir. I'll be here if you need me. Just say wake up.")
                        Listening = False
                        continue

                    if query == "none":
                        speak("I didn't catch that sir. Could you repeat?")
                        time.sleep(0.1)
                        continue
                    elif "how are you" in query:
                        speak(choice(random_text))
                        speak("Absolutely fine sir. How are you doing today?")
                    
                    elif "the time" in query:
                        tell_time()
                        
                    elif "the date" in query:
                        speak(choice(random_text))
                        tell_date()

                    elif "internet speed" in query:
                        speak(choice(random_text))
                        internet_speed()
                        
                    elif "mute" in query:
                        volume_control("mute")
                    elif "unmute" in query:
                        volume_control("unmute")
                    elif "volume up" in query:
                        volume_control("up")
                    elif "volume down" in query:
                        volume_control("down")
                        
                    elif "nasa" in query or "space" in query:
                        speak(choice(random_text))
                        nasa_astronomy()
                        
                    elif "lock the system" in query or "lockdown" in query:
                        speak(choice(random_text))
                        lock_system()
                        
                    elif "shutdown" in query or "restart" in query or "put the system to sleep" in query:
                        pc_power(query)
                        
                    elif "brightness" in query:
                        brightness_control(query)
                        
                    elif "whatsapp" in query:
                        send_whatsapp()

                    elif "note" in query:
                        write_note()
                        
                    elif "remember" in query or "save memory" in query:
                        manage_memory("save")
                        
                    elif "recall" in query or "what do you know about" in query:
                        manage_memory("recall")

                    elif "security scan" in query or "verify me" in query or "who am i" in query:
                        verify_face()

                    elif "battery" in query:
                        speak(get_battery_status())
                        
                    elif "system status" in query or "performance" in query:
                        speak("Checking system vitals sir...")
                        speak(get_system_stats())
                        
                    elif "joke" in query:
                        speak("Hope this one makes you laugh sir.")
                        joke = pyjokes.get_joke()
                        speak(joke)
                        
                    elif "who are you" in query:
                        speak("I am JARVIS, a Virtual Artificial Intelligence, and I'm here to assist you with a variety of tasks as best I can.")

                    elif "screenshot" in query:
                        take_screenshot()
                        
                    elif "self-destruct" in query or "self destruct" in query:
                        self_destruct()

                    elif "command prompt" in query or "cmd" in query:
                        speak("opening Command prompt sir")
                        os.system('start cmd')
                    elif "camera" in query:
                        speak("Opening Camera sir")
                        sp.run('start microsoft.windows.camera:',shell=True)
                    elif "notepad" in query:
                        speak("opening notepad sir")
                        notepad_path="C:\\Users\\Dilpreet\\AppData\\Local\\Microsoft\\WindowsApps\\notepad.exe"
                        try:
                            os.startfile(notepad_path)
                        except:
                            os.system("start notepad") # Fallback
                    elif "spotify" in query:
                        speak("opening spotify sir")
                        eel.showNotification("Launching Spotify", "success")
                        eel.setOrbState("processing")
                        Spotify_path="C:\\Users\\Dilpreet\\AppData\\Local\\Microsoft\\WindowsApps\\Spotify.exe"
                        try:
                            os.startfile(Spotify_path)
                            time.sleep(1)
                            eel.setOrbState("default")
                        except:
                            speak("Sir, I couldn't find the Spotify path, please check the main script.")
                            eel.setOrbState("error")
                    elif "photoshop" in query:
                        speak("opening photoshop sir")
                        photoshop_path="C:\\Program Files\\Adobe\\Adobe Photoshop 2023\\Photoshop.exe"
                        os.startfile(photoshop_path)
                    elif "gta" in query:
                        speak("opening gta 5 sir")
                        gta_v_path="D:\\Dilpreet Singh\\Games\\Grand Theft Auto V\\GTA5.exe"
                        os.startfile(gta_v_path)
                    
                    elif "premiere pro" in query:
                        speak("opening adobe premiere pro sir")
                        premiere_pro_path="C:\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs\\Adobe Premiere Pro 2023.lnk"
                        os.startfile(premiere_pro_path)
                    elif "edge" in query:
                        speak("opening microsoft edge sir")
                        eel.showNotification("Opening Microsoft Edge", "success")
                        edge_path="C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe"
                        os.startfile(edge_path)
                    elif "vs code" in query or "code" in query:
                        speak("opening vs code sir")
                        eel.showNotification("Accessing Development Environment", "success")
                        vscode_path="C:\\Users\\Dilpreet\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe"
                        os.startfile(vscode_path)
                    elif "chrome" in query:
                        speak("opening chrome sir")
                        eel.showNotification("Opening Google Chrome", "success")
                        chrome_="C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
                        os.startfile(chrome_)
                    elif "vintage" in query or "vantage" in query:
                        speak("opening lenovo vantage sir")
                        ventage_="C:\\Users\\Dilpreet\\OneDrive\\Desktop\\Lenovo Vantage.lnk"
                        os.startfile(ventage_)
                    elif "google" in query:
                        speak("opening google")
                        eel.showNotification("Searching on Google", "success")
                        webbrowser.open("https://www.google.co.in/")
                    elif "youtube" in query:
                        speak("opening youtube")
                        eel.showNotification("Streaming Uplink: YouTube", "alert")
                        webbrowser.open("https://www.youtube.com/")
                    elif "anime" in query:
                        speak("opening anime")
                        webbrowser.open("https://hianime.to/watch/demon-slayer-kimetsu-no-yaiba-swordsmith-village-arc-18056?ep=100092")
                
                #music opener
                    elif query.startswith("play"):
                        song=query.split(" ")[1]
                        link=musicLibrary.music[song]
                        webbrowser.open(link)
                #news headlines
                    elif "news" in query:
                        speak(choice(random_text))
                        eel.addTerminalLine("Connecting to News API...")
                        try:
                            r=requests.get(f"https://newsapi.org/v2/top-headlines?country=in&apiKey={NEWS}", timeout=10)
                            if r.status_code==200:
                                data=r.json()
                                articles=data.get("articles",[])
                                
                                lang = 'en'
                                if "hindi" in query: lang = 'hi'
                                elif "punjabi" in query: lang = 'pa'
                                
                                speak("Fetching the latest headlines for you sir.")
                                if not articles:
                                    speak("Sir, I couldn't find any news articles at the moment.")
                                    eel.addTerminalLine("ERROR: No news articles returned from API.")
                                else:
                                    for article in articles[:3]:
                                        title = article.get("title", "No Title Found")
                                        if lang == 'en':
                                            speak(title)
                                        else:
                                            speak_multilingual(title, lang)
                            else:
                                speak("Sir, I'm having trouble connecting to the news servers.")
                                eel.addTerminalLine(f"API Error: Status Code {r.status_code}")
                        except Exception as e:
                            speak("Sir, news servers are currently unreachable.")
                            eel.addTerminalLine(f"Request Error: {e}")
                    elif "my IP address" in query:
                        ip_address = find_my_ip()
                        print(f"Debug: IP address fetched is {ip_address}")
                        speak(f"your IP address is {ip_address}")
                        print(f"your IP address is {ip_address}")
                    elif " Jarvis play on youtube" in query:
                        speak("what do you want to play on youtube")
                        video = take_command().lower()
                        youtube(video)
                    elif "search on google" in query:
                        speak("what do you want to search on google")
                        query = take_command().lower()
                        search_on_google(query)
                    elif "search on amazon" in query:
                        speak("What product should I look for on Amazon, sir?")
                        product = take_command().lower()
                        if product != "none":
                            speak(f"Searching for {product} on Amazon.")
                            eel.showNotification("Amazon Uplink established", "alert")
                            webbrowser.open(f"https://www.amazon.in/s?k={product}")

                    elif "wikipedia" in query:
                        speak("what do you want to search on wikipidia sir")
                        search = take_command().lower()
                        results =search_on_wikipidia(search)
                        print(results)
                        speak(f"according to wikipidea, {results}")
                    # Assuming this is the relevant part of your code handling YouTube searches
                    elif "search on youtube" in query:
                        speak("What do you want to search on YouTube?")
                        search_query = take_command().lower()  # Capture the search query
                        youtube_search_url = f"https://www.youtube.com/results?search_query={search_query}"
                        webbrowser.open(youtube_search_url)  # Open the YouTube search page with the query
                    
                    elif query.strip() == "hindi":
                        speak_hindi("नमस्ते सर, मैं आपकी क्या सहायता कर सकता हूँ?")
                        
                    elif query.strip() == "punjabi":
                        speak_punjabi("ਸਤਿ ਸ੍ਰੀ ਅਕਾਲ ਸਰ, ਮੈਂ ਤੁਹਾਡੀ ਕਿਵੇਂ ਮਦਦ ਕਰ ਸਕਦਾ ਹਾਂ?")

                    elif 'weather' in query:
                        speak(choice(random_text))
                        # Check for language preference
                        lang = 'en'
                        if "hindi" in query: lang = 'hi'
                        elif "punjabi" in query: lang = 'pa'
                        
                        speak("Of course sir. Which city's weather should I fetch?")
                        city = take_command().lower()
                        if city != 'none':
                            speak(f"Searching for weather report in {city}...")
                            weather, temp, feels_like = weather_forecast(city)
                            
                            report = f"The current temperature is {temp}, but it feels like {feels_like}. The sky is currently showing {weather}"
                            
                            if lang == 'en':
                                speak(report)
                            else:
                                speak_multilingual(report, lang)
                                
                            print(f"\n--- WEATHER REPORT: {city.upper()} ---")
                            print(f"State: {weather}\nTemperature: {temp}\nFeels like: {feels_like}\n" + "-"*30)
                        else:
                            speak("I didn't catch the city name, sir.")
                            
                    elif "take a photo" in query or "snap" in query:
                        take_photo()
                        
                    elif "what do you see" in query or "describe this" in query or "look at this" in query:
                        from online import get_vision_response
                        global CAMERA_BUSY
                        CAMERA_BUSY = True
                        time.sleep(1.2)
                        
                        speak("Initiating neural sight. Analyzing visual feed, sir.")
                        eel.showNotification("Neural Sight Active", "alert")
                        eel.setOrbState("processing")
                        
                        cap = cv2.VideoCapture(0)
                        ret, frame = cap.read()
                        cap.release()
                        
                        if ret:
                            # Neural Image Enhancement (Contrast/Brightness)
                            alpha = 1.3 # Contrast control
                            beta = 30   # Brightness control
                            enhanced_frame = cv2.convertScaleAbs(frame, alpha=alpha, beta=beta)
                            
                            _, buffer = cv2.imencode('.jpg', enhanced_frame)
                            description = get_vision_response(buffer.tobytes(), query)
                            eel.addTerminalLine("VISION ANALYSIS COMPLETE.")
                            eel.setOrbState("default")
                            speak(description)
                        else:
                            speak("I'm sorry sir, I couldn't access the visual feed right now.")
                            eel.setOrbState("error")
                        CAMERA_BUSY = False
                        
                    elif "empty recycle bin" in query or "clear cache" in query:
                        empty_recycle_bin()

                    elif "send an email" in query:
                        speak(choice(random_text))
                        speak("Certainly. Who is the recipient? Please enter the address in the console for security.")
                        receiver_add = input("Recipient Email: ")
                        speak("What is the subject of the email?")
                        subject = take_command()
                        speak("And what is the message, sir?")
                        message = take_command()
                        if send_email(receiver_add, subject, message):
                            speak("The email has been dispatched, sir.")
                        else:
                            speak("Transmission failed. Please check the error logs.")

                    elif "tell me a fact" in query or "did you know" in query:
                        fact = get_random_fact()
                        eel.showNotification("Knowledge Retrieval", "success")
                        speak(f"Did you know that... {fact}")
                        
                    elif "increase volume" in query:
                        volume_up()
                        speak("Volume increased by ten percent, sir.")
                        
                    elif "decrease volume" in query:
                        volume_down()
                        speak("Volume decreased, sir.")

                    elif "mute" in query:
                        volume_mute()
                        speak("Audio output silenced, sir.")

                    elif "brightness" in query:
                        # Extract percentage if present
                        import re
                        match = re.search(r'\d+', query)
                        if match:
                            level = int(match.group())
                            if set_brightness(level):
                                speak(f"Brightness adjusted to {level} percent, sir.")
                            else:
                                speak("I'm having trouble accessing the display driver, sir.")
                        elif "full" in query or "maximum" in query:
                            set_brightness(100)
                            speak("Brightness set to maximum capacity.")
                        elif "minimum" in query or "lowest" in query:
                            set_brightness(10)
                            speak("Brightness reduced to minimum levels.")

                    elif "meaning of" in query:
                        speak("Searching for the definition, sir.")
                        word = query.split("of")[-1].strip()
                        meaning = get_dictionary_meaning(word)
                        if meaning:
                            speak(f"Sir, the definition of {word} is: {meaning}")
                            eel.addTerminalLine(f"DEFINE: {word} -> {meaning[:50]}...")
                        else:
                            speak(f"I'm sorry sir, I couldn't find the definition for {word}.")

                    elif "take a screenshot" in query or "snapshot" in query:
                        path = take_screenshot()
                        if path:
                            speak("Screen captured, sir. Saved in Screenshots folder.")
                            eel.showNotification("Screenshot Saved", "success")
                        else:
                            speak("Sir, I was unable to capture the display.")

                    elif "tell me a joke" in query or "make me laugh" in query:
                        joke = get_joke()
                        speak(joke)

                    elif "latest news" in query or "news briefing" in query:
                        speak("Accessing the news uplink, sir. Here are the top headlines.")
                        headlines = get_latest_news()
                        for i, h in enumerate(headlines):
                            speak(f"Headline {i+1}: {h}")
                            eel.addTerminalLine(f"NEWS: {h[:60]}...")
                        speak("Briefing complete, sir.")

                    elif "give me some advice" in query or "advice" in query:
                        advice = get_advice()
                        speak(f"Sir, my advice to you is: {advice}")

                    elif "system scan" in query or "perform diagnostic" in query:
                        system_scan()

                    elif "go to sleep" in query or "shutdown" in query or "exit" in query:
                        hour = datetime.now().hour
                        if hour >= 21 or hour < 6:
                            speak("Good night Sir, take care!")
                        else:
                            speak("Have a productive day, sir!")
                        os._exit(0)
                        
                    else:
                        # AI Brain Fallback with Neural Memory
                        GROQ_KEY = config("GROQ_API_KEY", default="")
                        
                        if GROQ_KEY:
                            eel.addTerminalLine("Consulting Secondary Neural Hub (GROQ)...")
                            eel.showNotification("Groq Link Established", "success")
                            eel.setOrbState("processing")
                            
                            ai_answer = get_groq_response(query, chat_history=chat_history)
                            
                            # Update Conversation Memory
                            chat_history.append({"role": "user", "content": query})
                            chat_history.append({"role": "assistant", "content": ai_answer})
                            
                            # Keep only last 10 exchanges (20 messages) to save memory/tokens
                            if len(chat_history) > 20:
                                chat_history = chat_history[-20:]
                                
                            eel.setOrbState("default")
                            speak(ai_answer)
                        else:
                            # Fallback to Gemini with Cooldown Protection
                            current_time = time.time()
                            time_since_last = current_time - LAST_AI_TIME
                            
                            if time_since_last < COOLDOWN_PERIOD:
                                wait_needed = int(COOLDOWN_PERIOD - time_since_last)
                                speak(f"Sir, the primary neural brain is cooling down. Please wait {wait_needed} seconds or configure the GROQ key for instant responses.")
                                eel.addTerminalLine(f"COOLDOWN: {wait_needed}s remaining")
                                continue

                            eel.addTerminalLine("Consulting Primary Neural Brain (GEMINI)...")
                            eel.showNotification("Gemini Link Established", "alert")
                            eel.setOrbState("processing")
                            
                            ai_answer = get_ai_response(query, chat_history=chat_history)
                            LAST_AI_TIME = time.time()
                            
                            # Update Conversation Memory
                            chat_history.append({"role": "user", "content": query})
                            chat_history.append({"role": "assistant", "content": ai_answer})
                            
                            if len(chat_history) > 20:
                                chat_history = chat_history[-20:]
                                
                            eel.setOrbState("default")
                            speak(ai_answer)
            
            except Exception as loop_e:
                print(f"Error in main loop: {loop_e}")
                eel.addTerminalLine(f"RECOVERY: Neural process error: {loop_e}")
                time.sleep(1)
                
    except Exception as fatal_e:
        print(f"Fatal error in logic thread: {fatal_e}")
        try:
            eel.addTerminalLine(f"FATAL SYSTEM FAILURE: {fatal_e}")
        except:
            pass

if __name__ == '__main__':
    # Project Synapse: Audio Reactive Thread
    threading.Thread(target=audio_reactive_thread, daemon=True).start()
    
    # Project Ghost & Kinetic: Vision Senses Thread
    threading.Thread(target=sensory_processing_thread, daemon=True).start()
    
    # Standard System Vitals
    threading.Thread(target=update_ui_vitals, daemon=True).start()
    
    # The Core AI Logic
    threading.Thread(target=start_jarvis_logic, daemon=True).start()
    
    # Start Eel (This blocks)
    try:
        eel.start('index.html', mode='chrome', size=(1200, 800))
    except (SystemExit, MemoryError, KeyboardInterrupt):
        pass

