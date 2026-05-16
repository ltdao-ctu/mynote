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
# Trọng số cộng thêm cho tài liệu cùng Category (0.0 -> 1.0)
CATEGORY_BONUS = 0.15 

def get_file_metadata(file_path):
    stats = os.stat(file_path)
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        word_count = len(content.split())
    
    category = os.path.dirname(file_path).split(os.sep)[-1]
    if category == KB_PATH or not category:
        category = "Chung"
        
    return {
        "size_kb": round(stats.st_size / 1024, 2),
        "word_count": word_count,
        "category": category
    }

def clean_and_enrich_markdown(text, category):
    """
    Làm sạch và chèn thêm nhãn Category để tăng cường mối liên kết ngữ nghĩa
    giữa các tài liệu cùng loại.
    """
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    content = " ".join(lines)[:2000]
    
    # Kỹ thuật chèn nhãn: Giúp SBERT hiểu đây là các tài liệu cùng nhóm
    if category != "Chung":
        enriched_content = f"Chủ đề {category}. Phân loại {category}. " + content
        return enriched_content
    return content

def build_semantic_graph():
    if not os.path.exists(KB_PATH):
        print(f"[!] Thư mục {KB_PATH} không tồn tại!")
        return

    # 2. TẢI MODEL
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
                        if len(raw_content) > 15:
                            meta = get_file_metadata(full_path)
                            file_list.append({
                                "id": rel_id,
                                "name": filename,
                                **meta
                            })
                            # Làm giàu ngữ nghĩa bằng category
                            enriched = clean_and_enrich_markdown(raw_content, meta['category'])
                            documents.append(enriched)
                except Exception as e:
                    print(f"[!] Lỗi đọc file {filename}: {e}")

    if not documents:
        print("[!] Không có dữ liệu để xử lý.")
        return

    # 4. TÍNH TOÁN NGỮ NGHĨA
    print(f"[*] Đang tính toán liên kết cho {len(file_list)} tài liệu...")
    embeddings = model.encode(documents, show_progress_bar=True)
    sim_matrix = cosine_similarity(embeddings)

    edges = []
    # Khởi tạo bộ đếm liên kết để xác định kích thước node
    connection_counts = {info["id"]: 0 for info in file_list}

    # Tính toán Edges trước
    for i in range(len(file_list)):
        for j in range(i + 1, len(file_list)):
            score = float(sim_matrix[i][j])
            cat_i = file_list[i]["category"]
            cat_j = file_list[j]["category"]

            # Áp dụng điểm thưởng nếu cùng loại
            effective_score = score
            if cat_i == cat_j and cat_i != "Chung":
                effective_score += CATEGORY_BONUS
            
            # Lọc theo ngưỡng (sau khi đã cộng thưởng)
            if THRESHOLD <= effective_score < 0.99:
                edges.append({
                    "from": file_list[i]["id"],
                    "to": file_list[j]["id"],
                    "weight": round(effective_score, 3),
                    "label": f"{int(min(effective_score, 1)*100)}%",
                    "color": {"opacity": round(min(effective_score, 1), 2), "color": "#848484"},
                    "font": {"size": 10, "align": "middle"}
                })
                # Tăng đếm liên kết
                connection_counts[file_list[i]["id"]] += 1
                connection_counts[file_list[j]["id"]] += 1

    # 5. TẠO NODES (Kích thước dựa trên số lượng liên kết)
    nodes = []
    for info in file_list:
        count = connection_counts[info["id"]]
        nodes.append({
            "id": info["id"],
            "label": info["name"],
            "group": info["category"],
            "value": 2 + count,  # Càng nhiều liên kết node càng to
            "path": info["id"],
            "title": f"Loại: {info['category']} | Kết nối: {count} tài liệu tương đồng"
        })

    # 6. XUẤT FILE JSON
    output_data = {
        "metadata": {
            "total_nodes": len(nodes),
            "total_edges": len(edges),
            "threshold_used": THRESHOLD,
            "category_bonus": CATEGORY_BONUS
        },
        "nodes": nodes,
        "edges": edges
    }

    with open('graph_data.json', 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=4)

    print(f"\n--- HOÀN THÀNH ---")
    print(f"Số lượng Nodes: {len(nodes)}")
    print(f"Số lượng Edges: {len(edges)}")
    print(f"Kết quả lưu tại: graph_data.json")

if __name__ == "__main__":
    build_semantic_graph()