from typing import List, Dict, Any
import aiohttp
from datetime import datetime, timedelta
from loguru import logger
from .base import BaseCrawler

class ProductHuntCrawler(BaseCrawler):
    def __init__(self, config: Dict[str, Any], max_products: int = 1):
        super().__init__(config)
        self.ph_config = self.crawler_config['targets']['producthunt']
        self.api_key = self.ph_config['api_key']
        self.base_url = "https://api.firecrawl.dev/v1/scrape"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.max_products = max_products

    async def fetch(self) -> List[Dict[str, Any]]:
        """获取Product Hunt上的AI相关产品"""
        try:
            # 构建Firecrawl请求
            payload = {
                "url": "https://www.producthunt.com/topics/artificial-intelligence",
                "formats": ["json"],
                "jsonOptions": {
                    "mode": "llm",
                    "prompt": """Extract all AI products from the page in the following format:
                    {
                        "products": [
                            {
                                "name": "Product name",
                                "description": "Product description",
                                "url": "Product URL",
                                "votes": 123,
                                "comments_count": 45,
                                "cover_image": "Image URL"
                            }
                        ]
                    }"""
                },
                "waitFor": 5000
            }

            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.post(self.base_url, json=payload) as response:
                    if response.status != 200:
                        response_text = await response.text()
                        logger.error(f"Firecrawl API请求失败: 状态码 {response.status}, 响应: {response_text}")
                        raise Exception(f"Firecrawl API请求失败: {response.status}")
                    
                    data = await response.json()
                    products_data = data.get("data", {}).get("json", {}).get("products", [])
                    logger.info(f"找到 {len(products_data)} 个产品")
                    
                    # 处理产品，限制数量
                    products = []
                    for i, product_data in enumerate(products_data):
                        if i >= self.max_products:
                            break
                            
                        try:
                            product = await self._process_product(product_data)
                            if product:
                                products.append(product)
                                # 记录产品详细信息
                                logger.info(f"\n产品名称: {product['name']}")
                                logger.info(f"描述: {product['description']}")
                                logger.info(f"链接: {product['url']}")
                                logger.info(f"投票数: {product['votes']}")
                                logger.info(f"评论数: {product['comments_count']}")
                                logger.info(f"评论示例: {product['comments'][:1] if product['comments'] else '无评论'}")
                        except Exception as e:
                            logger.error(f"处理产品 {product_data.get('name', 'unknown')} 失败: {str(e)}")
                            continue
                    
                    return products
                    
        except Exception as e:
            logger.error(f"Product Hunt爬取失败: {str(e)}")
            raise

    async def _process_product(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理单个产品数据"""
        try:
            # 获取产品详情页
            if not product_data.get("url"):
                return None
                
            detail_url = product_data["url"]
            if not detail_url.startswith("http"):
                detail_url = f"https://www.producthunt.com{detail_url}"

            # 获取评论
            detail_payload = {
                "url": detail_url,
                "formats": ["json"],
                "jsonOptions": {
                    "mode": "llm",
                    "prompt": """Extract all comments from the page in the following format:
                    {
                        "comments": [
                            {
                                "content": "Comment text",
                                "created_at": "Creation time",
                                "votes": 123
                            }
                        ]
                    }"""
                },
                "waitFor": 5000
            }

            comments = []
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.post(self.base_url, json=detail_payload) as response:
                    if response.status == 200:
                        detail_data = await response.json()
                        comments = detail_data.get("data", {}).get("json", {}).get("comments", [])
                    else:
                        logger.error(f"获取产品详情失败: {detail_url}")

            # 构建产品信息
            product = {
                "name": product_data["name"],
                "url": detail_url,
                "description": product_data["description"],
                "release_date": datetime.now().isoformat(),  # Product Hunt不直接提供发布日期
                "votes": product_data.get("votes", 0),
                "comments_count": product_data.get("comments_count", 0),
                "topics": ["AI"],  # 由于是AI专题页面，默认为AI
                "comments": comments,
                "cover_image": product_data.get("cover_image", ""),
                "content_images": []  # Product Hunt不提供内容图片
            }
            
            logger.info(f"成功处理产品: {product_data['name']}")
            return product
            
        except Exception as e:
            logger.error(f"处理产品失败 {product_data.get('name', 'unknown')}: {str(e)}")
            return None 