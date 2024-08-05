import glob
import os
import json
from datetime import datetime, timedelta

from pydub import AudioSegment

from audio_processor import process_audio_gpt4o

directory = r'C:\Users\Dismissive\Desktop\Safeway\Recordings'


def find_recordings(phone_number='', date='', time=''):
    recordings = glob.glob(os.path.join(directory, "*.mp3"))
    if phone_number or date or time:
        if phone_number:
            recordings = [rec for rec in recordings if phone_number in rec]
        if date:
            recordings = [rec for rec in recordings if date in rec]
        if time:
            recordings = [rec for rec in recordings if time in rec]
    return recordings


def edit_transcription_json(file_mp3):
    file_json = file_mp3.replace(".mp3", ".json")
    data = {}
    if os.path.exists(file_json):
        with open(file_json, 'r') as file:
            try:
                data = json.load(file)
            except json.decoder.JSONDecodeError:
                data = {}

    if 'recordings' in data and data['recordings']:
        return data['recordings']
    else:
        transcription = f"{process_audio_gpt4o(file_mp3)}"
        data['transcription'] = transcription
        with open(file_json, 'w') as file:
            json.dump(data, file, indent=4)
        return transcription


def process_files(directory):
    for filename in os.listdir(directory):
        if filename.endswith('.mp3'):
            if "." in filename.split(".mp3")[0]:
                continue
            #print(filename)
            parts = filename.split('_')
            timestamp_str = parts[1]
            direction = parts[2]
            phone_number_1 = parts[3]
            phone_number_2 = parts[4]
            timestamp = datetime.strptime(timestamp_str[:14], "%Y%m%d%H%M%S")
            new_timestamp = timestamp - timedelta(hours=4)
            formatted_date = new_timestamp.strftime("%m.%d.%y_%I.%M.%S%p").upper().replace(' ', '')
            new_filename = f"{formatted_date}_{direction}_{phone_number_1}_{phone_number_2}.mp3"
            new_filepath = os.path.join(directory, new_filename)
            old_filepath = os.path.join(directory, filename)

            audio = AudioSegment.from_mp3(old_filepath)
            duration_in_minutes = len(audio) / (1000 * 60)
            split_min = 15
            if duration_in_minutes > split_min:
                number_of_parts = int(duration_in_minutes // split_min) + 1
                for part in range(number_of_parts):
                    start_time = part * split_min * 60 * 1000
                    end_time = (part + 1) * split_min * 60 * 1000 if (part + 1) * split_min * 60 * 1000 < len(audio) else len(audio)
                    audio_part = audio[start_time:end_time]
                    part_filename = f"{formatted_date}_{direction}_{phone_number_1}_{phone_number_2}_PART{part + 1}.mp3"
                    part_filepath = os.path.join(directory, part_filename)
                    audio_part.export(part_filepath, format="mp3")

                    json_filename = part_filename.replace('.mp3', '.json')
                    json_filepath = os.path.join(directory, json_filename)
                    with open(json_filepath, 'w') as json_file:
                        json.dump({
                            "date": new_timestamp.strftime("%B %d %y"),
                            "time": new_timestamp.strftime("%I:%M:%S%p").upper().replace(' ', ''),
                            "direction": direction,
                            "from": phone_number_1,
                            "to": phone_number_2,
                            "transcription": None
                        }, json_file, indent=4)

                    print(f"Created {part_filename} and {json_filename}")
                os.remove(old_filepath)
                print(f"Deleted original file {filename}")
            else:
                os.rename(old_filepath, new_filepath)
                json_filename = new_filename.replace('.mp3', '.json')
                json_filepath = os.path.join(directory, json_filename)
                with open(json_filepath, 'w') as json_file:
                    json.dump({
                        "date": new_timestamp.strftime("%B %d %y"),
                        "time": new_timestamp.strftime("%I:%M:%S%p").upper().replace(' ', ''),
                        "direction": direction,
                        "from": phone_number_1,
                        "to": phone_number_2,
                        "transcription": None
                    }, json_file, indent=4)

                print(f"Renamed {filename} to {new_filepath} and created {json_filename}")

process_files(directory)