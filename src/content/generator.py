from typing import Dict, Any
from loguru import logger
from openai import AsyncOpenAI
from .templates import ProductIntroTemplate, UsageGuideTemplate

class ContentGenerator:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.content_config = config['content']
        self.client = AsyncOpenAI(
            api_key=self.content_config['openai']['api_key']
        )

    async def generate_intro(self, product: Dict[str, Any]) -> str:
        """生成产品介绍文章"""
        try:
            template = ProductIntroTemplate(product)
            prompt = template.generate_prompt()
            
            response = await self.client.chat.completions.create(
                model=self.content_config['openai']['model'],
                messages=[
                    {"role": "system", "content": "你是一个专业的技术产品分析师，擅长撰写产品介绍文章。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.content_config['openai']['temperature']
            )
            
            content = response.choices[0].message.content
            logger.info(f"成功生成产品介绍: {product['name']}")
            return content
            
        except Exception as e:
            logger.error(f"生成产品介绍失败: {str(e)}")
            raise

    async def generate_guide(self, product: Dict[str, Any]) -> str:
        """生成使用说明文档"""
        try:
            template = UsageGuideTemplate(product)
            prompt = template.generate_prompt()
            
            response = await self.client.chat.completions.create(
                model=self.content_config['openai']['model'],
                messages=[
                    {"role": "system", "content": "你是一个专业的技术文档撰写者，擅长编写使用说明文档。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.content_config['openai']['temperature']
            )
            
            content = response.choices[0].message.content
            logger.info(f"成功生成使用说明: {product['name']}")
            return content
            
        except Exception as e:
            logger.error(f"生成使用说明失败: {str(e)}")
            raise 