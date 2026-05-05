import os
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from pyvis.network import Network
import numpy as np

def build_interactive_graph(directory, threshold=0.4):
    print("[*] Đang tải mô hình tiếng Việt...")
    model = SentenceTransformer('keepitreal/vietnamese-sbert')
    
    files = [f for f in os.listdir(directory) if f.endswith('.md')]
    documents = []
    valid_files = []

    for file in files:
        with open(os.path.join(directory, file), 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if len(content) > 10: 
                documents.append(content)
                valid_files.append(file)

    if not valid_files: return

    embeddings = model.encode(documents)
    sim_matrix = cosine_similarity(embeddings)

    # Khởi tạo Network
    net = Network(height="750px", width="100%", bgcolor="#222222", font_color="white")
    net.force_atlas_2based()

    for i, file in enumerate(valid_files):
        # Chúng ta dùng tên file làm ID để dễ xử lý link
        net.add_node(file, label=file, title=f"Click để mở {file}", color="#00ffcc")

    for i in range(len(valid_files)):
        for j in range(i + 1, len(valid_files)):
            score = float(sim_matrix[i][j])
            if score > threshold:
                net.add_edge(valid_files[i], valid_files[j], value=score, weight=score)

    # Xuất file HTML
    output_path = "index.html"
    net.save_graph(output_path)

    # --- ĐOẠN CHÈN JS ĐỂ CLICK MỞ FILE ---
    # Đọc lại file vừa tạo để chèn mã bắt sự kiện click
    with open(output_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Đoạn script này sẽ lắng nghe sự kiện click vào node
    click_js = """
    network.on("click", function (params) {
        if (params.nodes.length > 0) {
            var nodeId = params.nodes[0];
            // nodeId chính là tên file .md chúng ta đã đặt ở trên
            window.open(nodeId, '_blank'); 
        }
    });
    """
    
    # Chèn script vào trước thẻ đóng body
    new_html = html_content.replace("</script>", click_js + "\n</script>")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(new_html)

    print(f"--- HOÀN THÀNH ---")
    print(f"Bây giờ bạn có thể click vào các node trong file {output_path}")

if __name__ == "__main__":
    build_interactive_graph('.', threshold=0.4)