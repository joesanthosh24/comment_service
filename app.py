# comment_service.py

from flask import Flask, jsonify, request
import requests
import uuid

app = Flask(__name__)

comments = {
    '1': {'user_id': '1', 'post_id': '2', 'comment': 'Amazing post!'},
    '2': {'user_id': '2', 'post_id': '2', 'comment': 'I did not know that'}
}

userservice_api_url = 'https://userservicecontainerapp--nsd4hlx.purplemoss-ca6cdeba.canadacentral.azurecontainerapps.io'
postservice_api_url = 'https://postservicecontainerapp--7qozew4.purplemoss-ca6cdeba.canadacentral.azurecontainerapps.io'

@app.route('/')
def hello():
    return "Hello, welcome to the comment service"

@app.route('/comment/<id>')
def comment(id):
    comment_info = comments.get(id, {})
    user = {}
    post = {}

    if comment_info:
        user_response = requests.get(
            f'{userservice_api_url}/user/{comment_info["user_id"]}'
        )
        if user_response.status_code == 200:
            user = user_response.json()
        
        post_response = requests.get(
            f'{postservice_api_url}/post/{comment_info["post_id"]}'
        )
        if post_response.status_code == 200:
            post = post_response.json()

    return jsonify({
        'comment': comment_info,
        'user': user,
        'post': post
    })

@app.route('/comment', methods=['POST'])
def create_comment():
    data = request.json
    user_id = data.get('user_id')
    post_id = data.get('post_id')

    user_response = requests.get(f'{userservice_api_url}/user/{user_id}')
    post_response = requests.get(f'{postservice_api_url}/post/{post_id}')

    if user_response.status_code == 200 and post_response.status_code == 200:
        comment = data.get('comment')
        new_comment_id = str(uuid.uuid1())
        comments[new_comment_id] = { 'user_id': str(user_id), 'post_id': str(post_id), 'comment': comment }

        return jsonify({
            'new_comment': comments[new_comment_id],
            'all_comments': comments
        })
    
    return jsonify('User or post do not exist')

@app.route('/comment/<id>', methods=['PUT'])
def update_comment(id):
    comment_ids = list(comments.keys())

    if id in comment_ids:
        user = {}
        post = {}

        data = request.json
        updated_comment = data.get('comment')

        comments[id]['comment'] = updated_comment

        user_response = requests.get(
            f'{userservice_api_url}/user/{comments[id]["user_id"]}'
        )
        if user_response.status_code == 200:
            user = user_response.json()
        
        post_response = requests.get(
            f'{postservice_api_url}/post/{comments[id]["post_id"]}'
        )
        if post_response.status_code == 200:
            post = post_response.json()

        return jsonify({
            'updated_comment': comments[id],
            'user': user,
            'post': post,
        })
    
    return jsonify('No comment with that id')

@app.route('/comment/<id>', methods=['DELETE'])
def delete_comment(id):
    comment_ids = list(comments.keys())

    if id in comment_ids:
        comment_to_delete = comments[id]
        comments.pop(id)

        return jsonify({
            'deleted_comment': comment_to_delete,
            'all_comments': comments
        })
    
    return jsonify('No comment with that id')

if __name__ == '__main__':
    app.run(port=5003)