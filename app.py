# app.py
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import csv
import os
from datetime import datetime
from google_checker import GoogleFactChecker
from rule_detector import FakeNewsDetector

app = Flask(__name__)
app.secret_key = 'fake_news_detection_secret_key_2024'

# تهيئة الأدوات
google_checker = GoogleFactChecker()
news_detector = FakeNewsDetector()

def save_user_data(name, phone):
    """حفظ بيانات المستخدم"""
    file_exists = os.path.isfile('data/users.csv')
    
    with open('data/users.csv', 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['name', 'phone', 'timestamp'])
        writer.writerow([name, phone, datetime.now().strftime("%Y-%m-%d %H:%M:%S")])

def save_detection_result(data):
    """حفظ نتائج الكشف"""
    file_exists = os.path.isfile('data/detection_history.csv')
    
    with open('data/detection_history.csv', 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['timestamp', 'title', 'result', 'score', 'confidence', 'reasons'])
        
        writer.writerow([
            data['timestamp'],
            data.get('title', '')[:50],  # أول 50 حرف فقط
            data['result'],
            data['score'],
            data['confidence'],
            '; '.join(data['reasons'])
        ])

@app.route('/', methods=['GET', 'POST'])
def login():
    """صفحة تسجيل الدخول"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        phone = request.form.get('phone', '').strip()
        
        if name and phone:
            # حفظ بيانات المستخدم
            save_user_data(name, phone)
            
            # حفظ في الجلسة
            session['user_name'] = name
            session['user_phone'] = phone
            
            return redirect(url_for('home'))
        
        return render_template('login.html', error='يرجى إدخال الاسم ورقم الهاتف')
    
    return render_template('login.html')

@app.route('/home')
def home():
    """الصفحة الرئيسية"""
    if 'user_name' not in session:
        return redirect(url_for('login'))
    
    return render_template('index.html', name=session['user_name'])

@app.route('/detect', methods=['POST'])
def detect_news():
    """واجهة الكشف عن الأخبار المزيفة"""
    if 'user_name' not in session:
        return jsonify({'error': 'غير مصرح بالدخول'}), 401
    
    # استقبال البيانات
    title = request.form.get('title', '').strip()
    text = request.form.get('text', '').strip()
    source = request.form.get('source', '').strip()
    
    if not title and not text:
        return jsonify({
            'error': 'يرجى إدخال عنوان أو نص الخبر'
        })
    
    result_data = {}
    
    # 1. التحقق من Google Fact Check أولاً
    google_results = None
    if text:
        google_results = google_checker.check_claim(text)
        
        if google_results:
            overall_rating = google_checker.get_overall_rating(google_results)
            
            if overall_rating and overall_rating['rating'] == 'FALSE':
                result_data = {
                    'result': 'خبر مزيف',
                    'score': 100,
                    'reasons': ['تم التحقق منه عبر Google Fact Check API'],
                    'color': 'danger',
                    'confidence': 'عالية جداً',
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'google_results': google_results[:2]
                }
                
                # حفظ النتيجة
                save_detection_result(result_data)
                return jsonify(result_data)
    
    # 2. استخدام نظام القواعد
    detection_result = news_detector.detect(title, text, source)
    
    # 3. إضافة نتائج Google إذا وجدت
    if google_results:
        detection_result['google_results'] = google_results[:2]
    
    # 4. حفظ النتيجة
    save_detection_result(detection_result)
    
    return jsonify(detection_result)

@app.route('/history')
def history():
    """عرض سجل الكشف"""
    if 'user_name' not in session:
        return redirect(url_for('login'))
    
    history_data = []
    
    if os.path.isfile('data/detection_history.csv'):
        with open('data/detection_history.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in list(reader)[-10:]:  # آخر 10 نتائج
                history_data.append(row)
    
    return render_template('history.html', 
                         history=reversed(history_data), 
                         name=session['user_name'])

@app.route('/stats')
def stats():
    """إحصائيات الكشف"""
    if 'user_name' not in session:
        return redirect(url_for('login'))
    
    stats_data = {
        'total': 0,
        'fake': 0,
        'real': 0,
        'suspicious': 0
    }
    
    if os.path.isfile('data/detection_history.csv'):
        with open('data/detection_history.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
            stats_data['total'] = len(rows)
            
            for row in rows:
                result = row.get('result', '')
                if 'مزيف' in result:
                    stats_data['fake'] += 1
                elif 'حقيقي' in result:
                    stats_data['real'] += 1
                elif 'مشبوه' in result:
                    stats_data['suspicious'] += 1
    
    return render_template('stats.html', 
                         stats=stats_data, 
                         name=session['user_name'])

@app.route('/logout')
def logout():
    """تسجيل الخروج"""
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    # إنشاء مجلد البيانات إذا لم يكن موجوداً
    os.makedirs('data', exist_ok=True)
    
    app.run(debug=True, host='0.0.0.0', port=5000)