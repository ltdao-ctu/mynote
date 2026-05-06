import os
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import normalize
from pyvis.network import Network
import numpy as np
import json
import re

from dotenv import load_dotenv # Thêm thư viện này

# Nạp các biến môi trường từ file .env
load_dotenv()

# Lấy cấu hình từ .env
THRESHOLD = float(os.getenv("THRESHOLD"))
KB_PATH = os.getenv("KB_PATH")


def clean_markdown_content(text):
    """Làm sạch nội dung Markdown để embedding tốt hơn"""
    # Xóa code blocks
    text = re.sub(r'```[\s\S]*?```', '', text)
    text = re.sub(r'`[^`]+`', '', text)
    
    # Xóa links nhưng giữ text
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    
    # Xóa image syntax
    text = re.sub(r'!\[([^\]]*)\]\([^\)]+\)', '', text)
    
    # Xóa HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Xóa markdown syntax (*, #, -, etc)
    text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\*+\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^-+\s+', '', text, flags=re.MULTILINE)
    
    # Xóa extra whitespace
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    
    return text



def build_interactive_graph(directory, threshold=THRESHOLD):
    print(threshold)
    print("[*] Loading Vietnamese model...")
    model = SentenceTransformer('keepitreal/vietnamese-sbert')
    
    # Quét đệ quy tất cả file .md trong thư mục và subfolders
    files = []
    for root, dirs, files_in_dir in os.walk(directory):
        for file in files_in_dir:
            if file.endswith('.md'):
                # Lưu đường dẫn tương đối từ directory gốc
                relative_path = os.path.relpath(os.path.join(root, file), directory)
                files.append(relative_path)
    
    documents = []
    valid_files = []
    file_contents = {}

    for file in files:
        file_path = os.path.join(directory, file)
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if len(content) > 10:
                # Làm sạch markdown syntax trước embedding
                cleaned_content = clean_markdown_content(content)
                documents.append(cleaned_content)
                valid_files.append(file)
                file_contents[file] = content  # Giữ nội dung gốc cho hiển thị

    if not valid_files: return

    embeddings = model.encode(documents)
    sim_matrix = cosine_similarity(embeddings)
    
    # Normalize similarity scores để dễ debug
    print(f"[*] Similarity scores - Min: {sim_matrix.min():.4f}, Max: {sim_matrix.max():.4f}, Mean: {sim_matrix.mean():.4f}")
    print(f"[*] Threshold: {threshold}")

    # Khởi tạo Network
    net = Network(height="750px", width="100%", bgcolor="#222222", font_color="white")
    net.force_atlas_2based()
    
    # Cấu hình vật lý: stabilize rồi dừng lại
    net.set_options("""
    var options = {
      "physics": {
        "enabled": true,
        "forceAtlas2Based": {
          "gravitationalConstant": -50,
          "centralGravity": 0.01,
          "springLength": 200,
          "springConstant": 0.08,
          "damping": 0.4,
          "avoidOverlap": 0.1
        },
        "solver": "forceAtlas2Based",
        "timestep": 0.35,
        "stabilization": {
          "iterations": 500,
          "fit": true,
          "updateInterval": 25
        }
      }
    }
    """)

    # Tính degree (số kết nối) của mỗi file
    node_degrees = {file: 0 for file in valid_files}
    edges_data = []

    for i in range(len(valid_files)):
        for j in range(i + 1, len(valid_files)):
            score = float(sim_matrix[i][j])
            if score > threshold:
                edges_data.append((valid_files[i], valid_files[j], score))
                node_degrees[valid_files[i]] += 1
                node_degrees[valid_files[j]] += 1

    # Tìm max degree để tính màu
    max_degree = max(node_degrees.values()) if node_degrees.values() else 1

    # Thêm nodes với màu tùy theo degree
    for i, file in enumerate(valid_files):
        degree = node_degrees[file]
        
        # Tô màu dựa trên degree
        if degree == 0:
            color = "#00ffcc"  # Xanh - không có kết nối
        elif degree <= max_degree / 3:
            color = "#ffcc00"  # Vàng - kết nối thấp
        elif degree <= 2 * max_degree / 3:
            color = "#ff9900"  # Cam - kết nối trung bình
        else:
            color = "#ff6b6b"  # Đỏ - kết nối cao
        
        net.add_node(file, label=file, title=f"Click để xem nội dung {file} (kết nối: {degree})", color=color)

    # Thêm edges
    for file1, file2, score in edges_data:
        net.add_edge(file1, file2, value=score, weight=score)

    # Xuất file HTML
    output_path = "index.html"
    net.save_graph(output_path)

    # --- ĐOẠN CHÈN JS ĐỂ CLICK HIỂN THỊ MARKDOWN ---
    # Đọc lại file vừa tạo để chèn mã
    with open(output_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Thêm marked.js vào head
    marked_script = '<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>'
    html_content = html_content.replace('<meta charset="utf-8">', '<meta charset="utf-8">\n' + marked_script)

    # Thêm modal vào cuối body
    modal_html = '''
<div class="modal fade" id="markdownModal" tabindex="-1" aria-labelledby="markdownModalLabel" aria-hidden="true">
  <div class="modal-dialog modal-lg">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title" id="markdownModalLabel">Nội dung Markdown</h5>
        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
      </div>
      <div class="modal-body">
        <div id="markdown-body"></div>
      </div>
    </div>
  </div>
</div>
'''
    html_content = html_content.replace('</body>', modal_html + '\n</body>')

    # Xóa tất cả click handler cũ
    html_content = re.sub(r'network\.on\("click".*?\}\);', '', html_content, flags=re.DOTALL)

    # Ghi file main.js với dữ liệu markdown và handler ngoài
    file_contents_json = json.dumps(file_contents, ensure_ascii=False)
    main_js = f'''
var fileContents = {file_contents_json};

function bindMarkdownClickHandler() {{
    if (typeof network === 'undefined') {{
        return;
    }}

    network.on("click", function (params) {{
        if (params.nodes.length > 0) {{
            var nodeId = params.nodes[0];
            var content = fileContents[nodeId];
            if (content) {{
                document.getElementById('markdown-body').innerHTML = marked.parse(content);
                var modal = new bootstrap.Modal(document.getElementById('markdownModal'));
                modal.show();
            }}
        }}
    }});
}}

function disablePhysicsAfterStabilization() {{
    if (typeof network === 'undefined') {{
        return;
    }}
    
    network.once('stabilizationIterationsDone', function() {{
        network.setOptions({{ physics: false }});
        console.log('Graph stabilized and physics disabled');
    }});
}}

if (document.readyState === 'complete') {{
    bindMarkdownClickHandler();
    disablePhysicsAfterStabilization();
}} else {{
    window.addEventListener('load', function() {{
        bindMarkdownClickHandler();
        disablePhysicsAfterStabilization();
    }});
}}
'''
    with open('main.js', 'w', encoding='utf-8') as f:
        f.write(main_js)

    # Thêm tham chiếu đến main.js
    html_content = html_content.replace('</body>', '    <script src="main.js"></script>\n</body>')

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print("--- COMPLETE ---")
    print(f"You can now click nodes in {output_path} to view markdown content.")

if __name__ == "__main__":
    build_interactive_graph(KB_PATH)