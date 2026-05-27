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
│   └── contract001.pdf          # Original contract PDF / 原始合同文件
└── annotations/
    ├── contract001_v1.json         # Annotation / 标注 JSON
    └── contract001_v1.md          # Markdown
```

### Annotation Schema Example / 标注格式示例


```json
{
  "total_pages": 6,
  "stats": {
    "text": 43,
    "title": 12,
    "table_title": 1,
    "table": 2,
    "stamp": 2
  },
  "contents": [
    {
      "page": 1,
      "position": [
        657,
        112,
        995,
        112,
        995,
        142,
        657,
        142
      ],
      "type": "text",
      "content": "合同编号：HRK2019-3-01"
    },
    {
      "page": 1,
      "position": [
        176,
        231,
        977,
        231,
        977,
        334,
        176,
        334
      ],
      "type": "title",
      "level": 0,
      "content": "环境污染防治管理中心大气全面量化管理医废处置废气监督性监测及应急演练项目"
    },
    {
      "type": "table",
      "page": 6,
      "position": [
        122,
        1106,
        1090,
        1097,
        1094,
        1490,
        120,
        1498
      ],
      "structured": {
        "headers": [
          {
            "text": "买方<br>（盖章）"
          },
          {
            "text": "环境污染防治管理中心"
          },
          {
            "text": ""
          },
          {
            "text": "买方<br>（盖章）"
          },
          {
            "text": "XXX有限公司"
          }
        ],
        "rows": [
          [
            {
              "text": "法人（代表）签字"
            },
            {
              "text": "吴世"
            },
            {
              "text": "",
              "row_span": 2
            },
            {
              "text": "法人（代表）签字"
            },
            {
              "text": "罗云"
            }
          ],
          [
            {
              "text": "日期："
            },
            {
              "text": "2019 年4月15日"
            },
            {
              "text": "日期："
            },
            {
              "text": "2019年3 月7 日"
            }
          ]
        ]
      },
      "html": "<table border=\"1\" ><tr>\n<td>买方<br>（盖章）</td>\n<td>环境污染防治管理中心</td>\n<td></td>\n<td>买方<br>（盖章）</td>\n<td>XXX有限公司</td>\n</tr><tr>\n<td>法人（代表）签字</td>\n<td>吴世</td>\n<td rowspan=\"2\"></td>\n<td>法人（代表）签字</td>\n<td>罗云</td>\n</tr><tr>\n<td>日期：</td>\n<td>2019 年4月15日</td>\n<td>日期：</td>\n<td>2019年3 月7 日</td>\n</tr></table>"
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