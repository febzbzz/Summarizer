from flask import Flask, render_template, request, jsonify
from newspaper import Article
import nltk
import uuid  # For unique IDs
import sqlite3  # For SQLite database

nltk.download("punkt")

app = Flask(__name__)

# Store summarized news in a list
summaries = []

# Initialize the SQLite database and create the table if it doesn't exist
def init_db():
    conn = sqlite3.connect('contact_info.db')  # Connect to SQLite database (it will be created if it doesn't exist)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS messages (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    message TEXT NOT NULL)''')  # Table to store contact info
    conn.commit()
    conn.close()

# Call init_db() to create the database and table when the app starts
init_db()

# Function to store messages in the SQLite database
def store_message(name, email, message):
    conn = sqlite3.connect('contact_info.db')
    c = conn.cursor()
    c.execute("INSERT INTO messages (id, name, email, message) VALUES (?, ?, ?, ?)",
              (str(uuid.uuid4()), name, email, message))  # Generate unique ID
    conn.commit()
    conn.close()

def summarize_article(url):
    """Extract and summarize an article from a given URL."""
    try:
        article = Article(url)
        article.download()
        article.parse()
        article.nlp()
        return article.title, article.summary
    except Exception as e:
        return None, f"Error: {e}"

@app.route("/", methods=["GET", "POST"])
def home():
    global summaries
    if request.method == "POST":
        url = request.form["url"]
        title, summary = summarize_article(url)
        
        if title and summary:
            news_entry = {
                "id": str(uuid.uuid4()),  # Generate unique ID
                "title": title,
                "summary": summary
            }
            summaries.append(news_entry)  # Save multiple summaries
        
        return render_template("index.html", summaries=summaries)

    return render_template("index.html", summaries=summaries)

@app.route("/get_summary/<news_id>")
def get_summary(news_id):
    """Retrieve full summary based on ID."""
    news_item = next((news for news in summaries if news["id"] == news_id), None)
    if news_item:
        return jsonify(news_item)
    return jsonify({"error": "Summary not found"}), 404

@app.route("/delete_summary/<news_id>", methods=["DELETE"])
def delete_summary(news_id):
    """Delete a news summary based on its unique ID."""
    global summaries
    summaries = [news for news in summaries if news["id"] != news_id]
    return jsonify({"message": "Summary deleted successfully."}), 200

@app.route('/send-message', methods=['POST'])
def send_message():
    data = request.json  # Get the JSON data from the request
    name = data.get('name')
    email = data.get('email')
    message = data.get('message')

    # Check if all fields are provided
    if not name or not email or not message:
        return jsonify({"error": "All fields are required!"}), 400

    # Store the message in the SQLite database
    store_message(name, email, message)

    return jsonify({"success": "Message received successfully!"}), 200

if __name__ == "__main__":
    app.run(debug=True)
