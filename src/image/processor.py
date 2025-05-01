from typing import Dict, Any, List
import os
from loguru import logger
from PIL import Image
import cv2
import numpy as np
from .utils import ImageUtils

class ImageProcessor:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.image_config = config['image']
        self.utils = ImageUtils()

    async def process_images(self, product: Dict[str, Any]) -> List[str]:
        """处理产品相关图片"""
        try:
            processed_images = []
            
            # 1. 处理封面图
            if 'cover_image' in product:
                cover_path = await self._process_cover(product['cover_image'])
                processed_images.append(cover_path)
            
            # 2. 处理内容图
            if 'content_images' in product:
                content_paths = await self._process_content_images(product['content_images'])
                processed_images.extend(content_paths)
            
            # 3. 添加水印
            if self.image_config['watermark']['enabled']:
                for image_path in processed_images:
                    await self._add_watermark(image_path)
            
            logger.info(f"成功处理产品图片: {product['name']}")
            return processed_images
            
        except Exception as e:
            logger.error(f"处理图片失败: {str(e)}")
            raise

    async def _process_cover(self, image_url: str) -> str:
        """处理封面图"""
        try:
            # 下载图片
            image_path = await self.utils.download_image(image_url)
            
            # 调整尺寸
            target_size = self.image_config['sizes']['cover']
            resized_path = await self.utils.resize_image(image_path, target_size)
            
            return resized_path
            
        except Exception as e:
            logger.error(f"处理封面图失败: {str(e)}")
            raise

    async def _process_content_images(self, image_urls: List[str]) -> List[str]:
        """处理内容图片"""
        try:
            processed_paths = []
            
            for url in image_urls:
                # 下载图片
                image_path = await self.utils.download_image(url)
                
                # 调整尺寸
                target_size = self.image_config['sizes']['content']
                resized_path = await self.utils.resize_image(image_path, target_size)
                
                processed_paths.append(resized_path)
            
            return processed_paths
            
        except Exception as e:
            logger.error(f"处理内容图片失败: {str(e)}")
            raise

    async def _add_watermark(self, image_path: str) -> None:
        """添加水印"""
        try:
            # 读取图片
            img = cv2.imread(image_path)
            
            # 添加水印文字
            text = self.image_config['watermark']['text']
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 1
            thickness = 2
            
            # 计算文字位置
            (text_width, text_height), _ = cv2.getTextSize(text, font, font_scale, thickness)
            x = img.shape[1] - text_width - 10
            y = img.shape[0] - 10
            
            # 绘制水印
            cv2.putText(img, text, (x, y), font, font_scale, (255, 255, 255), thickness)
            
            # 保存图片
            cv2.imwrite(image_path, img)
            
        except Exception as e:
            logger.error(f"添加水印失败: {str(e)}")
            raise 