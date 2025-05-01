from typing import List, Dict, Any
import aiohttp
from datetime import datetime, timedelta
import base64
from loguru import logger
from .base import BaseCrawler

class GitHubCrawler(BaseCrawler):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.github_config = self.crawler_config['targets']['github']
        self.api_token = self.github_config['api_token']
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {self.api_token}",
            "Accept": "application/vnd.github.v3+json"
        }

    async def fetch(self) -> List[Dict[str, Any]]:
        """获取GitHub上的AI相关项目"""
        try:
            # 获取最近7天内的项目
            since_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
            
            # 构建搜索查询
            query = f"topic:ai created:>{since_date} stars:>10"
            logger.info(f"搜索条件: {query}")
            
            # 调用GitHub API
            async with aiohttp.ClientSession(headers=self.headers) as session:
                # 搜索仓库
                search_url = f"{self.base_url}/search/repositories"
                params = {
                    "q": query,
                    "sort": "stars",
                    "order": "desc",
                    "per_page": 30
                }
                
                logger.info(f"请求URL: {search_url}")
                async with session.get(search_url, params=params) as response:
                    if response.status != 200:
                        response_text = await response.text()
                        logger.error(f"GitHub API请求失败: 状态码 {response.status}, 响应: {response_text}")
                        raise Exception(f"GitHub API请求失败: {response.status}")
                    
                    data = await response.json()
                    total_count = data.get("total_count", 0)
                    repositories = data.get("items", [])
                    logger.info(f"找到 {total_count} 个仓库，获取到 {len(repositories)} 个")
                    
                    # 处理每个仓库
                    products = []
                    for repo in repositories:
                        try:
                            product = await self._process_repository(repo, session)
                            if product:
                                products.append(product)
                        except Exception as e:
                            logger.error(f"处理仓库 {repo.get('full_name', 'unknown')} 失败: {str(e)}")
                            continue
                    
                    return products
                    
        except Exception as e:
            logger.error(f"GitHub爬取失败: {str(e)}")
            raise

    async def _process_repository(self, repo: Dict[str, Any], session: aiohttp.ClientSession) -> Dict[str, Any]:
        """处理单个仓库数据"""
        try:
            # 获取README内容
            readme_content = await self._get_readme_content(repo, session)
            
            # 获取仓库语言统计
            languages = await self._get_languages(repo, session)
            
            # 构建产品信息
            product = {
                "name": repo["name"],
                "url": repo["html_url"],
                "description": repo["description"] or "",
                "release_date": repo["created_at"],
                "stars": repo["stargazers_count"],
                "forks": repo["forks_count"],
                "language": repo["language"],
                "languages": languages,
                "topics": repo.get("topics", []),
                "readme": readme_content,
                "cover_image": repo.get("owner", {}).get("avatar_url", ""),
                "content_images": []  # 从README中提取的图片URL
            }
            
            # 从README中提取图片URL
            if readme_content:
                product["content_images"] = self._extract_images_from_markdown(readme_content)
            
            logger.info(f"成功处理仓库: {repo['full_name']}")
            return product
            
        except Exception as e:
            logger.error(f"处理仓库失败 {repo.get('full_name', 'unknown')}: {str(e)}")
            return None

    async def _get_readme_content(self, repo: Dict[str, Any], session: aiohttp.ClientSession) -> str:
        """获取仓库README内容"""
        try:
            readme_url = f"{self.base_url}/repos/{repo['full_name']}/readme"
            async with session.get(readme_url) as response:
                if response.status == 200:
                    data = await response.json()
                    content = data.get("content", "")
                    if content:
                        # Base64解码
                        return base64.b64decode(content).decode('utf-8')
                return ""
        except Exception as e:
            logger.error(f"获取README失败 {repo['full_name']}: {str(e)}")
            return ""

    async def _get_languages(self, repo: Dict[str, Any], session: aiohttp.ClientSession) -> Dict[str, int]:
        """获取仓库语言统计"""
        try:
            languages_url = f"{self.base_url}/repos/{repo['full_name']}/languages"
            async with session.get(languages_url) as response:
                if response.status == 200:
                    return await response.json()
                return {}
        except Exception as e:
            logger.error(f"获取语言统计失败 {repo['full_name']}: {str(e)}")
            return {}

    def _extract_images_from_markdown(self, markdown: str) -> List[str]:
        """从Markdown中提取图片URL"""
        import re
        # 匹配Markdown中的图片语法
        pattern = r'!\[.*?\]\((.*?)\)'
        return re.findall(pattern, markdown) 