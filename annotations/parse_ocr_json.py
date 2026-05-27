"""
OCR JSON 解析脚本
解析 Textin OCR 识别结果 JSON，抽离核心识别内容，生成精简的 xxx_new.json

用法：
    python parse_ocr_json.py                   # 处理当前目录下所有 *_textin.json
    python parse_ocr_json.py file1.json file2   # 处理指定文件
    python parse_ocr_json.py --dry-run          # 预览模式，不写入文件
"""

import json
import os
import sys
import glob
import argparse
from html.parser import HTMLParser


# ── HTML 表格 → 结构化数据 ──────────────────────────────────────────

class TableHTMLParser(HTMLParser):
    """解析 <table> HTML，输出二维列表 + 合并信息"""

    def __init__(self):
        super().__init__()
        self.rows = []
        self.current_row = []
        self.current_cell = None
        self.current_attrs = {}
        self.in_cell = False

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == "tr":
            self.current_row = []
        elif tag in ("td", "th"):
            self.current_cell = ""
            self.current_attrs = {}
            if "colspan" in attrs_dict:
                self.current_attrs["col_span"] = int(attrs_dict["colspan"])
            if "rowspan" in attrs_dict:
                self.current_attrs["row_span"] = int(attrs_dict["rowspan"])
            self.in_cell = True

    def handle_data(self, data):
        if self.in_cell and self.current_cell is not None:
            self.current_cell += data

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self.in_cell:
            cell_info = {"text": self.current_cell.strip()}
            cell_info.update(self.current_attrs)
            self.current_row.append(cell_info)
            self.current_cell = None
            self.in_cell = False
        elif tag == "tr" and self.current_row is not None:
            self.rows.append(self.current_row)
            self.current_row = []


def parse_table_html(html_str: str) -> list[list[dict]]:
    """将 HTML 表格字符串解析为二维列表"""
    parser = TableHTMLParser()
    try:
        parser.feed(html_str)
    except Exception:
        return []
    return parser.rows


def cells_to_structured(cells: list) -> dict:
    """将 cells 数组转为结构化表格（行列表）"""
    if not cells:
        return {"headers": [], "rows": []}

    # 找出最大行列
    max_row = max((c.get("row") or 0) for c in cells)
    max_col = max((c.get("col") or 0) for c in cells)

    # 构建二维表
    grid = [[None] * (max_col + 1) for _ in range(max_row + 1)]
    for c in cells:
        r, co = c.get("row") or 0, c.get("col") or 0
        cell_data = {"text": c.get("text", "").strip()}
        if c.get("col_span", 1) > 1:
            cell_data["col_span"] = c["col_span"]
        if c.get("row_span", 1) > 1:
            cell_data["row_span"] = c["row_span"]
        grid[r][co] = cell_data

    # 分离表头和数据行（首行作为表头）
    headers = [c for c in grid[0] if c] if grid else []
    rows = []
    for r in grid[1:]:
        row = [c for c in r if c is not None]
        if row:
            rows.append(row)

    return {"headers": headers, "rows": rows}


# ── 核心解析逻辑 ──────────────────────────────────────────────────

def extract_stamp_info(item: dict) -> dict | None:
    """提取印章信息"""
    stamp_data = item.get("stamp")
    if not stamp_data:
        return None
    return {
        "type": stamp_data.get("type", ""),
        "shape": stamp_data.get("stamp_shape", ""),
        "color": stamp_data.get("color", ""),
        "content": stamp_data.get("value", "").strip(),
    }


