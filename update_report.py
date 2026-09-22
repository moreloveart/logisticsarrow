import os
import re
from datetime import datetime
from google import genai
from google.genai import types

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise ValueError("Thiếu biến môi trường GEMINI_API_KEY")

client = genai.Client(api_key=api_key)

prompt = """
BẮT BUỘC: Sử dụng công cụ Google Search để tra cứu thông tin và số liệu thị trường thực tế trong 24 giờ qua. 
TUYỆT ĐỐI KHÔNG lập danh sách lý thuyết hay giải thích cần thu thập gì. HÃY TRẢ LỜI BẰNG SỐ LIỆU VÀ TIN TỨC THỰC TẾ.

Nhiệm vụ: Hãy đóng vai Chuyên gia Chuỗi cung ứng Dệt may & Logistics, tổng hợp BẢN TIN THỊ TRƯỜNG HÔM NAY theo đúng các nhóm nội dung sau (nêu rõ số liệu, giá trị, % tăng/giảm nếu tìm thấy):

1. Thị trường Nguyên phụ liệu: Giá bông quốc tế (Cotton Futures/Cotlook A Index), giá xơ sợi polyester, cotton/polyester và vải mộc (Trung Quốc, Ấn Độ, Việt Nam).
2. Cước vận tải & Logistics: Biến động chỉ số SCFI, FBX, Drewry WCI tuyến Á - Mỹ, Á - Âu; cước đường bộ/liên vận Việt - Trung.
3. Nhiên liệu hàng hải: Giá dầu Brent, VLSFO/MGO tại Singapore/Rotterdam.
4. Thị trường Tiền tệ: Tỷ giá USD/VND, EUR/VND mới nhất.
5. Cảng biển & Rủi ro chuỗi cung ứng: Tình hình thông quan, tắc nghẽn cảng biển (Hải Phòng, Cái Mép - Thị Vải, Ninh Ba, Thượng Hải); các sự kiện đình công hoặc biến động chính sách thương mại (UFLPA, EUDR, CBAM).

YÊU CẦU ĐỊNH DẠNG:
- Trả về mã HTML trực tiếp (sử dụng các thẻ: <h4>, <p>, <ul>, <li>, <strong>).
- Không bọc trong ```html ... ```.
- Trình bày ngắn gọn, súc tích, đi thẳng vào số liệu tin tức của ngày hôm nay.
"""

print("Đang gọi Gemini lấy tin tức thị trường...")

# Sử dụng cú pháp Tool chuẩn của google-genai SDK
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt,
    config=types.GenerateContentConfig(
        tools=[types.Tool(google_search=types.GoogleSearch())],
        temperature=0.3,
    ),
)

report_text = response.text.strip()
report_text = re.sub(r"^```html\s*", "", report_text)
report_text = re.sub(r"```$", "", report_text).strip()

time_now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
content_to_insert = f"""<!-- MARKET_REPORT_START -->
<p style="color: #64748b; font-size: 0.9em;"><em>Cập nhật lần cuối: {time_now} (Hệ thống tự động)</em></p>
{report_text}
<!-- MARKET_REPORT_END -->"""

html_path = "index.html"
with open(html_path, "r", encoding="utf-8") as f:
    html_data = f.read()

pattern = r"<!-- MARKET_REPORT_START -->[\s\S]*?<!-- MARKET_REPORT_END -->"
if not re.search(pattern, html_data):
    raise ValueError("Không tìm thấy thẻ MARKET_REPORT_START trong index.html")

new_html_data = re.sub(pattern, content_to_insert, html_data)

with open(html_path, "w", encoding="utf-8") as f:
    f.write(new_html_data)

print("Cập nhật file index.html thành công!")
