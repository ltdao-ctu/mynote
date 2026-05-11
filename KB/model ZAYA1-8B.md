Zyphra vừa release ZAYA1-8B — một trong những model open-weight thú vị
nhất hiện nay trong xu hướng “small MoE, high intelligence density”.

Điểm đặc biệt:

\* tổng ~8.4B params

\* nhưng chỉ ~760M active params mỗi lần inference

→ cực kỳ nhẹ so với hiệu năng đạt được.

Đây là mô hình Mixture-of-Experts (MoE) tập trung mạnh vào:

\* reasoning

\* toán học

\* coding

\* long-form thinking

Và benchmark khá ấn tượng:

\* AIME’26: 89.1

\* GPQA Diamond: 71.0

\* LiveCodeBench-v6: 65.8

→ cạnh tranh trực tiếp với nhiều model lớn hơn rất nhiều.

Insight quan trọng:

ZAYA1-8B cho thấy một hướng rất rõ của AI hiện tại:

👉 không phải model càng to càng tốt

👉 mà là “intelligence density” — trí tuệ trên mỗi compute/token.

Một điểm đáng chú ý khác:

Model được train hoàn toàn trên AMD MI300X stack thay vì NVIDIA.

→ cho thấy ecosystem AI đang bắt đầu đa dạng hơn về hardware.

Ngoài ra:

\* Apache 2.0 license

\* hỗ trợ Transformers + vLLM

\* VRAM requirement khá thấp

\* phù hợp local inference và agent workflow

Đây có thể là tín hiệu cho tương lai của reasoning models:

❌ giant dense model

✅ small efficient MoE + test-time compute

Nếu xu hướng này tiếp tục, các model nhỏ nhưng “suy nghĩ tốt” sẽ ngày
càng quan trọng hơn trong AI sản phẩm thực tế.

\#LLM

Model: https://huggingface.co/Zyphra/ZAYA1-8B
