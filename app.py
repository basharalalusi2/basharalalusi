from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)

DB_FILE = 'users.db'

# إنشاء قاعدة البيانات وتجهيزها
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (username TEXT PRIMARY KEY, password TEXT, phone TEXT, 
                  start_date TEXT, exp_date TEXT, debt TEXT, status TEXT)''')
    conn.commit()
    conn.close()

init_db()

# حسابك الإداري للدخول للوحة التحكم
ADMIN_USER = "bashar@dsc"
ADMIN_PASS = "bashar2000"

@app.route('/login-subscriber', methods=['POST'])
def login():
    data = request.json
    user = data.get('username')
    pw = data.get('password')

    if not user or not pw:
        return jsonify({"error": "الرجاء إدخال اليوزر والباسورد"}), 400

    # إذا كان الدخول للإدمن
    if user == ADMIN_USER and pw == ADMIN_PASS:
        return jsonify({"role": "admin", "status": "success"})

    # إذا كان الدخول لمشترك عادي
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT exp_date, debt, status, phone, start_date FROM users WHERE username=? AND password=?", (user, pw))
    row = c.fetchone()
    conn.close()

    if row:
        return jsonify({
            "role": "user",
            "status": "success",
            "expiration": row[0],
            "debt": row[1],
            "status_active": row[2] == 'متصل',
            "phone": row[3],
            "start_date": row[4]
        })
    else:
        return jsonify({"error": "اليوزر أو الباسورد غير صحيح"}), 401

@app.route('/add_user', methods=['POST'])
def add_user():
    data = request.json
    admin_user = data.get('admin_user')
    admin_pass = data.get('admin_pass')

    # التحقق من صلاحيات الإدمن قبل الإضافة
    if admin_user != ADMIN_USER or admin_pass != ADMIN_PASS:
        return jsonify({"error": "غير مصرح لك بالإضافة"}), 403

    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("REPLACE INTO users (username, password, phone, start_date, exp_date, debt, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
                  (data['username'], data['password'], data['phone'], data['start_date'], data['exp_date'], data['debt'], data['status']))
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "تم إضافة / تعديل المشترك بنجاح!"})
    except Exception as e:
        return jsonify({"error": "حدث خطأ أثناء الحفظ"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
