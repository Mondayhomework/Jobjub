import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from PIL import Image as PILImage
from flask_cors import CORS
from google import genai
from google.genai.errors import APIError
import requests

load_dotenv()

application = Flask(__name__)

# ✅ แก้ไข: ดึงค่าจากตัวแปรชื่อ "key" ในไฟล์ .env
GEMINI_API_KEY_VALUE = os.environ.get("key")
client = None

url = "https://raw.githubusercontent.com/Leebob001/JobJub/refs/heads/main/provinces.json"
provinces = requests.get(url).json()

print(provinces)

if GEMINI_API_KEY_VALUE:
    try:
        # ✅ สร้าง Client ด้วยค่าที่ดึงมา (แม้ชื่อจะต่างกัน)
        client = genai.Client(api_key=GEMINI_API_KEY_VALUE) 
        print("✅ Gemini Client initialized successfully.")
    except Exception as e:
        print(f"❌ ERROR: Global Gemini Client failed to initialize: {e}")
else:
    print("⚠️ WARNING: API key 'key' not found. API calls will fail.")
# ... ส่วนที่เหลือเหมือนเดิม
CORS(application, resources={r"/ask": {"origins": "*"}})

@application.route('/ask', methods=['POST'])
def handle_gemini_request() : # ✅ เปลี่ยนชื่อฟังก์ชันเพื่อป้องกันความสับสน
    
    data = request.get_json()

    track = data.get('track')
    address = data.get('address')
    grade = data.get('grade')

    valid_province_names = [p['name_th'] for p in provinces]

    if track and address and grade and (address in valid_province_names):
        contents = f"ถนัด", track, "อยู่จังหวัด", address ,"อยู่ชั้น", grade, "ไปต่อที่ไหนได้บ้างขอชื่อรร. และ อธิบายสั้นๆ"
        print(contents)
    else :
        print("❌💥")

    # 6. ตรวจสอบ Client และ Contents 
    if not client:
        return jsonify({'error': 'Gemini Client not initialized. Check terminal for API Key warning.'}), 500

    if not contents:
        return jsonify({'error': 'No text prompt or image file found in request.'}), 400
    try:
        # 3. ✅ ใช้ client ที่สร้างไว้แล้ว
        print("💡 START: Calling Gemini API...")

        answer = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=contents,
            )

        print("💡 END: Gemini API returned successfully.")

        response_data = {
            'text': answer.text,
        }
        
        print("Response sent successfully.")
        return jsonify(response_data)

    except APIError as e:
        print(f"API Error: {e.message}")
        return jsonify({'error': f'Gemini API Error: {e.message}'}), 500
    except Exception as e:
        print(f"Internal Error: {str(e)}")
        return jsonify({'error': f'Internal Server Error: {str(e)}'}), 500

    pass

if __name__ == '__main__':
    application.run(debug=True, port=5001)