def parse_detail_item(item: dict) -> dict | None:
    """解析单个 detail item，返回精简的核心内容"""
    item_type = item.get("type")
    sub_type = item.get("sub_type")
    text = item.get("text", "").strip()

    result = {
        "page": item.get("page_id") or 0,
        "index": item.get("paragraph_id") or 0,
        "position": item.get("position", []),
    }

    # ── 段落类 ──
    if item_type == "paragraph":
        if not text:
            return None

        # 标题
        if sub_type == "text_title":
            result["type"] = "title"
            result["level"] = item.get("outline_level", -1)
            result["content"] = text
            return result

        # 目录
        if sub_type == "catalog":
            result["type"] = "catalog"
            result["content"] = text
            return result

        # 表格标题
        if sub_type == "table_title":
            result["type"] = "table_title"
            result["content"] = text
            return result

        # 页眉页脚（默认保留但标记）
        if sub_type in ("header", "footer"):
            result["type"] = sub_type
            result["content"] = text
            return result

        # 侧栏/卡片
        if sub_type in ("sidebar", "card"):
            result["type"] = sub_type
            result["content"] = text
            return result

        # 普通正文
        result["type"] = "text"
        result["content"] = text
        return result

    # ── 表格类 ──
    if item_type == "table":
        table_result = {
            "type": "table",
            "page": item.get("page_id") or 0,
            "index": item.get("paragraph_id") or 0,
            "position": item.get("position", []),
        }

        # 优先用 cells 结构化数据
        cells = item.get("cells")
        if cells:
            table_result["structured"] = cells_to_structured(cells)

        # 同时保留 HTML 文本（便于回溯）
        if text and "<table" in text:
            table_result["html"] = text
            # 如果没有 cells，尝试从 HTML 解析
            if not cells:
                parsed = parse_table_html(text)
                if parsed:
                    headers = [c for c in parsed[0]] if parsed else []
                    rows = parsed[1:] if len(parsed) > 1 else []
                    table_result["structured"] = {"headers": headers, "rows": rows}

        # 表格标题引用
        caption = item.get("caption_id")
        if caption:
            table_result["caption_page"] = caption.get("page_id")
            table_result["caption_index"] = caption.get("paragraph_id")

        return table_result

    # ── 图片类 ──
    if item_type == "image":
        # 印章
        if sub_type == "stamp":
            stamp_info = extract_stamp_info(item)
            if stamp_info:
                return {
                    "type": "stamp",
                    "page": item.get("page_id") or 0,
                    "index": item.get("paragraph_id") or 0,
                    "position": item.get("position", []),
                    "stamp": stamp_info,
                    "text": text if text else None,
                }
            return None

        # 二维码
        if sub_type == "qrcode":
            return {
                "type": "qrcode",
                "page": item.get("page_id") or 0,
                "index": item.get("paragraph_id") or 0,
                "position": item.get("position", []),
                "content": text if text else None,
            }

        # 条形码
        if sub_type == "barcode":
            return {
                "type": "barcode",
                "page": item.get("page_id") or 0,
                "index": item.get("paragraph_id") or 0,
                "position": item.get("position", []),
                "content": text if text else None,
            }

        # 普通图片（仅标记存在）
        return {
            "type": "image",
            "page": item.get("page_id") or 0,
            "index": item.get("paragraph_id") or 0,
            "position": item.get("position", []),
            "content": text if text else None,
        }

    # ── 其他未知类型 ──
    if text:
        result["type"] = sub_type or item_type or "unknown"
        result["content"] = text
        return result

    return None


def process_ocr_json(input_path: str) -> dict:
    """处理单个 OCR JSON 文件，返回精简后的结果"""
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    result_data = data.get("result", {})
    detail = result_data.get("detail", [])

    # 逐条解析
    contents = []
    for item in detail:
        parsed = parse_detail_item(item)
        if parsed:
            contents.append(parsed)

    # 按页码和段落顺序排序
    contents.sort(key=lambda x: (x.get("page", 0), x.get("index", 0)))

    # 去掉排序用字段
    for c in contents:
        c.pop("index", None)

    # 统计信息
    stats = {}
    for c in contents:
        t = c.get("type", "unknown")
        stats[t] = stats.get(t, 0) + 1

    # 构建输出
    output = {
        "file": os.path.basename(input_path),
        "total_pages": result_data.get("total_page_number", 0),
        "stats": stats,
        "contents": contents,
    }

    # 提取合同关键元数据（标题、买卖双方、编号等）
    metadata = extract_metadata(contents)
    if metadata:
        output["metadata"] = metadata

    return output


