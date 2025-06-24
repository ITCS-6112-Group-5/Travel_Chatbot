from flask import Flask, request, jsonify, send_from_directory
import os
from chatbot_core import Chatbot

app = Flask(__name__, static_folder='website', template_folder='website')

# Create single chatbot instance
chatbot = Chatbot()

@app.route('/')
def home():
    return send_from_directory('website', 'index.html')

@app.route('/<path:filename>')
def serve_static_files(filename):
    return send_from_directory('website', filename)

@app.route('/api/chat', methods=['POST'])
def chat_api():
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Use shared chatbot logic
        bot_response = chatbot.process_input(user_message)
        
        return jsonify({
            'response': bot_response,
            'status': 'success'
        })
    
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({
            'error': 'Something went wrong',
            'status': 'error'
        }), 500

@app.route('/api/health')
def health_check():
    return jsonify({'status': 'NaviBlu is running!'})

# Online Deployment
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)