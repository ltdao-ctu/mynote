# Knowledge Graph - Workflow Documentation

## 概述 Overview
Hệ thống tự động theo dõi, đồng bộ hóa file markdown từ Obsidian và Google Drive, sau đó tạo interactive knowledge graph.

## 📋 Các Scripts

### 1. **watcher.py** - Main Monitor Script
**Mục đích**: Theo dõi thay đổi file từ 2 nguồn và tự động build graph

**Theo dõi (Monitor)**:
- ✅ `SOURCE_DOCX_PATH` - Google Drive Raw folder
- ✅ `OBSIDIAN_PATH` - Obsidian vault folder  

**Xử lý sự kiện**:
- **File .docx mới/thay đổi**: Chuyển đổi sang markdown
- **File .md mới**: 
  - Kiểm tra xem có `.docx` trùng tên không
  - Nếu không → Copy vào KB folder
  - Tự động build graph

**Chạy**:
```bash
python watcher.py
```

---

### 2. **build_graph.py** - Manual Graph Builder
**Mục đích**: Build graph từ tất cả file md trong KB (chạy thủ công)

**Sử dụng khi**:
- Muốn build lại graph thủ công
- File cấu hình KB đã thay đổi
- Cần cập nhật graph mà không muốn theo dõi file

**Chạy**:
```bash
python build_graph.py
```

---

### 3. **sync_and_build.py** - Full Sync & Build
**Mục đích**: Đồng bộ từ cả 2 nguồn + build graph (chạy thủ công)

**Quy trình**:
1. Đồng bộ file `.md` từ `SOURCE_DOCX_PATH` → KB
2. Đồng bộ file `.md` từ `OBSIDIAN_PATH` → KB
3. Build interactive graph

**Chạy**:
```bash
python sync_and_build.py
```

**Output**:
```
============================================================
   SYNC & BUILD KNOWLEDGE GRAPH
============================================================

[*] Cấu hình:
    SOURCE_DOCX_PATH: G:/My Drive/My KB/Raw
    OBSIDIAN_PATH: G:/My Drive/Obsidian/Raw
    KB_PATH: D:\github\mynote\KB

[*] Đang đồng bộ file...
    SOURCE_DOCX: Đồng bộ 5 file
    OBSIDIAN: Đồng bộ 3 file

[*] Tổng cộng đồng bộ: 8 file
[*] Tổng số file markdown trong KB: 45

[*] Đang xây dựng knowledge graph...
[✓] Hoàn thành xây dựng graph!
[✓] Graph đã được lưu vào: index.html

============================================================
```

---

## 🔧 Cấu hình (.env)

```ini
# Google Drive paths
SOURCE_DOCX_PATH="G:/My Drive/My KB/Raw"
OBSIDIAN_PATH="G:/My Drive/Obsidian/Raw"

# Knowledge base folder
KB_PATH=KB

# Similarity threshold (0-1)
THRESHOLD=0.7

# Git config
GIT_BRANCH=main
```

**Lưu ý**: 
- Cấp quyền Google Drive nếu cần
- Đảm bảo đường dẫn tồn tại
- Tạo symbolic link nếu thư mục không trực tiếp trên máy

---

## 📊 Workflow Tự động

```
┌─────────────────────────────────────────┐
│        Watcher Running (monitor)         │
└────────────┬────────────────────────────┘
             │
             ├─────────────────────────────────────────┐
             │                                         │
    ┌────────▼─────────┐                  ┌───────────▼─────────┐
    │ .docx Changed    │                  │ .md File Created    │
    │ (SOURCE_DOCX)    │                  │ (OBSIDIAN or SOURCE)│
    └────────┬─────────┘                  └───────────┬─────────┘
             │                                        │
             ▼                                        ▼
    ┌─────────────────┐                   ┌─────────────────────┐
    │ run_workflow()  │                   │ Check if docx       │
    │ (doc2md.py)     │                   │ with same name      │
    │ Convert DOCX→MD │                   │ already exists      │
    └────────┬────────┘                   └────────┬────────────┘
             │                                     │
             └──────────────────┬──────────────────┘
                                │
                    ┌───────────▼──────────┐
                    │ Copy .md to KB       │
                    │ (if no matching docx)│
                    └───────────┬──────────┘
                                │
                    ┌───────────▼────────────────┐
                    │ build_interactive_graph()  │
                    │ • Parse all .md files     │
                    │ • Create embeddings       │
                    │ • Calculate similarity    │
                    │ • Generate index.html     │
                    └───────────────────────────┘
```

