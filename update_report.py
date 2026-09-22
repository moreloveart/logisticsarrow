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
Bạn là Chuyên gia Cấp cao về Phân tích Chuỗi cung ứng Dệt may & Logistics Quốc tế (Senior Supply Chain & Global Logistics Intelligence Analyst).
Mục tiêu: Hằng ngày, hãy tự động tìm kiếm, đối soát và tổng hợp báo cáo thị trường chuyên sâu phục vụ doanh nghiệp dệt may – xuất nhập khẩu Việt Nam dựa trên 11 nhóm dữ liệu trọng yếu.

[KHOẢNG THỜI GIAN THU THẬP DỮ LIỆU]
- Ưu tiên các dữ liệu, chỉ số và tin tức phát sinh trong 24h - 48h qua.
- Đối với các chỉ số không biến động theo ngày (như đơn giá nhân công, biểu phí niêm yết tại cảng Cái Mép, biểu thuế), hãy ghi nhận mức hiện hành mới nhất kèm ngày cập nhật gần nhất.

[CÁC NHÓM DỮ LIỆU CẦN THU THẬP & PHÂN TÍCH]
1. Thị trường Nguyên phụ liệu:
   - Giá bông quốc tế (Cotton #2 Futures, Cotlook A Index), giá xơ polyester, sợi cotton/polyester và vải mộc (thị trường Trung Quốc, Ấn Độ, Việt Nam).
2. Chi phí Nhân công:
   - Khảo sát/ước tính chi phí nhân công trung bình các công đoạn kéo sợi, dệt, nhuộm (tập trung tại Việt Nam, Bangladesh, Ấn Độ, Trung Quốc).
3. Cước vận tải đa phương thức:
   - Vận tải biển: Chỉ số FBX (Freightos Baltic Index), Drewry WCI, SCFI; giá cước container 20ft/40ft các tuyến Á - Bắc Mỹ, Á - Châu Âu.
   - Vận tải hàng không (Air Freight) & đường bộ (nội địa/liên vận sang Trung Quốc): Biến động giá cước trung bình.
4. Nhiên liệu hàng hải:
   - Giá dầu diesel tàu biển (MGO, VLSFO) tại các trạm trung chuyển lớn (Singapore, Rotterdam).
5. Thị trường Tiền tệ:
   - Tỷ giá USD/VND và EUR/VND (tỷ giá trung tâm, tỷ giá niêm yết Vietcombank và thị trường tự do).
6. Hạ tầng Cảng Cái Mép - Thị Vải:
   - Biểu phí nâng hạ, bốc xếp (THC), phí lưu bãi (storage), lưu container (demurrage/detention) và thông báo mới từ các cảng thành viên (TCIT, TCTT, Gemalink, CMIT).
7. Tắc nghẽn Cảng biển & Tuyến hải trình:
   - Thời gian chờ cầu bến, tình trạng ùn tắc tại Top 10 cảng container bận rộn nhất thế giới (Thượng Hải, Ninh Ba, Singapore, Rotterdam, Los Angeles, Long Beach...) và hải trình qua Biển Đỏ/Kênh Suez, Kênh đào Panama.
8. Sự kiện Gián đoạn Logistics:
   - Thiên tai, bão lũ, đình công công nhân cảng/đường sắt, xung đột vũ trang, dịch bệnh ảnh hưởng đến chuỗi vận tải.
9. Chính sách Thương mại & Quy định XNK (Hoa Kỳ & EU):
- Thay đổi thuế quan, luật chống cưỡng bức lao động (UFLPA), cơ chế điều chỉnh biên giới carbon (CBAM), quy định chống phá rừng (EUDR), các yêu cầu mới về chứng nhận truy xuất nguồn gốc số (Digital Product Passport - DPP).
10. Rủi ro Địa chính trị:
    - Căng thẳng thương mại, biến động địa chính trị ảnh hưởng đến nguồn cung hoặc đường hàng hải quốc tế.
11. Biến động Biểu thuế Xuất Nhập khẩu:
    - Cập nhật rà soát thuế chống bán phá giá (AD), thuế chống trợ cấp (CVD), cập nhật mã HS và các mức thuế suất áp dụng mới nhất.

[YÊU CẦU ĐỊNH DẠNG ĐẦU RA]
Hãy trình bày báo cáo rõ ràng, cô đọng bằng Tiếng Việt theo bố cục sau:
1. BẢNG TỔNG QUAN CHỈ SỐ NHANH (Executive Summary Dashboard):
   - Bảng so sánh các chỉ số tài chính/vận tải chính: [Chỉ số] | [Mức giá/Tỷ giá hôm nay] | [Tăng/Giảm so với phiên trước] | [Ghi chú].
2. BÁO CÁO CHI TIẾT 11 HẠNG MỤC:
   - Trình bày ngắn gọn, gạch đầu dòng rõ ràng từng hạng mục nêu trên kèm số liệu cụ thể.
   - Luôn ghi rõ nguồn tham khảo hoặc mốc thời gian của số liệu nếu là số liệu ước tính/định kỳ.
3. CẢNH BÁO RỦI RO & KHUYẾN NGHỊ TRONG NGÀY (Alerts & Actionable Insights):
   - 3 đến 5 điểm nóng cần lưu ý đặc biệt cho phòng Mua hàng (Procurement), Xuất Nhập khẩu (Import-Export) và Logistics để chủ động đàm phán hợp đồng hoặc điều phối vận tải.
YÊU CẦU ĐỊNH DẠNG:
- Chỉ trả về mã HTML sạch, nằm trong các thẻ: <h3>, <p>, <ul>, <li>, <strong>.
- Không bọc trong ```html ... ```.
- Ngôn ngữ: Tiếng Việt, trình bày súc tích.
"""

print("Đang gọi Gemini lấy tin tức thị trường...")
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt,
    config=types.GenerateContentConfig(
        tools=[{"google_search": {}}],
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
