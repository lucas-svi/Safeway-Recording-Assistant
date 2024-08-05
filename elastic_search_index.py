import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from elasticsearch import Elasticsearch
import os

es = Elasticsearch(
    [{'host': 'localhost', 'port': 9200, 'scheme': 'http'}]
)
index_all = False
DIRECTORY_TO_WATCH = r'C:\Users\Dismissive\Desktop\Safeway\Recordings'


class Watcher:

    def __init__(self):
        self.observer = Observer()

    def run(self):
        if index_all:
            index_handler()
        event_handler = Handler()
        self.observer.schedule(event_handler, DIRECTORY_TO_WATCH, recursive=True)
        self.observer.start()
        try:
            while True:
                time.sleep(5)
        except:
            self.observer.stop()
            print("Observer Stopped")

        self.observer.join()


def index(file_name, file_path):
    parts = file_name.split('_')
    if len(parts) == 4:
        date = parts[0]
        time = parts[1]
        caller_id = parts[2]
        call_id = parts[3].replace('.mp3', '')
        doc_id = f"{date}_{time}_{caller_id}_{call_id}"
        if not es.exists(index='recordings', id=doc_id):
            doc = {
                'date': date,
                'time': time,
                'caller_id': caller_id,
                'call_id': call_id,
                'file_path': file_path
            }
            es.index(index='recordings', id=doc_id, body=doc)
            print(f"Indexed file: {file_name}")
        else:
            print(f"File already indexed: {file_name}")


def index_handler():
    for root, _, files in os.walk(DIRECTORY_TO_WATCH):
        for file in files:
            if file.endswith(".mp3"):
                file_path = os.path.join(root, file)
                index(file, file_path)
    print("Finished indexing files.")


class Handler(FileSystemEventHandler):

    @staticmethod
    def process(event):
        """
        event.event_type
            'modified' | 'created' | 'moved' | 'deleted'
        event.src_path
            path to the changed file
        """
        if event.event_type == 'created' and event.src_path.endswith(".mp3"):
            index(os.path.basename(event.src_path), event.src_path)

    def on_created(self, event):
        self.process(event)

    def on_modified(self, event):
        self.process(event)


if __name__ == '__main__':
    index_all = True
    # es.indices.delete(index='recordings')
    w = Watcher()
    w.run()
