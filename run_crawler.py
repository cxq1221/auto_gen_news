import asyncio
import os
import sys
import yaml
from loguru import logger

async def main():
    # 加载配置
    config_path = os.path.join('config', 'config.yaml')
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # 创建爬虫实例
    from src.crawler import Crawler
    crawler = Crawler(config)
    
    try:
        # 运行爬虫
        logger.info("开始爬取数据...")
        products = await crawler.fetch_all()
        
        # 输出结果
        logger.info(f"成功爬取 {len(products)} 个产品")
        for product in products:
            logger.info("-" * 50)
            logger.info(f"产品名称: {product['name']}")
            logger.info(f"产品链接: {product['url']}")
            logger.info(f"描述: {product['description']}")
            logger.info(f"发布时间: {product['release_date']}")
            logger.info(f"Stars: {product['stars']}")
            logger.info(f"Forks: {product['forks']}")
            logger.info(f"主要语言: {product['language']}")
            
    except Exception as e:
        logger.error(f"爬虫运行失败: {str(e)}")
        raise

if __name__ == "__main__":
    # 设置日志
    logger.remove()  # 移除默认的处理器
    
    # 添加文件处理器
    logger.add(
        "logs/crawler.log",
        rotation="500 MB",
        retention="10 days",
        level="INFO",
        encoding="utf-8",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}"
    )
    
    # 添加控制台处理器
    logger.add(
        sys.stdout,
        level="INFO",
        format="{message}"
    )
    
    # 运行主程序
    asyncio.run(main()) 