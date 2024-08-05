import json
import os
import tempfile
import tkinter as tk
from tkinter import simpledialog, messagebox

import requests
from pydub import AudioSegment

from borisBlogs.safeway.src import handler
from openAI.openAI import askGPT

temp_files = []


def search_query():
    query = {
        field.lower().replace(" ", "_").split("_(")[0]: entry.get() for field, entry in entries.items()
    }

    try:
        response = requests.post('http://localhost:5000/search', json=query)
        response.raise_for_status()
        result = response.json()
        display_result(result['recordings'])
    except requests.exceptions.RequestException as e:
        print(f"HTTP request failed: {e}")
        display_result([f"An error occurred: {e}"])
    except ValueError as e:
        print(f"ValueError: {e}")
        display_result([f"An error occurred: {e}"])
    except Exception as e:
        print(f"Unexpected error: {e}")
        display_result([f"An error occurred: {e}"])


def has_transcription(recording):
    json_recording = f"{os.path.splitext(recording)[0]}.json"
    return os.path.exists(json_recording) and json.load(open(json_recording)).get('transcription')


def display_result(recordings):
    clear_frame(result_frame)
    if transcription_var.get():
        recordings = [rec for rec in recordings if has_transcription(rec)]
    if not recordings:
        tk.Label(result_frame, text="No recordings found.").pack(anchor='w')
        return
    if "error" in recordings[0]:
        tk.Label(result_frame, text="Error found. Server might be having trouble.").pack(anchor='w')
        return

    tk.Label(result_frame, text=f"Recordings found ({len(recordings)}):").pack(anchor='w')
    for recording in recordings:
        create_recording_frame(recording)


def get_audio_duration(file_path):
    minutes, seconds = divmod(int(AudioSegment.from_file(file_path).duration_seconds), 60)
    return f"({minutes}m:{seconds}s)"


def create_recording_frame(recording):
    frame = tk.Frame(result_frame)
    frame.pack(fill='x', padx=5, pady=5)
    duration = get_audio_duration(recording)
    tk.Label(frame, text=f"{duration} {recording}", wraplength=400).pack(side='left', fill='x', expand=True)
    json_recording = f"{os.path.splitext(recording)[0]}.json"
    play_button = tk.Button(frame, text="Play", command=lambda: play_recording(recording))
    play_button.pack(side='right')
    if has_transcription(recording):
        create_transcription_controls(frame, json_recording)
    else:
        transcribe_button = tk.Button(frame, text="Transcribe",
                                      command=lambda: transcribe_recording(recording, frame, transcribe_button))
        transcribe_button.pack(side='right')


def create_transcription_controls(frame, json_recording):
    link = tk.Label(frame, text="View Transcription", fg="blue", cursor="hand2")
    link.pack(side='left')
    link.bind("<Button-1>", lambda e: view_transcription(json_recording))
    tk.Button(frame, text="Prompt", command=lambda: prompt_user(json_recording)).pack(side='right')


def view_transcription(json_recording):
    transcription = json.load(open(json_recording))['transcription']
    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode='w') as temp_file:
        temp_file.write(transcription)
    temp_files.append(temp_file.name)
    os.system(f'start {temp_file.name}')


def transcribe_recording(recording, frame, transcribe_button):
    json_recording = f"{os.path.splitext(recording)[0]}.json"
    handler.edit_transcription_json(recording)
    replace_transcribe_with_prompt(frame, json_recording, transcribe_button)
    messagebox.showinfo("Complete!", "Transcription is complete. Please press 'View Transcription'")


def replace_transcribe_with_prompt(frame, json_recording, transcribe_button):
    transcribe_button.destroy()
    create_transcription_controls(frame, json_recording)


def prompt_user(json_recording):
    user_input = simpledialog.askstring("Input", "Enter your prompt:")
    if user_input:
        messagebox.showinfo("Prompt", askGPT("You analyze a dialog between a conversation from a Customer Support "
                                             "Agent at Safeway Moving Systems, and a customer. You are given a prompt "
                                             "and a transcription, and you provide an answer based on the "
                                             "transcription and what the question is asking of you.",
                                             f"Prompt: {user_input}\nTranscription: {json.load(open(json_recording))['transcription']}"))


def play_recording(recording):
    os.system(f'start {recording}')


def reset_fields():
    for entry in entries.values():
        entry.delete(0, tk.END)
    clear_frame(result_frame)


def clear_frame(frame):
    for widget in frame.winfo_children():
        widget.destroy()


def on_closing():
    for file in temp_files:
        try:
            os.remove(file)
        except Exception as e:
            print(f"Error deleting temporary file {file}: {e}")
    root.destroy()


root = tk.Tk()
root.title("Customer Support Search")

fields = ['Phone Number', 'Date (MM.DD.YY)', 'Time (HH.MM.SS)']
entries = {}

for i, field in enumerate(fields):
    tk.Label(root, text=field).grid(row=i, column=0, padx=10, pady=5, sticky='e')
    entry = tk.Entry(root)
    entry.grid(row=i, column=1, padx=10, pady=5, sticky='ew')
    entries[field] = entry

transcription_var = tk.BooleanVar()
transcription_checkbox = tk.Checkbutton(root, text="Available Transcriptions", variable=transcription_var)
transcription_checkbox.grid(row=len(fields), column=0, columnspan=2, pady=5, sticky='ew')

tk.Button(root, text='Search', command=search_query).grid(row=len(fields) + 1, column=0, columnspan=2, pady=10,
                                                          sticky='ew')
tk.Button(root, text='Reset', command=reset_fields).grid(row=len(fields) + 2, column=0, columnspan=2, pady=10,
                                                         sticky='ew')
tk.Button(root, text='Quit', command=on_closing).grid(row=len(fields) + 3, column=0, columnspan=2, pady=10, sticky='ew')

canvas = tk.Canvas(root)
result_frame = tk.Frame(canvas)
scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
canvas.configure(yscrollcommand=scrollbar.set)

scrollbar.grid(row=len(fields) + 4, column=2, sticky='ns')
canvas.grid(row=len(fields) + 4, column=0, columnspan=2, padx=10, pady=10, sticky='nsew')
canvas.create_window((0, 0), window=result_frame, anchor='nw')

result_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

root.rowconfigure(len(fields) + 4, weight=3)
root.columnconfigure(1, weight=3)

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()
