from flask import Flask, request, jsonify

from borisBlogs.safeway.src import handler

app = Flask(__name__)


@app.route('/search', methods=['POST'])
def search():
    try:
        data = request.get_json()
        print("Received request data:", data)
        phone_number = data['phone_number']
        date = data['date']
        time = data['time']
        data['recordings'] = handler.find_recordings(phone_number, date, time)
        return data
    except Exception as e:
        print("Error: ", (str(e)))
        return jsonify({'error': 'internal server error'}, 500)


app.run(debug=True)
