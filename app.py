from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app) # للسماح للتطبيق بالاتصال بالوسيط

# بيانات الإدمن الخاصة بك (تبقى مخفية هنا في السيرفر ولا تصل للمشترك)
ADMIN_USER = "admin@dsc"
ADMIN_PASS = "bashar2000"
# رابط الـ API الفعلي للساس (يجب استخراجه من لوحة التحكم)
SAS_API_URL = "https://itpc2.scn-wifi.com/api" 

@app.route('/login-subscriber', methods=['POST'])
def login_subscriber():
    data = request.json
    sub_user = data.get('username')
    sub_pass = data.get('password')

    if not sub_user or not sub_pass:
        return jsonify({"error": "الرجاء إدخال اليوزر والباسورد"}), 400

    try:
        # 1. السيرفر يقوم بتسجيل الدخول للساس كإدمن للحصول على Token/Session
        admin_login = requests.post(f"{SAS_API_URL}/login", json={
            "username": ADMIN_USER,
            "password": ADMIN_PASS
        })
        
        # ملاحظة: هذا مجرد هيكل تقريبي، الكود الدقيق يعتمد على شكل الـ API الخاص بنظام SCN-WIFI
        if admin_login.status_code == 200:
            token = admin_login.json().get('token')
            
            # 2. السيرفر يبحث عن المشترك باستخدام اليوزر الخاص به
            headers = {"Authorization": f"Bearer {token}"}
            sub_info = requests.get(f"{SAS_API_URL}/users/{sub_user}", headers=headers)
            
            if sub_info.status_code == 200:
                user_data = sub_info.json()
                # 3. التحقق من تطابق باسورد المشترك
                if user_data.get('password') == sub_pass:
                    return jsonify({
                        "status": "success",
                        "expiration": user_data.get('expiration_date', 'غير متوفر'),
                        "debt": user_data.get('debt', '0'),
                        "status_active": user_data.get('is_online', False)
                    })
                else:
                    return jsonify({"error": "كلمة المرور غير صحيحة"}), 401
            else:
                return jsonify({"error": "هذا المشترك غير موجود"}), 404
        else:
            return jsonify({"error": "خطأ في اتصال السيرفر بالساس"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
