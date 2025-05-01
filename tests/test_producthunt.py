import asyncio
import yaml
from loguru import logger
from src.crawler import ProductHuntCrawler

# 配置日志
logger.add("crawler.log", rotation="1 day", level="INFO")

async def test_producthunt_crawler():
    # 加载配置
    with open("config/config.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    
    # 创建爬虫实例
    crawler = ProductHuntCrawler(config, max_products=1)
    
    try:
        # 执行爬取
        logger.info("开始测试 Product Hunt 爬虫...")
        products = await crawler.fetch()

        if products:
            product = products[0]
            logger.info(f"\n产品名称: {product['name']}")
        else:
            logger.warning("没有找到任何产品")
            
    except Exception as e:
        logger.error(f"测试失败: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(test_producthunt_crawler()) 