from typing import List, Dict, Any
from loguru import logger
from .base import BaseCrawler
from .github import GitHubCrawler
from .producthunt import ProductHuntCrawler

class Crawler:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.crawlers = self._init_crawlers()

    def _init_crawlers(self) -> List[BaseCrawler]:
        """初始化所有爬虫"""
        crawlers = []
        targets = self.config['crawler']['targets']
        
        if targets['github']['enabled']:
            crawlers.append(GitHubCrawler(self.config))
        if targets['producthunt']['enabled']:
            crawlers.append(ProductHuntCrawler(self.config))
        # TODO: 添加其他爬虫
        # if targets['futurepedia']['enabled']:
        #     crawlers.append(FuturepediaCrawler(self.config))
        # if targets['kr36']['enabled']:
        #     crawlers.append(Kr36Crawler(self.config))
            
        return crawlers

    async def fetch_all(self) -> List[Dict[str, Any]]:
        """从所有启用的爬虫获取数据"""
        all_products = []
        
        for crawler in self.crawlers:
            try:
                products = await crawler.fetch_all()
                all_products.extend(products)
            except Exception as e:
                logger.error(f"爬虫 {crawler.__class__.__name__} 执行失败: {str(e)}")
                continue
        
        return all_products

__all__ = [
    'Crawler',
    'BaseCrawler',
    'GitHubCrawler',
    'ProductHuntCrawler'
] 