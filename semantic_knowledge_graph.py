import os
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from pyvis.network import Network
import numpy as np
import json
import re

from dotenv import load_dotenv # Thêm thư viện này

# Nạp các biến môi trường từ file .env
load_dotenv()

# Lấy cấu hình từ .env
THRESHOLD = float(os.getenv("THRESHOLD"))


def build_interactive_graph(directory, threshold=THRESHOLD):
    print(threshold)
    print("[*] Loading Vietnamese model...")
    model = SentenceTransformer('keepitreal/vietnamese-sbert')
    
    files = [f for f in os.listdir(directory) if f.endswith('.md')]
    documents = []
    valid_files = []
    file_contents = {}

    for file in files:
        with open(os.path.join(directory, file), 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if len(content) > 10: 
                documents.append(content)
                valid_files.append(file)
                file_contents[file] = content

    if not valid_files: return

    embeddings = model.encode(documents)
    sim_matrix = cosine_similarity(embeddings)
    #print(sim_matrix)

    # Khởi tạo Network
    net = Network(height="750px", width="100%", bgcolor="#222222", font_color="white")
    net.force_atlas_2based()

    for i, file in enumerate(valid_files):
        # Chúng ta dùng tên file làm ID để dễ xử lý link
        net.add_node(file, label=file, title=f"Click để xem nội dung {file}", color="#00ffcc")

    for i in range(len(valid_files)):
        for j in range(i + 1, len(valid_files)):
            score = float(sim_matrix[i][j])
            if score > threshold:
                net.add_edge(valid_files[i], valid_files[j], value=score, weight=score)
            #else:
            #    print(score)

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

if (document.readyState === 'complete') {{
    bindMarkdownClickHandler();
}} else {{
    window.addEventListener('load', bindMarkdownClickHandler);
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
    build_interactive_graph('.')