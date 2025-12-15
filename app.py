from flask import Flask, render_template_string, request, redirect, session
import os

app = Flask(__name__)
app.secret_key = "rahasia_desa_2025"

# Ambil DATABASE_URL dari environment (nanti diisi Render)
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:////tmp/test.db')

@app.route('/')
def home():
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head><title>Voting Kades</title></head>
    <body style="font-family: Arial; text-align: center; padding: 50px;">
        <h1>✅ Deploy Berhasil!</h1>
        <p>Aplikasi voting desa sudah online.</p>
        <p>Database: {{ status }}</p>
    </body>
    </html>
    ''', status="Terkoneksi" if "postgres" in DATABASE_URL else "Belum terhubung ke PostgreSQL")

if __name__ == '__main__':
    app.run(debug=False)
