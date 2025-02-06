import json
from flask import Flask, jsonify, request, send_from_directory
import rota as rotaeno

app = Flask(__name__)

def get_user_data(userID):
    if not userID:
        return None, jsonify({'error': 'userID is required'}), 400
    
    with open('users.json', 'r') as file:
        users = json.load(file)
    
    if userID not in users:
        return None, jsonify({'error': 'userID not found'}), 400
    
    return users[userID], None, None

@app.route('/img/<path:filename>', methods=['GET'])
def img(filename):
    return send_from_directory('img', filename)

@app.route('/web/Best40', methods=['GET'])
def Best40():
    userID = request.args.get('userID')
    user_data, error_response, status_code = get_user_data(userID)
    if error_response:
        return error_response, status_code
    
    return rotaeno.getBest40(user_data, justHTML=True)

@app.route('/web/Song', methods=['GET'])
def Song():
    userID = request.args.get('userID')
    songID = request.args.get('songID')
    
    if not songID:
        return jsonify({'error': 'songID is required'}), 400
    
    user_data, error_response, status_code = get_user_data(userID)
    if error_response:
        return error_response, status_code
    
    return rotaeno.getSong(user_data, songID, justHTML=True)

@app.route('/api/getBest40', methods=['GET'])
def getBest40():
    userID = request.args.get('userID')
    user_data, error_response, status_code = get_user_data(userID)
    if error_response:
        return error_response, status_code
    
    return jsonify(rotaeno.getBest40(user_data, justDATA=True))

@app.route('/api/getSong', methods=['GET'])
def getSong():
    userID = request.args.get('userID')
    songID = request.args.get('songID')
    
    if not songID:
        return jsonify({'error': 'songID is required'}), 400
    
    user_data, error_response, status_code = get_user_data(userID)
    if error_response:
        return error_response, status_code
    
    return jsonify(rotaeno.getSong(user_data, songID, justDATA=True))

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
