# BioRegex-Hub  
**面向生物统计与精算的标准正则知识图谱基础库（初期版本）**

BioRegex-Hub 是一个开源项目，旨在为生物统计、临床试验与精算建模提供 **权威、可维护、可扩展** 的正则规则库。  
本仓库仅包含 **项目初期阶段（0-6 个月）** 的核心代码与文档，聚焦标准正则库本身，暂不提供联邦学习等高级功能。

---

## 🚀 快速开始
```bash
git clone https://github.com/your-org/BioRegex-Hub.git
cd BioRegex-Hub
docker-compose up -d        # 一键启动前后端及数据库
```
浏览器访问 http://localhost:3000 即可体验。

---

## 📦 核心功能
| 功能模块           | 状态 | 说明 |
|--------------------|------|------|
| 权威规则采集       | ✅   | 自动爬取 FDA/EMA 官网，结构化入库 |
| 正则库查询 API     | ✅   | RESTful，支持按监管依据、数据类型过滤 |
| 用户自定义规则提交 | ✅   | Web 表单 + 专家审核 |
| 多格式文件解析     | ✅   | SAS7BDAT / CSV / Excel / SDTM XML |
| 统计验证 (KS 检验) | ✅   | R + SAS 宏，一键报告 |

---

## 🗂️ 仓库结构
```
├── backend/          # Python FastAPI 服务
├── frontend/         # React + TypeScript
├── db/               |-- init.sql
├── parsers/          # 多格式文件解析脚本
├── rules/            # 初始 300+ 条权威正则（CSV + JSON）
├── docs/             # 详细设计与 API 文档
└── docker-compose.yml
```

---

## 🤝 贡献指南
1. 发现规则缺失？→ 提 [Issue](https://github.com/your-org/BioRegex-Hub/issues/new)  
2. 想提交正则？→ 用 `/contribute` 页面，填写表单并上传监管依据 PDF。  
3. 开发者 → 见 [CONTRIBUTING.md](CONTRIBUTING.md)

---

## 📄 许可证
MIT © 2024 BioRegex-Hub Contributors# BioRegex-Hub
