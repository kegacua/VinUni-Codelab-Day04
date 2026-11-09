import json
import os
from typing import List, Dict, Any
from datetime import datetime

RAW_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "raw-data")

# Đảm bảo thư mục raw-data tồn tại
os.makedirs(RAW_DATA_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# Tool #1: search_product_catalog
# ---------------------------------------------------------------------------

def search_product_catalog(category: str, max_price: int = 999999999999) -> List[Dict[str, Any]]:
    """
    Tra cứu sản phẩm/dịch vụ Vingroup theo danh mục và giá tối đa.
    
    Args:
        category: Loại sản phẩm ('xe_dien' hoặc 'du_lich').
        max_price: Giá tối đa (VNĐ). Mặc định không giới hạn.
    
    Returns:
        Danh sách sản phẩm phù hợp điều kiện.
    """
    catalog_file = os.path.join(RAW_DATA_DIR, "product_catalog.json")
    
    if not os.path.exists(catalog_file):
        return []

    try:
        with open(catalog_file, "r", encoding="utf-8") as f:
            products = json.load(f)
    except (json.JSONDecodeError, IOError):
        return []
    
    # Lọc sản phẩm theo category và giá
    filtered_products = [
        p for p in products 
        if p.get("category") == category and p.get("price_vnd", 0) <= max_price
    ]
    
    return filtered_products


# ---------------------------------------------------------------------------
# Tool #2: submit_support_ticket
# ---------------------------------------------------------------------------

def submit_support_ticket(
    customer_name: str,
    issue_description: str,
    priority: str = "medium"
) -> Dict[str, Any]:
    """
    Ghi nhận yêu cầu hỗ trợ của khách hàng vào hệ thống ticket.
    
    Args:
        customer_name: Tên khách hàng.
        issue_description: Mô tả vấn đề cần hỗ trợ.
        priority: Mức độ ưu tiên ('low', 'medium', 'high'). Mặc định 'medium'.
    
    Returns:
        Thông tin ticket vừa tạo bao gồm ticket_id, status.
    """
    tickets_file = os.path.join(RAW_DATA_DIR, "support_tickets.json")
    tickets = []
    
    # Load existing tickets nếu file tồn tại
    if os.path.exists(tickets_file):
        try:
            with open(tickets_file, "r", encoding="utf-8") as f:
                tickets = json.load(f)
        except (json.JSONDecodeError, IOError):
            tickets = []

    # Tạo ticket_id mới theo format: TK-YYYYMMDD-SEQ
    today = datetime.now().strftime("%Y%m%d")
    today_tickets = [t for t in tickets if t.get("ticket_id", "").startswith(f"TK-{today}")]
    seq = len(today_tickets) + 1
    ticket_id = f"TK-{today}-{seq:03d}"
    
    new_ticket = {
        "ticket_id": ticket_id,
        "customer_name": customer_name,
        "issue_description": issue_description,
        "priority": priority,
        "status": "open",
        "created_at": datetime.now().isoformat()
    }
    
    tickets.append(new_ticket)
    
    # Lưu lại vào file
    with open(tickets_file, "w", encoding="utf-8") as f:
        json.dump(tickets, f, ensure_ascii=False, indent=4)
        
    return new_ticket


# ---------------------------------------------------------------------------
# TOOL_DEFINITIONS — JSON Schemas mô tả cho LLM
# ---------------------------------------------------------------------------

TOOL_DEFINITIONS = [
    {
        "name": "search_product_catalog",
        "description": "Tra cứu sản phẩm/dịch vụ Vingroup theo danh mục và giá tối đa. Dùng để tìm kiếm thông tin xe điện, du lịch, v.v...",
        "parameters": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "description": "Loại sản phẩm cần tra cứu (ví dụ: 'xe_dien' hoặc 'du_lich')."
                },
                "max_price": {
                    "type": "integer",
                    "description": "Giá tối đa bằng VNĐ. Mặc định là không giới hạn."
                }
            },
            "required": ["category"]
        }
    },
    {
        "name": "submit_support_ticket",
        "description": "Ghi nhận yêu cầu hỗ trợ, khiếu nại, hoặc thắc mắc của khách hàng vào hệ thống ticket.",
        "parameters": {
            "type": "object",
            "properties": {
                "customer_name": {
                    "type": "string",
                    "description": "Họ và tên của khách hàng."
                },
                "issue_description": {
                    "type": "string",
                    "description": "Mô tả chi tiết vấn đề khách hàng đang gặp phải hoặc yêu cầu hỗ trợ."
                },
                "priority": {
                    "type": "string",
                    "enum": ["low", "medium", "high"],
                    "description": "Mức độ ưu tiên của ticket (mặc định là 'medium')."
                }
            },
            "required": ["customer_name", "issue_description"]
        }
    }
]


# ---------------------------------------------------------------------------
# TOOL_MAP — Ánh xạ tên tool → hàm thực thi
# ---------------------------------------------------------------------------

TOOL_MAP = {
    "search_product_catalog": search_product_catalog,
    "submit_support_ticket": submit_support_ticket
}