---

## 🎯 Knowledge Graph Features

### Nodes (File Markdown)
- **Màu**: Dựa trên số lượng kết nối
  - 🟦 Xanh: Không có kết nối
  - 🟨 Vàng: Kết nối thấp
  - 🟧 Cam: Kết nối trung bình
  - 🟥 Đỏ: Kết nối cao

- **Kích thước**: Proportional to connections

- **Tương tác**: Click để xem nội dung markdown

### Edges (Liên hệ giữa file)
- **Trọng số**: Tính theo cosine similarity
- **Threshold**: Configurable via `THRESHOLD` (mặc định 0.7)

### Model
- **Embeddings**: Vietnamese SBERT (`keepitreal/vietnamese-sbert`)
- **Similarity**: Cosine similarity between documents
- **Physics**: Force-directed layout (stabilized)

---

## 💡 Workflow Tùy chọn

### Scenario 1: Development Mode
Chỉ build graph một lần khi cần:
```bash
python build_graph.py
```

### Scenario 2: Production Mode  
Chạy watcher liên tục để tự động cập nhật:
```bash
python watcher.py
# Bấm Ctrl+C để dừng
```

### Scenario 3: Full Sync Mode
Đồng bộ từ 2 nguồn rồi build:
```bash
python sync_and_build.py
```

---

## 📌 Lưu ý Quan trọng

1. **Debounce (5 giây)**: Tránh trigger nhiều lần liên tục
2. **DOCX Priority**: Nếu có `.docx`, file `.md` không được copy
3. **Recursive**: Theo dõi tất cả subfolder
4. **Unicode Support**: Hỗ trợ tiếng Việt & ký tự đặc biệt
5. **Error Handling**: Log lỗi nhưng tiếp tục chạy

---

## 🐛 Troubleshooting

| Vấn đề | Giải pháp |
|--------|----------|
| Script không chạy | Kiểm tra `.env`, đảm bảo đường dẫn hợp lệ |
| Không copy file md | Kiểm tra xem có `.docx` trùng tên không |
| Graph không update | Run `python build_graph.py` thủ công |
| Lỗi embedding | Kiểm tra internet (cần download model SBERT) |
| Memory high | Giảm số file md hoặc split vào subfolders |

---

## 📁 Project Structure

```
mynote/
├── watcher.py              # Main monitor (auto-rebuild)
├── build_graph.py          # Manual graph builder
├── sync_and_build.py       # Full sync + build
├── semantic_knowledge_graph.py  # Graph generation engine
├── doc2md.py               # DOCX → Markdown converter
├── sync_obsidian.py        # Legacy sync script
├── .env                    # Configuration
├── KB/                     # Knowledge base folder
│   ├── file1.md
│   ├── file2.md
│   └── ...
└── index.html              # Generated interactive graph
```

---

## 🚀 Quick Start

```bash
# 1. Cấu hình .env
# (Chỉnh sửa SOURCE_DOCX_PATH, OBSIDIAN_PATH, KB_PATH)

# 2. Chạy watcher
python watcher.py

# 3. Thêm file vào SOURCE_DOCX_PATH hoặc OBSIDIAN_PATH

# 4. Mở index.html trong browser để xem graph

# 5. Bấm Ctrl+C để dừng watcher
```

---

**Last Updated**: 2026-05-13  
**Status**: ✅ Production Ready
