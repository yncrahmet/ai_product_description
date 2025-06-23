from flask import Flask, request, jsonify, g, render_template, redirect, url_for, session
import uuid
import json
import redis
import threading
import os
from datetime import datetime
from dotenv import load_dotenv
from flask_bcrypt import Bcrypt
import sqlite3
from google import genai
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Uygulama ve bağımlılıklar
app = Flask(__name__)
bcrypt = Bcrypt(app)
load_dotenv()
app.secret_key = os.getenv("FLASK_SECRET_KEY", "your-secret-key")
r = redis.Redis(host='localhost', port=6379, decode_responses=True)
limiter = Limiter(app=app, key_func=get_remote_address)

# Veritabanı başlatma
def init_db():
    conn = sqlite3.connect('admin.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS admins
                 (email TEXT PRIMARY KEY, password_hash TEXT, secret_hash TEXT)''')
    conn.commit()
    conn.close()

# Admin ekleme (ilk kurulumda bir kez çalıştır)
def add_admin(email, password, secret):
    conn = sqlite3.connect('admin.db')
    c = conn.cursor()
    password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    secret_hash = bcrypt.generate_password_hash(secret).decode('utf-8')
    c.execute("INSERT OR REPLACE INTO admins (email, password_hash, secret_hash) VALUES (?, ?, ?)",
              (email, password_hash, secret_hash))
    conn.commit()
    conn.close()

# Admin doğrulama
def verify_admin(email, password, secret):
    conn = sqlite3.connect('admin.db')
    c = conn.cursor()
    c.execute("SELECT password_hash, secret_hash FROM admins WHERE email = ?", (email,))
    result = c.fetchone()
    conn.close()
    if result and bcrypt.check_password_hash(result[0], password) and bcrypt.check_password_hash(result[1], secret):
        return True
    return False

# Gemini API istemcisi
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

PLAN_LIMITS = {
    "trial": 5,
    "starter": 500,
    "pro": 1000,
    "boss": 2000
}

driver_lock = threading.Lock()

# Veritabanını başlat
init_db()
# Örnek admin ekle (ilk kurulumda bir kez çalıştır, sonra yorum satırına al)
add_admin(os.getenv("ADMIN_EMAIL"), os.getenv("ADMIN_PASSWORD"),os.getenv("ADMIN_SECRET"))

@app.route('/create-token-form')
def create_token_form():
    return render_template("create_token.html")

def ask_gemini(prompt):
    with driver_lock:
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            return response.text
        except Exception as e:
            print(f"Gemini API Hatası: {str(e)}")
            return None

@app.route('/create-token', methods=['POST'])
@limiter.limit("5 per minute")
def create_token():
    auth = request.headers.get("X-Admin-Secret", "")
    if not verify_admin(os.getenv("ADMIN_EMAIL"), os.getenv("ADMIN_PASSWORD"), auth):
        return jsonify({"error": "Yetkisiz erişim"}), 403
    data = request.get_json()
    email = data.get("email")
    plan = data.get("plan")
    if not email or plan not in PLAN_LIMITS:
        return jsonify({"error": "Eksik ya da geçersiz bilgi"}), 400
    token = str(uuid.uuid4())
    user_data = {
        "email": email,
        "plan": plan,
        "remaining": PLAN_LIMITS[plan]
    }
    r.set(f"user:{token}", json.dumps(user_data))
    return jsonify({"token": token, "email": email, "plan": plan, "limit": PLAN_LIMITS[plan]})

@app.route('/')
@app.route('/login')
@limiter.limit("10 per minute")
def login():
    if 'admin_session' in session:
        return redirect(url_for('admin_panel'))
    if 'user_session' in session:
        token = session['user_session']
        user_data = r.get(f"user:{token}")
        if user_data:
            return redirect(url_for('user_panel'))
        session.pop('user_session', None)
        session.pop('user_email', None)
    role = request.args.get('role', 'user')
    if role == 'admin':
        return render_template("login.html")
    return render_template("login_user.html")

@app.before_request
def check_token():
    if request.endpoint == 'generate_description':
        if 'user_session' not in session:
            return jsonify({"error": "Oturum geçersiz"}), 401
        token = session['user_session']
        email = session['user_email']
        user_data = r.get(f"user:{token}")
        if not user_data:
            return jsonify({"error": "Geçersiz token"}), 401
        user = json.loads(user_data)
        if user['email'] != email:
            return jsonify({"error": "Email ve token uyuşmuyor"}), 401
        if user['remaining'] <= 0:
            return jsonify({"error": "Kalan limitiniz doldu"}), 402
        user['remaining'] -= 1
        r.set(f"user:{token}", json.dumps(user))
        g.user = user

@app.route('/validate-token', methods=['POST'])
@limiter.limit("10 per minute")
def validate_token():
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "").strip() if auth_header else ""
    email = request.headers.get("X-User-Email", "")
    if not token or not email:
        return jsonify({"error": "Token veya email eksik"}), 401
    user_data = r.get(f"user:{token}")
    if not user_data:
        return jsonify({"error": "Geçersiz token"}), 401
    user = json.loads(user_data)
    if user['email'] != email:
        return jsonify({"error": "Email ve token uyuşmuyor"}), 401
    session['user_session'] = token
    session['user_email'] = email
    return jsonify({"message": "Giriş başarılı", "remaining": user['remaining'], "plan": user['plan'], "email": user['email']})

@app.route('/user-panel')
def user_panel():
    if 'user_session' not in session:
        return redirect(url_for('login'))
    token = session['user_session']
    user_data = json.loads(r.get(f"user:{token}"))
    return render_template("user_panel.html", email=user_data['email'], plan=user_data['plan'], remaining=user_data['remaining'])

@app.route('/generate-description', methods=['POST'])
def generate_description():
    if 'user_session' not in session:
        return jsonify({"error": "Oturum geçersiz"}), 401
    data = request.get_json()
    required_fields = ['product_name', 'category', 'audience', 'material', 'usage', 'platform']
    if not all(data.get(f) for f in required_fields):
        return jsonify({"error": "Eksik bilgi var"}), 400
    prompt = f"""
    Ürün Adı: {data['product_name']}
    Kategori: {data['category']}
    Hedef Kitle: {data['audience']}
    Malzeme: {data['material']}
    Kullanım: {data['usage']}
    Platform: {data['platform']}

    Yukarıdaki bilgilere göre şu kurallara uygun, SEO uyumlu, 250 kelimelik, profesyonel ve satışa yönelik bir ürün açıklaması yaz:
    - Başlık: Ürün adını ve anahtar kelimeleri içeren çekici bir başlık (H1).
    - Giriş: Ürünün temel faydasını ve hedef kitleye hitap eden 2-3 cümle.
    - Özellikler: Madde işaretleriyle malzeme, kullanım ve platformu vurgulayan 3-5 özellik.
    - CTA: 'Şimdi satın al', 'Hemen keşfet' gibi bir call-to-action.
    - Anahtar Kelimeler: 'product_name', 'category', 'audience' ile ilişkili doğal anahtar kelimeleri %1-2 yoğunlukta kullan.
    - Okunabilirlik: Kısa cümleler, aktif dil ve kullanıcı dostu ton.
    """
    answer = ask_gemini(prompt)
    if answer:
        return jsonify({"description": answer})
    return jsonify({"error": "Ürün açıklaması oluşturulamadı"}), 500

@app.route('/admin-login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def admin_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        secret = request.form.get('secret')
        if verify_admin(email, password, secret):
            session['admin_session'] = True
            return redirect(url_for('admin_panel'))
        return render_template("login.html", error=True)
    return render_template("login.html")

@app.route('/admin-panel')
@limiter.limit("5 per minute")
def admin_panel():
    if 'admin_session' not in session:
        return redirect(url_for('login', role='admin'))
    keys = r.keys("user:*")
    users = []
    for k in keys:
        token = k.split("user:")[1]
        data = json.loads(r.get(k))
        # Basit bir kullanım logu (örneğin son kullanım zamanı)
        usage_log = r.get(f"usage:{token}") or "Hiç kullanılmadı"
        users.append({"token": token, "email": data['email'], "plan": data['plan'], "remaining": data['remaining'], "usage": usage_log})
    return render_template("admin_panel.html", users=users)

@app.route('/delete-token/<token>', methods=['POST'])
@limiter.limit("5 per minute")
def delete_token(token):
    if 'admin_session' not in session:
        return jsonify({"error": "Yetkisiz erişim"}), 403
    r.delete(f"user:{token}")
    r.delete(f"usage:{token}")  # Kullanım logunu da sil
    return jsonify({"message": "Token silindi"}), 200

@app.before_request
def log_api_usage():
    if request.endpoint == 'generate_description' and 'user_session' in session:
        token = session['user_session']
        r.set(f"usage:{token}", f"Son kullanım: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ex=86400)

@app.route('/create-user', methods=['POST'])
@limiter.limit("5 per minute")
def create_user():
    if 'admin_session' not in session:
        return jsonify({"error": "Yetkisiz erişim"}), 403
    data = request.get_json()
    email = data.get("email")
    plan = data.get("plan")
    if not email or plan not in PLAN_LIMITS:
        return jsonify({"error": "Eksik ya da geçersiz bilgi"}), 400
    token = str(uuid.uuid4())
    user_data = {
        "email": email,
        "plan": plan,
        "remaining": PLAN_LIMITS[plan]
    }
    r.set(f"user:{token}", json.dumps(user_data))
    return jsonify({"token": token, "email": email, "plan": plan, "limit": PLAN_LIMITS[plan]})

@app.route('/api-management')
def api_management():
    if 'user_session' not in session:
        return redirect(url_for('login'))
    token = session['user_session']
    user_data = json.loads(r.get(f"user:{token}"))
    return render_template("api_management.html", token=token, email=user_data['email'], plan=user_data['plan'], remaining=user_data['remaining'])

@app.route('/logout')
def logout():
    session.pop('user_session', None)
    session.pop('user_email', None)
    session.pop('admin_session', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)