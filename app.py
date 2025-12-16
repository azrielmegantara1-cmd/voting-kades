from flask import Flask, render_template_string, request, redirect, session
import psycopg2
import os

app = Flask(__name__)
app.secret_key = "rahasia_desa_2025_sangat_rahasia"

# Ambil DATABASE_URL dari environment (dari PythonAnywhere)
DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db():
    return psycopg2.connect(DATABASE_URL)

# === HALAMAN LOGIN ===
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nik = request.form['nik'].strip()
        if not nik.isdigit() or len(nik) != 16:
            return render_template_string(login_page, error="NIK harus 16 digit angka!")
        
        try:
            with get_db() as conn:
                cur = conn.cursor()
                cur.execute("SELECT id, nama FROM pemilih WHERE nik = %s AND sudah_vote = FALSE", (nik,))
                user = cur.fetchone()
                if user:
                    session['user_id'] = user[0]
                    session['nama'] = user[1]
                    return redirect('/vote')
                else:
                    return render_template_string(login_page, error="NIK tidak terdaftar atau sudah memberikan suara.")
        except Exception as e:
            return f"<h3>Error koneksi database:</h3><p>{str(e)}</p>"
    
    return render_template_string(login_page)

# === HALAMAN VOTING ===
@app.route('/vote', methods=['GET', 'POST'])
def vote():
    if 'user_id' not in session:
        return redirect('/')
    
    try:
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, nama FROM kandidat ORDER BY nama")
            kandidat = cur.fetchall()
            
            if request.method == 'POST':
                kandidat_id = request.form.get('kandidat')
                if not kandidat_id:
                    return render_template_string(vote_page, kandidat=kandidat, error="Pilih salah satu kandidat!")
                
                # Simpan suara
                cur.execute("INSERT INTO suara (pemilih_id, kandidat_id) VALUES (%s, %s)",
                           (session['user_id'], kandidat_id))
                cur.execute("UPDATE pemilih SET sudah_vote = TRUE WHERE id = %s", (session['user_id'],))
                conn.commit()
                session.clear()
                return "<h2 style='text-align:center; margin-top:50px;'>✅ Terima kasih telah memilih!</h2>"
            
            return render_template_string(vote_page, kandidat=kandidat)
    except Exception as e:
        return f"<h3>Error:</h3><p>{str(e)}</p>"

# === HALAMAN HASIL (otomatis refresh tiap 10 menit) ===
@app.route('/hasil')
def hasil():
    try:
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT k.nama, COUNT(s.id) as suara
                FROM kandidat k
                LEFT JOIN suara s ON k.id = s.kandidat_id
                GROUP BY k.id
                ORDER BY suara DESC
            """)
            hasil = cur.fetchall()
        
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Hasil Voting Sementara</title>
            <meta charset="UTF-8">
            <meta http-equiv="refresh" content="600"> <!-- 600 detik = 10 menit -->
            <style>
                body { font-family: Arial, sans-serif; background: #f5f7fa; padding: 20px; }
                .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
                h1 { text-align: center; color: #2c3e50; }
                .candidate { margin: 20px 0; padding: 15px; border-left: 4px solid #3498db; background: #f8f9fa; }
                .count { font-size: 24px; font-weight: bold; color: #27ae60; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>📊 Hasil Voting Sementara</h1>
        """
        for nama, suara in hasil:
            html += f'<div class="candidate"><div class="count">{suara}</div><div>{nama}</div></div>'
        html += """
            </div>
        </body>
        </html>
        """
        return html
    except Exception as e:
        return f"<h3>Error menampilkan hasil:</h3><p>{str(e)}</p>"

# ===== TEMPLATES =====
login_page = """
<!DOCTYPE html>
<html>
<head>
    <title>Login Warga</title>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial; background: #e3f2fd; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .box { background: white; padding: 30px; border-radius: 15px; box-shadow: 0 4px 20px rgba(0,0,0,0.15); width: 90%; max-width: 400px; }
        input, button { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ccc; border-radius: 8px; font-size: 16px; }
        button { background: #1976d2; color: white; cursor: pointer; }
        button:hover { background: #1565c0; }
        .error { color: #d32f2f; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="box">
        <h2 style="text-align:center;">🗳️ Login Warga</h2>
        <form method="post">
            <input name="nik" placeholder="NIK (16 digit)" maxlength="16" required>
            <button type="submit">Masuk</button>
        </form>
        {% if error %}<p class="error">{{ error }}</p>{% endif %}
    </div>
</body>
</html>
"""

vote_page = """
<!DOCTYPE html>
<html>
<head>
    <title>Pilih Kandidat</title>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial; background: #f1f8e9; padding: 20px; }
        .container { max-width: 500px; margin: 0 auto; background: white; padding: 30px; border-radius: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
        h2 { text-align: center; color: #2e7d32; }
        .option { margin: 15px 0; padding: 15px; border: 2px solid #c8e6c9; border-radius: 10px; cursor: pointer; }
        .option:hover { background: #f1f8e9; }
        input[type="radio"] { transform: scale(1.3); margin-right: 10px; }
        button { width: 100%; padding: 14px; background: #388e3c; color: white; border: none; border-radius: 10px; font-size: 18px; cursor: pointer; margin-top: 20px; }
        button:hover { background: #2e7d32; }
        .error { color: #c62828; text-align: center; margin: 15px 0; }
    </style>
</head>
<body>
    <div class="container">
        <h2>✅ Pilih Kandidat Anda</h2>
        {% if error %}<p class="error">{{ error }}</p>{% endif %}
        <form method="post">
            {% for id, nama in kandidat %}
            <label class="option">
                <input type="radio" name="kandidat" value="{{ id }}" required> {{ nama }}
            </label>
            {% endfor %}
            <button type="submit">Kirim Suara</button>
        </form>
    </div>
</body>
</html>
"""

if __name__ == '__main__':
    app.run(debug=False)
