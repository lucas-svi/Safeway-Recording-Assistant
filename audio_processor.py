import atexit
import os
import shutil
import time

from openAI.openAI import askWhisper, askGPT

segments_dir = ''


def cleanup():
    if os.path.exists(segments_dir):
        try:
            shutil.rmtree(segments_dir)
            print(f"Deleted the directory: {segments_dir}")
        except Exception as e:
            print(f"Error during cleanup: {e}")


atexit.register(cleanup)

def get_full_sentence(transcription):
    if not transcription:
        return None
    sentence = ' '.join([word['word'] for word in transcription if word['word'] != ''])
    return sentence.strip() if sentence else None

def process_audio_gpt4o(file):
    file = file.replace(".json", ".mp3")
    start_time = time.time()
    transcription = askWhisper(rf'{file}', False, False)
    full_transcription = get_full_sentence(transcription)
    #print(full_transcription)
    diarize_request = askGPT("Your task is to differentiate and diarize a conversation between a customer support agent from Safeway Moving Systems and a customer. If a voice recording is just an automated message, please do not diarize anything and simply return the same exact message WITHOUT INCLUDING ANYTHING ELSE. You must always return the transcription with no further dialogue from yourself. Use clear labels to identify the speaker in each part of the conversation.",
                             f"Please differentiate and diarize the conversation (or leave it alone if it's an automated message), clearly labeling each speaker as 'Customer Support Agent' or 'Customer', and separating messages with new lines: {full_transcription}")

    elapsed_time = time.time() - start_time
    print(f"Elapsed time for {file}: {elapsed_time:.2f} seconds")
    return diarize_request.replace("*", "")
    #print(f"Elapsed time: {elapsed_time:.2f} seconds")
