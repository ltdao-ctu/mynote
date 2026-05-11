Chonkie - Table Chunker dành cho RAG 🔥

Chonkie là 1 thư viện cung cấp 1 tính năng khá hữu ích cho ai đang làm
RAG với dữ liệu dạng bảng, thông qua TableChunker

Cụ thể, TableChunker giúp chia các bảng markdown lớn thành nhiều phần
nhỏ hơn theo từng dòng, đồng thời luôn giữ lại phần header trong mỗi
chunk.

Điểm này rất quan trọng vì khi đưa dữ liệu bảng vào pipeline RAG, nếu
cắt bảng theo token một cách ngẫu nhiên thì nội dung rất dễ mất ngữ
cảnh.

Những điểm đặc biệt ở TableChunker

📌Chia theo row, không cắt tùy ý theo token

📌Giữ header ở mọi chunk

📌Hoạt động với nhiều tokenizer khác nhau

📌Phù hợp cho indexing, embedding, retrieval

📌Mỗi chunk đều là markdown hợp lệ, có thể dùng ngay

Đây là một giải pháp rất thực tế để xử lý tabular data trong RAG, giúp
dữ liệu dễ đọc hơn với model và giữ được ngữ cảnh tốt hơn khi truy xuất.

Link repo & documentation:
[<u>https://docs.chonkie.ai/oss/chunkers/table-chunker</u>](https://docs.chonkie.ai/oss/chunkers/table-chunker)
