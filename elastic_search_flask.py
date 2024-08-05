from flask import Flask, request, jsonify
from elasticsearch import Elasticsearch

app = Flask(__name__)
es = Elasticsearch([{'host': 'localhost', 'port': 9200, 'scheme': 'http'}])


@app.route('/search', methods=['GET'])
def search_recordings():
    date = request.args.get('date')
    time = request.args.get('time')
    caller_id = request.args.get('caller_id')
    call_id = request.args.get('call_id')

    query = {
        'query': {
            'bool': {
                'must': []
            }
        }
    }

    if date:
        query['query']['bool']['must'].append({'match': {'date': date}})
    if time:
        query['query']['bool']['must'].append({'match': {'time': time}})
    if caller_id:
        query['query']['bool']['must'].append({'match': {'caller_id': caller_id}})
    if call_id:
        query['query']['bool']['must'].append({'match': {'call_id': call_id}})

    if not query['query']['bool']['must']:
        return jsonify({'error': 'At least one search parameter (date, time, caller_id, or call_id) is required'}), 400

    response = es.search(index='recordings', body=query)
    results = [{'file_path': hit['_source'][r'file_path'], 'took': f'{response["took"]}ms'} for hit in
               response['hits']['hits']]

    return jsonify(results)


@app.route('/all', methods=['GET'])
def get_all_recordings():
    response = es.search(index='recordings', body={"query": {"match_all": {}}}, size=50)
    results = [{'file_path': hit['_source']['file_path'], 'took': f'{response["took"]}ms'} for hit in
               response['hits']['hits']]
    return jsonify(results)


if __name__ == '__main__':
    app.run(debug=True)
