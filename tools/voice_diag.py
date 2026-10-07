import speech_recognition as sr
import sounddevice as sd
from app.config import config
from app.logging_config import logger

def diagnose_voice():
    print("\n=== OMEN Voice Diagnostic Tool ===")
    
    # 1. List all audio devices
    print("\n[1] Scanning for audio devices...")
    try:
        devices = sd.query_devices()
        print("\nAvailable Audio Devices:")
        print(devices)
        
        # Try to find the default input device
        default_input = sd.query_devices(kind='input')
        print(f"\nDefault Input Device Index: {default_input['index']}")
    except Exception as e:
        print(f"Error scanning devices: {e}")

    # 2. Test the current config
    print("\n[2] Testing current config...")
    print(f"Current Mic Index: {config.microphone_index}")
    print(f"Current Energy Threshold: {config.stt_energy_threshold}")
    
    try:
        recognizer = sr.Recognizer()
        mic = sr.Microphone(device_index=config.microphone_index)
        with mic as source:
            print("\n>>> PLEASE STAY SILENT for 2 seconds to calibrate background noise...")
            recognizer.adjust_for_ambient_noise(source, duration=2)
            actual_threshold = recognizer.energy_threshold
            print(f"Calculated Background Energy: {actual_threshold}")
            
            if actual_threshold > config.stt_energy_threshold:
                print(f"⚠️ WARNING: Your background noise ({actual_threshold}) is HIGHER than your threshold ({config.stt_energy_threshold}).")
                print("You will likely see 'no speech detected'.")
            else:
                print("✅ Background noise level is within acceptable limits.")
                
            print("\n>>> NOW SPEAK SOMETHING (e.g., 'Hello OMEN')...")
            try:
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
                print("✓ Audio captured! Attempting transcription...")
                text = recognizer.recognize_google(audio)
                print(f"✓ Success! I heard: '{text}'")
            except sr.WaitTimeoutError:
                print("❌ Error: No speech detected within 5 seconds.")
            except sr.UnknownValueError:
                print("❌ Error: Audio captured but could not be understood (Check mic quality).")
            except Exception as e:
                print(f"❌ Unexpected error: {e}")

    except Exception as e:
        print(f"❌ Microphone Error: {e}")
        print("\nTIP: Try changing 'microphone_index' in your config to match one of the indices listed in Step 1.")

if __name__ == "__main__":
    diagnose_voice()
