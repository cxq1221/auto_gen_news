from abc import ABC, abstractmethod
from typing import List, Dict, Any
from loguru import logger

class BaseCrawler(ABC):
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.crawler_config = config['crawler']

    @abstractmethod
    async def fetch(self) -> List[Dict[str, Any]]:
        """获取数据"""
        pass

    def _validate_product(self, product: Dict[str, Any]) -> bool:
        """验证产品数据完整性"""
        required_fields = ['name', 'url', 'description', 'release_date']
        return all(field in product for field in required_fields)

    def _deduplicate(self, products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """去重"""
        seen = set()
        unique_products = []
        
        for product in products:
            # 使用名称和URL生成唯一标识
            product_id = f"{product['name']}_{product['url']}"
            if product_id not in seen:
                seen.add(product_id)
                unique_products.append(product)
        
        return unique_products

    async def fetch_all(self) -> List[Dict[str, Any]]:
        """获取所有数据并进行处理"""
        try:
            products = await self.fetch()
            
            # 验证数据
            valid_products = [p for p in products if self._validate_product(p)]
            
            # 去重
            unique_products = self._deduplicate(valid_products)
            
            logger.info(f"成功获取 {len(unique_products)} 个产品信息")
            return unique_products
            
        except Exception as e:
            logger.error(f"爬取数据失败: {str(e)}")
            raise 