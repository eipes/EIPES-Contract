# EIPES-ContractBench

<div align="center">

An open benchmark and dataset project for OCR, Document AI and multimodal contract understanding.

面向 OCR、Document AI 与多模态合同理解的开源数据集与 Benchmark 项目。

</div>

---

# Overview | 项目简介

EIPES-ContractBench aims to build high-quality contract document datasets for:

EIPES-ContractBench 致力于构建高质量合同文档数据集，用于：

- OCR
- Layout Analysis / 文档版面分析
- Table Recognition / 表格识别
- Key Information Extraction (KIE) / 关键信息抽取
- Clause Extraction / 条款抽取
- Document Structuring / 文档结构化
- Multimodal Document Understanding / 多模态文档理解

This repository includes:

本仓库包含：

- Sample contract documents / 合同样例数据
- OCR Ground Truth / OCR 标注

---

# Quick Tour & Data Samples | 快速了解与数据样例

### Repository Structure / 目录结构

```text
EIPES-ContractBench/
├── README.md
├── samples/
│   └── contract_001.pdf          # Original contract PDF / 原始合同文件
└── annotations/
    └── contract_001.json         # Annotation / 标注 JSON
```

### Annotation Schema Example / 标注格式示例


```json
{
  "doc_id": "contract_001",
  "meta": {
    "doc_type": "Purchase Contract / 采购合同",
    "total_pages": 1
  },
  "pages": [
    {
      "page_index": 0,
      "size": { "width": 1240, "height": 1754 },
      
      "comment_1": "1. OCR & Layout Analysis Layer / 文本块与版面分析层",
      "layout_elements": [
        {
          "id": "block_0",
          "type": "title",
          "bbox": [100, 150, 1140, 220],
          "text": "物资采购合同"
        },
        {
          "id": "block_1",
          "type": "table",
          "bbox": [100, 500, 1140, 900],
          "cells": [
            { "row": 0, "col": 0, "text": "序号", "bbox": [110, 510, 200, 550] }
          ]
        }
      ],
      
      "comment_2": "2. Key Information Extraction (KIE) / 关键实体抽取层",
      "kie_entities": [
        { "label": "party_a", "text": "某某科技有限公司", "bbox": [200, 300, 500, 340] },
        { "label": "party_b", "text": "某某制造有限公司", "bbox": [200, 350, 500, 390] },
        { "label": "contract_amount", "text": "￥1,000,000.00", "bbox": [800, 1200, 950, 1240] }
      ]
    }
  ],
  
  "comment_3": "3. High-level Semantic Clause Layer / 高层级语义条款层",
  "clauses": [
    {
      "type": "dispute_resolution",
      "text": "本合同在履行过程中发生的争议，由双方当事人协商解决；协商不成的，提交上海仲裁委员会仲裁。"
    }
  ]
}

```
---

# Data Sources | 数据来源

The data is sourced from the internet.

数据来自网络。

This repository:

本仓库：

* Does NOT claim ownership of original documents
不声明原始合同文件所有权
* Provides limited sample data for research and benchmarking purposes
仅提供少量 Sample 数据用于研究与 Benchmark

---

# Contact | 联系我

For technical discussions, bug reports, or collaboration, please use the following channels:

如有技术交流、问题反馈或合作意向，可以通过以下方式联系：

* **Email**: relove100@gmail.com