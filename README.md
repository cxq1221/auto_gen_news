# AI News Generator

一个自动化的AI新闻生成系统，通过爬取多个数据源（GitHub、Product Hunt、Futurepedia等）来收集最新的AI相关项目、工具和研究成果，并自动生成新闻内容。

## 功能特点

- 多数据源爬取
  - GitHub AI项目
  - Product Hunt AI产品
  - Futurepedia AI工具
  - Hugging Face AI模型
  - Papers with Code AI论文

- 智能内容生成
  - 新闻内容生成
  - 产品描述优化
  - 标题生成

- 图片处理
  - 自动下载
  - 优化处理
  - CDN支持

## 技术栈

- Python 3.8+
- aiohttp（异步HTTP客户端）
- loguru（日志系统）
- PyYAML（配置文件处理）

## 快速开始

1. 克隆仓库
```bash
git clone https://github.com/yourusername/auto_gen_news.git
cd auto_gen_news
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 配置
- 复制 `config/config.yaml.example` 到 `config/config.yaml`
- 修改配置文件中的API密钥和其他设置

4. 运行爬虫
```bash
python ./run_crawler.py
```

## 项目结构

```
auto_gen_news/
├── config/
│   └── config.yaml
├── docs/
│   └── progress.md
├── logs/
│   └── crawler.log
├── src/
│   ├── crawler/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── github.py
│   ├── __init__.py
│   └── run_crawler.py
└── requirements.txt
```

## 开发进度

查看 [进度日志](docs/progress.md) 了解项目的最新进展。

## 贡献指南

- [x] 基础框架搭建
- [ ] 爬虫模块实现
- [ ] 内容生成模块实现
- [ ] 图片处理模块实现
- [ ] 调度模块实现
- [ ] 测试用例编写
- [ ] 文档完善

## 许可证

MIT License 