from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/message', methods=['POST'])
def handle_message():
    user_message = request.json.get('message')
    return jsonify({"response": f"You said: {user_message}"})

if __name__ == '__main__':
    app.run(debug=True)
