import json
import threading
import urllib.request
import urllib.error
from datetime import datetime

from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.utils import platform

KV = r"""
<JarvisRoot>:
    orientation: "vertical"
    padding: "16dp"
    spacing: "10dp"
    canvas.before:
        Color:
            rgba: 0.015, 0.045, 0.09, 1
        Rectangle:
            pos: self.pos
            size: self.size
    Label:
        text: "[b]J.A.R.V.I.S.[/b]"
        markup: True
        font_size: "30sp"
        color: 0.2, 0.85, 1, 1
        size_hint_y: None
        height: "55dp"
    Label:
        text: root.status
        color: 0.65, 0.85, 1, 1
        size_hint_y: None
        height: "34dp"
    TextInput:
        id: transcript
        text: root.output
        readonly: True
        multiline: True
        background_color: 0.03, 0.10, 0.17, 1
        foreground_color: 0.85, 0.95, 1, 1
        cursor_color: 0.2, 0.85, 1, 1
    TextInput:
        id: command
        hint_text: "Type a command or ask JARVIS..."
        multiline: False
        size_hint_y: None
        height: "48dp"
        on_text_validate: root.process_text(self.text)
    BoxLayout:
        size_hint_y: None
        height: "52dp"
        spacing: "8dp"
        Button:
            text: "🎙 SPEAK"
            background_color: 0.02, 0.45, 0.65, 1
            on_release: root.listen()
        Button:
            text: "SEND"
            background_color: 0.02, 0.35, 0.5, 1
            on_release: root.process_text(command.text)
    BoxLayout:
        size_hint_y: None
        height: "48dp"
        spacing: "8dp"
        Button:
            text: "HELP"
            on_release: root.help()
        Button:
            text: "FLASHLIGHT"
            on_release: root.torch()
        Button:
            text: "TIME"
            on_release: root.tell_time()
"""

