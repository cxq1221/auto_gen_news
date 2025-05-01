import pytest
import os
import sys
import yaml

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.crawler.github import GitHubCrawler

@pytest.fixture
def config():
    """加载测试配置"""
    config_path = os.path.join(project_root, 'config', 'config.yaml')
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

@pytest.mark.asyncio
async def test_github_crawler(config):
    """测试GitHub爬虫"""
    crawler = GitHubCrawler(config)
    products = await crawler.fetch()
    
    # 验证返回的数据
    assert isinstance(products, list)
    if products:  # 如果有数据
        product = products[0]
        assert isinstance(product, dict)
        assert 'name' in product
        assert 'url' in product
        assert 'description' in product
        assert 'release_date' in product
        assert 'stars' in product
        assert 'forks' in product
        assert 'language' in product
        assert 'languages' in product
        assert 'topics' in product
        assert 'readme' in product
        assert 'cover_image' in product
        assert 'content_images' in product

@pytest.mark.asyncio
async def test_github_crawler_error_handling(config):
    """测试GitHub爬虫错误处理"""
    # 使用无效的API token
    config['crawler']['targets']['github']['api_token'] = 'invalid_token'
    crawler = GitHubCrawler(config)
    
    with pytest.raises(Exception):
        await crawler.fetch() 