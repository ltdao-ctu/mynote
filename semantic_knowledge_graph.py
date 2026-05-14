import os
import json
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv

# 1. CẤU HÌNH HỆ THỐNG
load_dotenv()
THRESHOLD = float(os.getenv("THRESHOLD", "0.4"))
KB_PATH = os.getenv("KB_PATH", "KB")

def get_file_metadata(file_path):
    """Trích xuất thông tin cơ bản của file"""
    stats = os.stat(file_path)
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        word_count = len(content.split())
    
    # Lấy tên thư mục cha để làm Category
    category = os.path.dirname(file_path).split(os.sep)[-1]
    if category == KB_PATH or not category:
        category = "Chung"
        
    return {
        "size_kb": round(stats.st_size / 1024, 2),
        "word_count": word_count,
        "category": category
    }

def clean_markdown(text):
    """Loại bỏ bớt ký tự thừa để SBERT xử lý chính xác hơn"""
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return " ".join(lines)[:2000]  # Giới hạn 2000 ký tự đầu để tăng tốc

def build_semantic_graph():
    if not os.path.exists(KB_PATH):
        print(f"[!] Thư mục {KB_PATH} không tồn tại!")
        return

    # 2. TẢI MODEL (Chuyên dụng cho tiếng Việt)
    print("[*] Đang khởi tạo trí tuệ nhân tạo (Vietnamese-SBERT)...")
    model = SentenceTransformer('keepitreal/vietnamese-sbert')
    
    file_list = []
    documents = []

    # 3. QUÉT DỮ LIỆU
    print(f"[*] Đang đọc dữ liệu từ: {KB_PATH}...")
    for root, _, filenames in os.walk(KB_PATH):
        for filename in filenames:
            if filename.endswith('.md'):
                full_path = os.path.join(root, filename)
                rel_id = os.path.relpath(full_path, KB_PATH).replace(os.sep, '/')
                
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        raw_content = f.read().strip()
                        if len(raw_content) > 15: # Bỏ qua file quá ngắn
                            meta = get_file_metadata(full_path)
                            file_list.append({
                                "id": rel_id,
                                "name": filename,
                                **meta
                            })
                            documents.append(clean_markdown(raw_content))
                except Exception as e:
                    print(f"[!] Lỗi đọc file {filename}: {e}")

    if not documents:
        print("[!] Không có dữ liệu để xử lý.")
        return

    # 4. TÍNH TOÁN NGỮ NGHĨA
    print(f"[*] Đang tính toán liên kết cho {len(file_list)} tài liệu...")
    embeddings = model.encode(documents, show_progress_bar=True)
    sim_matrix = cosine_similarity(embeddings)

    nodes = []
    edges = []

    # Tạo Nodes
    for info in file_list:
        nodes.append({
            "id": info["id"],
            "label": info["name"],
            "group": info["category"],
            "value": max(info["word_count"] // 100, 5),
            "path": info["id"], # Lưu đường dẫn tương đối để Fetch từ Server
            "title": f"Click để xem nội dung: {info['name']}"
        })

    # Tạo Edges (Đã lọc dư thừa)
    for i in range(len(file_list)):
        for j in range(i + 1, len(file_list)):
            score = float(sim_matrix[i][j])
            
            # CHỐNG DƯ THỪA: 
            # - Chỉ lấy score > THRESHOLD
            # - score < 0.98 để loại bỏ các file copy hoặc trùng lặp hoàn toàn
            if THRESHOLD <= score < 0.98:
                edges.append({
                    "from": file_list[i]["id"],
                    "to": file_list[j]["id"],
                    "weight": round(score, 3),
                    "label": f"{int(score*100)}%",
                    "color": {"opacity": round(score, 2), "color": "#848484"},
                    "font": {"size": 10, "align": "middle"}
                })

    # 5. XUẤT FILE JSON
    output_data = {
        "metadata": {
            "total_nodes": len(nodes),
            "total_edges": len(edges),
            "threshold": THRESHOLD
        },
        "nodes": nodes,
        "edges": edges
    }

    with open('graph_data.json', 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=4)

    print(f"\n--- XONG! ---")
    print(f"Tìm thấy: {len(nodes)} nodes và {len(edges)} liên kết.")
    print(f"Kết quả lưu tại: graph_data.json")

if __name__ == "__main__":
    build_semantic_graph()