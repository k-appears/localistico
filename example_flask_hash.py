import hashlib
from collections import defaultdict

from flask import Flask, request

app = Flask(__name__)

hashtable = defaultdict(list)


@app.route('/api/add_url/', methods=['POST'])
def add_url():
    # Use validation package for url parameter
    url = request.get_json()['url']
    sha = hashlib.sha256()
    sha.update(url.encode())
    key = sha.hexdigest()
    hashtable[key].append(url)
    return key


@app.route('/api/add_url/<key>', methods=['GET'])
def get_url(key):
     hashtable[key]

if __name__ == '__main__':
    app.run()
