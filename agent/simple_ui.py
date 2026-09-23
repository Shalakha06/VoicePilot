"""
VoicePilot Minimal HUD - Clean Push-to-Talk Remote
Zero dependencies on complex loops or timers. Pure interactive button control.
"""
import threading
import numpy as np
import sounddevice as sd
import customtkinter as ctk

from agent.speech.stt import SpeechToText, get_real_mic_device
from agent.speech.tts import TextToSpeech
from agent.brain.llm import LLMBrain
from agent.tools.executor import ToolExecutor
from agent.memory.context import ShortTermMemory

# ── PALETTE ───────────────────────────────────────────────────────────
BG_COLOR = "#0A0912"
CARD_COLOR = "#131122"
BORDER_COLOR = "#25213B"
TEXT_COLOR = "#F8FAFC"
MUTED_COLOR = "#94A3B8"
ACCENT_IDLE = "#8B5CF6"      # Purple
ACCENT_REC = "#EF4444"       # Red
ACCENT_THINK = "#F59E0B"     # Amber


class VoicePilotMiniHUD(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("VoicePilot Mini")
        self.geometry("480x420")
        self.resizable(False, False)
        self.configure(fg_color=BG_COLOR)
        ctk.set_appearance_mode("dark")

        # Keep on top so you can interact with other apps while using it
        self.attributes("-topmost", True)

        # ── INITIALIZE BACKEND ENGINES ────────────────────────────────
        self.stt = SpeechToText()
        self.tts = TextToSpeech()
        self.brain = LLMBrain()
        self.executor = ToolExecutor()
        self.memory = ShortTermMemory(max_turns=5)

        # Audio Stream Recording State
        self.is_recording = False
        self.is_processing = False
        self.recorded_chunks = []
        self.stream = None

        self._build_ui()

        # Keyboard hotkey: Press Spacebar anywhere on the window to toggle Mic
        self.bind("<space>", lambda e: self.toggle_mic())

        threading.Thread(target=lambda: self.tts.speak("VoicePilot online."), daemon=True).start()

    def _build_ui(self):
        # ── HEADER ───────────────────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(16, 8))

        ctk.CTkLabel(
            header, text="⚡ VoicePilot",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color=TEXT_COLOR
        ).pack(side="left")

        self.status_pill = ctk.CTkLabel(
            header, text="● READY",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#10B981", fg_color="#064E3B", corner_radius=12, padx=10, pady=3
        )
        self.status_pill.pack(side="right")

        # ── BIG INTERACTIVE MIC BUTTON ───────────────────────────────
        self.mic_btn = ctk.CTkButton(
            self, text="🎙️ TAP TO SPEAK (Space)",
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            fg_color=ACCENT_IDLE, hover_color="#7C3AED", text_color="#FFFFFF",
            corner_radius=14, height=56, command=self.toggle_mic
        )
        self.mic_btn.pack(fill="x", padx=20, pady=10)

        # ── LIVE SPOKEN / STATUS PREVIEW ─────────────────────────────
        self.status_label = ctk.CTkLabel(
            self, text='"Click button or hit Spacebar to start speaking."',
            font=ctk.CTkFont(family="Segoe UI", size=12, slant="italic"),
            text_color=MUTED_COLOR, wraplength=440, justify="center"
        )
        self.status_label.pack(fill="x", padx=20, pady=(0, 10))

        # ── LIVE EXECUTION LOG BOX ───────────────────────────────────
        log_frame = ctk.CTkFrame(self, fg_color=CARD_COLOR, border_width=1, border_color=BORDER_COLOR, corner_radius=10)
        log_frame.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        self.log_box = ctk.CTkTextbox(
            log_frame, corner_radius=8,
            font=ctk.CTkFont(family="Consolas", size=11),
            fg_color="#07060E", text_color="#E2E8F0"
        )
        self.log_box.pack(fill="both", expand=True, padx=8, pady=8)
        self.log_box.configure(state="disabled")
        self.log("VoicePilot initialized. Push button to speak.")

    def log(self, text: str):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", text + "\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    # ── PUSH-TO-TALK LOGIC ───────────────────────────────────────────
    def toggle_mic(self):
        if self.is_processing:
            return

        if not self.is_recording:
            # START RECORDING
            self.is_recording = True
            self.recorded_chunks = []
            self.mic_btn.configure(text="⏹️ STOP & PROCESS (Space)", fg_color=ACCENT_REC, hover_color="#DC2626")
            self.status_pill.configure(text="● LISTENING...", text_color="#F43F5E", fg_color="#4C0519")
            self.status_label.configure(text='"Listening... speak naturally, click Stop when done."')

            # Start hardware audio stream
            threading.Thread(target=self._audio_capture_stream, daemon=True).start()
        else:
            # STOP RECORDING & EXECUTE PIPELINE
            self.is_recording = False
            self.mic_btn.configure(text="⏳ Processing...", fg_color=ACCENT_THINK, state="disabled")
            self.status_pill.configure(text="● THINKING...", text_color="#F59E0B", fg_color="#451A03")

    def _audio_capture_stream(self):
        def callback(indata, frames, time_info, status):
            if self.is_recording:
                self.recorded_chunks.append(indata.copy())

        mic_index = get_real_mic_device()
        try:
            with sd.InputStream(samplerate=16000, channels=1, dtype='float32', device=mic_index, callback=callback):
                while self.is_recording:
                    sd.sleep(50)
        except Exception as e:
            self.log(f"[AUDIO ERROR]: {e}")

        # When recording turns False, process the recorded buffer
        threading.Thread(target=self._process_captured_audio, daemon=True).start()

    def _process_captured_audio(self):
        self.is_processing = True
        try:
            if not self.recorded_chunks:
                self._reset_ui("No audio captured. Try again.")
                return

            audio = np.concatenate(self.recorded_chunks, axis=0).flatten()

            # Normalization
            peak = float(np.max(np.abs(audio))) if audio.size > 0 else 0.0
            if peak < 0.0005:
                self._reset_ui("Pure silence captured. Try again.")
                return

            audio = audio * (0.70 / max(peak, 0.01))

            # 1. Faster-Whisper
            self.status_label.configure(text='"Transcribing speech..."')
            segments, _ = self.stt.whisper.transcribe(audio, beam_size=5, temperature=0.0, language="en")
            user_text = " ".join([s.text for s in segments]).strip()

            if not user_text:
                self._reset_ui("Could not transcribe words clearly.")
                return

            self.log(f"\n[USER]: \"{user_text}\"")
            self.status_label.configure(text=f'"{user_text}"')

            # 2. Plan via LLM + Memory
            context_summary = self.memory.get_context_summary()
            plan = self.brain.plan(user_text, context=context_summary)
            self.log(f"[THOUGHT]: {plan.thought}")

            # 3. Spoken feedback
            if plan.spoken_response:
                self.status_label.configure(text=f'"{plan.spoken_response}"')
                threading.Thread(target=lambda: self.tts.speak(plan.spoken_response), daemon=True).start()

            # 4. Tool Execution
            if plan.steps:
                self.status_pill.configure(text="● EXECUTING...", text_color="#A855F7", fg_color="#3B0764")
                results = self.executor.execute_plan(plan)
                for res in results:
                    msg = res.get('result', {}).get('message', 'Done')
                    self.log(f"[TOOL]: {msg}")

            # 5. Record Memory
            self.memory.record_turn(
                user_command=user_text,
                thought=plan.thought,
                steps=[s.model_dump() for s in plan.steps],
                spoken=plan.spoken_response
            )

        except Exception as e:
            self.log(f"[ERROR]: {e}")
        finally:
            self._reset_ui()

    def _reset_ui(self, message: str = ""):
        self.is_processing = False
        self.is_recording = False
        self.mic_btn.configure(state="normal", text="🎙️ TAP TO SPEAK (Space)", fg_color=ACCENT_IDLE)
        self.status_pill.configure(text="● READY", text_color="#10B981", fg_color="#064E3B")
        if message:
            self.status_label.configure(text=f'"{message}"')


if __name__ == "__main__":
    app = VoicePilotMiniHUD()
    app.mainloop()