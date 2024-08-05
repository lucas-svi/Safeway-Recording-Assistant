# Safeway Recording Assistant

Safeway Recording Assistant is a Python tool for Safeway support agents to retrieve, play, transcribe, and query company calls from Vonage.

## Setup Instructions

### Prerequisites

1. **OpenAI API Key**: You need to set your OpenAI API Key for transcription and query purposes.
2. **Function for OpenAI Requests**: Ensure you have a function in a separate program that handles requests to OpenAI.
3. **MP3 Recording Directory**: Obtain the full directory path of the MP3 recordings and update the necessary files with this path.
4. **Elasticsearch**: Set up an instance of Elasticsearch to run locally on your computer.

### Step-by-Step Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/lucas-svi/Safeway-Recording-Assistant.git
   cd Safeway-Recording-Assistant
2. **Set Your OpenAI API Key**:
In your environment variables, set the OpenAI API key:
  ```export OPENAI_API_KEY='your_openai_api_key'```
3. **Ensure you have a function in a separate program to handle OpenAI requests.**

4. **Update MP3 Recording Directory:**
Locate the files requiring the MP3 recording directory path and update them with the full directory path of your recordings.
5. **Set Up Elasticsearch:**
Download and install Elasticsearch from Elasticsearch Downloads.
6. **Start Elasticsearch:**
7. **Index Recordings:**
Run the indexing script to index all recordings:
```
python elastic_search_index.py
```
**Run Flask Application:**
Start the Flask application to handle queries:
```
python elastic_search_flask.py
```
**Querying Recordings:**
Once the Flask application is running, you can make requests to http://localhost:5000 using the following arguments:
```
date
time
caller_id
call_id
```
**Graphical User Interface:**

Open program.py to access the Tkinter interface, which allows you to:
1. Retrieve any recording.
2. Play recordings.
3. Transcribe and diarize audio.
4. Query the audio to understand the conversation between the customer and the support agent.
-> Example Requests
Retrieve a recording by date:
```
curl -X GET "http://localhost:5000/recordings?date=2024-08-01"
```

Use the Tkinter interface:
```python program.py```