def extract_metadata(contents: list[dict]) -> dict:
    """从识别内容中尝试提取合同关键元数据"""
    meta = {}
    all_text = " ".join(
        c.get("content", "") for c in contents if c.get("type") in ("title", "text")
    )

    import re

    # 标题
    for c in contents:
        if c.get("type") == "title" and c.get("level", -1) >= 0:
            text = c.get("content", "")
            if any(kw in text for kw in ("合同", "协议", "采购", "订单")):
                meta["document_title"] = text
                break

    # 买方/卖方/需方/供方/甲方/乙方
    party_patterns = [
        (r"买\s*方[：:]\s*(.+?)(?:\s{2,}|卖|$)", "buyer"),
        (r"卖\s*方[：:]\s*(.+?)(?:\s{2,}|$)", "seller"),
        (r"需\s*方[：:]\s*(.+?)(?:\s{2,}|供|$)", "buyer"),
        (r"供\s*方[：:]\s*(.+?)(?:\s{2,}|$)", "seller"),
        (r"甲\s*方[：:]\s*(.+?)(?:\s{2,}|乙|$)", "party_a"),
        (r"乙\s*方[：:]\s*(.+?)(?:\s{2,}|$)", "party_b"),
    ]
    for pattern, key in party_patterns:
        m = re.search(pattern, all_text)
        if m:
            meta[key] = m.group(1).strip()[:100]

    # 合同编号
    for p in [r"合同编号[：:]\s*(\S+)", r"委托编号[：:]\s*(\S+)", r"编号[：:]\s*(\S+)"]:
        m = re.search(p, all_text)
        if m:
            meta["contract_no"] = m.group(1).strip()
            break

    # 签订日期
    m = re.search(r"签订日期[：:]\s*(\d{4}年\d{1,2}月\d{1,2}日)", all_text)
    if m:
        meta["sign_date"] = m.group(1)

    # 合同金额
    m = re.search(r"(\d[\d,.]*)\s*元", all_text)
    if m:
        amount_str = m.group(1).replace(",", "")
        try:
            meta["amount"] = float(amount_str)
        except ValueError:
            pass

    return meta if meta else None


def main():
    parser = argparse.ArgumentParser(description="OCR JSON 解析脚本")
    parser.add_argument("files", nargs="*", help="指定文件或目录")
    parser.add_argument("--dry-run", action="store_true", help="预览模式，不写入文件")
    args = parser.parse_args()

    # 确定输入文件列表
    if args.files:
        input_files = []
        for f in args.files:
            if os.path.isdir(f):
                input_files.extend(glob.glob(os.path.join(f, "*_textin.json")))
            elif os.path.isfile(f):
                input_files.append(f)
            else:
                input_files.extend(glob.glob(f))
    else:
        # 默认处理当前目录
        input_files = glob.glob("*_textin.json")

    if not input_files:
        print("未找到匹配的 JSON 文件")
        return

    print(f"找到 {len(input_files)} 个文件待处理")

    success = 0
    failed = 0

    for i, input_path in enumerate(input_files, 1):
        try:
            result = process_ocr_json(input_path)

            # 生成输出路径
            base = os.path.splitext(input_path)[0]
            # 去掉 _textin 后缀，加上 _v1 后缀
            if base.endswith("_textin"):
                base = base[:-7]
            output_path = base + "_v1.json"

            if args.dry_run:
                print(f"\n[{i}/{len(input_files)}] {os.path.basename(input_path)} (dry-run)")
                print(f"  页数: {result['total_pages']}")
                print(f"  统计: {result['stats']}")
                if result.get("metadata"):
                    print(f"  元数据: {json.dumps(result['metadata'], ensure_ascii=False)}")
                # 打印前3条内容预览
                for c in result["contents"][:3]:
                    ctype = c.get("type", "?")
                    content = c.get("content", c.get("html", ""))[:80]
                    print(f"  [{ctype}] {content}")
                if len(result["contents"]) > 3:
                    print(f"  ... 共 {len(result['contents'])} 条")
            else:
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                print(
                    f"[{i}/{len(input_files)}] {os.path.basename(input_path)} -> {os.path.basename(output_path)} "
                    f"({result['stats']})"
                )

            success += 1
        except Exception as e:
            print(f"[{i}/{len(input_files)}] {os.path.basename(input_path)} 失败: {e}")
            failed += 1

    print(f"\n完成: 成功 {success}, 失败 {failed}")


if __name__ == "__main__":
    main()
