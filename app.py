from flask import Flask, request
import sqlite3

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)')
    c.execute('INSERT OR IGNORE INTO users (id, username, password) VALUES (1, "admin", "supersecret")')
    conn.commit()
    conn.close()

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    query = "SELECT * FROM users WHERE username = ? AND password = ?"
    c.execute(query, (username, password))
    user = c.fetchone()
    conn.close()
    
    if user:
        return "Logged in successfully!"
    else:
        return "Invalid credentials"

if __name__ == '__main__':
    init_db()
    # INTENTIONAL VULNERABILITY: Running Flask in debug mode
    app.run(debug=True)