class JarvisRoot(BoxLayout):
    status = StringProperty("SYSTEM ONLINE • Voice button to speak")
    output = StringProperty(
        "JARVIS: Hello. I am ready.\\n"
        "Try: open YouTube, open WhatsApp, flashlight, battery, time, or ask a question.\\n"
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api_key = ""  # Optional: set only for testing; don't share APKs containing secrets.
        self.speech_request_code = 7314
        if platform == "android":
            try:
                from android import activity
                activity.bind(on_activity_result=self.on_activity_result)
            except Exception as exc:
                self.add_line("Android voice setup: " + str(exc))

    def add_line(self, text):
        self.output += "\\n" + text
        self.ids.transcript.text = self.output
        self.ids.transcript.cursor = (0, 0)

    def speak(self, text):
        self.add_line("JARVIS: " + text)
        try:
            from plyer import tts
            tts.speak(text)
        except Exception:
            pass

    def listen(self):
        if platform != "android":
            self.speak("Voice recognition works in the Android APK.")
            return
        try:
            from jnius import autoclass
            from android import activity
            Intent = autoclass("android.content.Intent")
            RecognizerIntent = autoclass("android.speech.RecognizerIntent")
            intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH)
            intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL,
                            RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
            intent.putExtra(RecognizerIntent.EXTRA_PROMPT, "Speak to JARVIS")
            intent.putExtra(RecognizerIntent.EXTRA_MAX_RESULTS, 1)
            activity.startActivityForResult(intent, self.speech_request_code)
            self.status = "LISTENING • Speak now"
        except Exception as exc:
            self.speak("Could not start speech recognition. " + str(exc))

    def on_activity_result(self, request_code, result_code, data):
        if request_code != self.speech_request_code:
            return
        try:
            from jnius import autoclass
            Activity = autoclass("android.app.Activity")
            if result_code != Activity.RESULT_OK or data is None:
                self.status = "READY"
                return
            results = data.getStringArrayListExtra(
                autoclass("android.speech.RecognizerIntent").EXTRA_RESULTS
            )
            if results and results.size() > 0:
                phrase = str(results.get(0))
                self.ids.command.text = phrase
                self.process_text(phrase)
        except Exception as exc:
            self.speak("I could not read the voice result. " + str(exc))
        self.status = "READY"

    def launch_app(self, app):
        if platform != "android":
            self.speak("App launching is available in the Android APK.")
            return
        packages = {
            "whatsapp": "com.whatsapp",
            "youtube": "com.google.android.youtube",
            "chrome": "com.android.chrome",
            "maps": "com.google.android.apps.maps",
            "settings": "com.android.settings",
            "camera": "com.sec.android.app.camera",
            "phone": "com.samsung.android.dialer",
            "gallery": "com.sec.android.gallery3d",
            "play store": "com.android.vending",
        }
        package = packages.get(app.strip().lower())
        if not package:
            self.speak("I don't have a shortcut for " + app)
            return
        try:
            from jnius import autoclass
            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            activity = PythonActivity.mActivity
            intent = activity.getPackageManager().getLaunchIntentForPackage(package)
            if intent is None:
                self.speak(app + " does not appear to be installed.")
                return
            activity.startActivity(intent)
            self.speak("Opening " + app)
        except Exception as exc:
            self.speak("Could not open " + app + ". " + str(exc))

    def torch(self):
        if platform != "android":
            self.speak("Flashlight control is available on Android.")
            return
        try:
            from jnius import autoclass
            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            Context = autoclass("android.content.Context")
            camera = PythonActivity.mActivity.getSystemService(Context.CAMERA_SERVICE)
            ids = camera.getCameraIdList()
            if ids and ids.size() > 0:
                camera.setTorchMode(ids.get(0), True)
                self.speak("Flashlight turned on.")
            else:
                self.speak("No camera flashlight was found.")
        except Exception as exc:
            self.speak("Flashlight control failed. " + str(exc))

    def tell_time(self):
        self.speak(datetime.now().strftime("It is %I:%M %p, %A %d %B."))

    def help(self):
        self.speak("Try open WhatsApp, open YouTube, flashlight, time, battery, or ask me a question.")

    def process_text(self, text):
        text = (text or "").strip()
        if not text:
            return
        self.ids.command.text = ""
        self.add_line("YOU: " + text)
        low = text.lower()
        if low.startswith("open "):
            self.launch_app(low[5:])
        elif "time" in low or "waqt" in low:
            self.tell_time()
        elif "flashlight" in low or "torch" in low or "torch on" in low:
            self.torch()
        elif "battery" in low or "charge" in low:
            self.speak("Battery percentage is not yet connected in this prototype. It can be added with a native Android battery API.")
        elif low in ("help", "commands"):
            self.help()
        else:
            self.ask_ai(text)

    def ask_ai(self, prompt):
        if not self.api_key:
            self.speak("AI chat needs a secure AI API connection. For now, I can run the built-in phone commands.")
            return
        self.status = "THINKING..."
        threading.Thread(target=self._ai_request, args=(prompt,), daemon=True).start()

    def _ai_request(self, prompt):
        try:
            payload = {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": "You are JARVIS, a helpful concise assistant. Reply in the user's language."},
                    {"role": "user", "content": prompt}
                ]
            }
            req = urllib.request.Request(
                "https://api.openai.com/v1/chat/completions",
                data=json.dumps(payload).encode(),
                headers={"Authorization": "Bearer " + self.api_key,
                         "Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=30) as response:
                data = json.loads(response.read().decode())
            answer = data["choices"][0]["message"]["content"]
            Clock.schedule_once(lambda dt: self.speak(answer))
        except Exception as exc:
            Clock.schedule_once(lambda dt: self.speak("AI connection error: " + str(exc)))
        finally:
            Clock.schedule_once(lambda dt: setattr(self, "status", "READY"))

class JarvisApp(App):
    def build(self):
        Builder.load_string(KV)
        return JarvisRoot()

if __name__ == "__main__":
    JarvisApp().run()
