👍 Faster Qwen3 TTS là một dự án open-source tập trung giải quyết bài
toán lớn nhất của voice AI hiện nay: latency và realtime khi chạy local.

Dự án này tối ưu Qwen3-TTS bằng cách dùng CUDA Graph để gom hàng trăm
kernel nhỏ thành một bước chạy duy nhất, giúp tăng tốc mạnh mà không cần
Flash Attention hay vLLM. ￼

Kết quả là có thể đạt tốc độ nhanh hơn realtime (RTF &gt; 1), với
time-to-first-audio chỉ \~150–400ms trên GPU phổ biến như RTX 4090. ￼

Các điểm nổi bật:

\* Realtime TTS + streaming audio (phát ra từng chunk ngay khi generate)

\* Voice cloning từ audio mẫu

\* Hỗ trợ cả streaming và non-streaming

\* OpenAI-compatible API (drop-in cho app hiện có)

\* Có CLI, Python API và WebUI demo

\* Tối ưu mạnh trên GPU nhưng vẫn giữ chất lượng gần như tương đương bản
gốc ￼

Usecase rất rõ:

\* Voice agent realtime (AI gọi điện, trợ lý ảo)

\* Dub video, podcast, audiobook

\* TTS backend cho chatbot/AI app

\* Local voice pipeline không cần SaaS

Điểm đáng chú ý là dự án không thay đổi model mà tối ưu cách chạy → giữ
chất lượng nhưng tăng tốc 2–9x, biến Qwen3-TTS từ “gần realtime” thành
“thực sự realtime”.

Thu thập từ internet
