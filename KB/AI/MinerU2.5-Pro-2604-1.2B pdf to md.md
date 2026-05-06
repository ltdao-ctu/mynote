🚀 Model OCR 1.2B tham số nguồn mở chuyên convert PDF -\> Markdown vừa
ra phiên bản mới SOTA chất lượng tốt cho tiếng Việt 🇻🇳

Nếu bạn đang làm RAG, xử lý PDF hay trích xuất dữ liệu tài liệu, thì
model này đáng để chú ý.

MinerU2.5-Pro-2604-1.2B là model vision-language 1.2B tham số, tập trung
vào document parsing (PDF → Markdown) với độ chính xác cực cao.

🔥 Điểm đột phá lớn nhất

\* SOTA trên OmniDocBench v1.6 (~95.69) → vượt cả model OCR chuyên dụng
và VLM cực lớn ￼

\* Không tăng model size → vẫn giữ 1.2B params nhưng cải thiện mạnh nhờ
data engineering ￼

👉 Ý nghĩa:

Không cần model to → vẫn đánh bại model 100B+

⚡ Khả năng thực tế cực mạnh

\* 📄 Parse PDF → Markdown có cấu trúc chuẩn

\* 📊 Nhận diện bảng phức tạp (table parsing top leaderboard) ￼

\* 🧮 Extract công thức toán học chính xác cao (~97%) ￼

\* 🖼️ Hỗ trợ:

\* Chart / image parsing

\* Merge bảng nhiều trang

\* Ghép đoạn text bị cắt

👉 Không chỉ OCR → mà là hiểu cấu trúc tài liệu

🧠 Bí mật phía sau: Data Engine

Thay vì đổi kiến trúc, team tập trung vào dữ liệu:

\* Scale dataset từ \<10M → 65.5M pages ￼

\* Cross-model verification để giảm noise annotation

\* Pipeline training 3 giai đoạn (pretrain → hard sample → alignment) ￼

👉 Insight quan trọng:

Data \> Model size (ít nhất trong bài toán document parsing)

💡 Use case cực rõ ràng

\* RAG từ PDF / tài liệu nội bộ

\* Digitize tài liệu doanh nghiệp

\* AI đọc báo cáo tài chính / khoa học

\* Xây hệ thống search + knowledge base

⚙️ Triển khai

\* Compatible với Transformers + vLLM

\* Có thể chạy inference async (~2.1 fps trên A100) ￼

\* Output JSON → convert Markdown dễ dàng

👉 Tóm lại

MinerU2.5-Pro không chỉ là OCR

→ nó là “data ingestion engine” cho LLM

Nếu bạn đang build:

\* RAG system

\* AI đọc tài liệu

\* Knowledge automation

👉 Đây là một trong những model đáng dùng nhất hiện tại
