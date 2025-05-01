import os
import yaml
from loguru import logger
from src.scheduler import Scheduler
from src.crawler import Crawler
from src.content import ContentGenerator
from src.image import ImageProcessor

class AutoGenNews:
    def __init__(self):
        self.config = self._load_config()
        self._setup_logger()
        self.scheduler = Scheduler(self.config)
        self.crawler = Crawler(self.config)
        self.content_generator = ContentGenerator(self.config)
        self.image_processor = ImageProcessor(self.config)

    def _load_config(self):
        """加载配置文件"""
        config_path = os.path.join('config', 'config.yaml')
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"配置文件不存在: {config_path}")
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def _setup_logger(self):
        """配置日志"""
        log_config = self.config['logging']
        logger.add(
            log_config['file'],
            rotation=f"{log_config['max_size']} MB",
            retention=log_config['backup_count'],
            level=log_config['level']
        )

    async def run(self):
        """运行主程序"""
        try:
            # 1. 爬取数据
            products = await self.crawler.fetch_all()
            
            # 2. 生成内容
            for product in products:
                # 生成产品介绍
                intro_content = await self.content_generator.generate_intro(product)
                
                # 生成使用说明
                guide_content = await self.content_generator.generate_guide(product)
                
                # 处理图片
                await self.image_processor.process_images(product)
                
                logger.info(f"成功处理产品: {product['name']}")
                
        except Exception as e:
            logger.error(f"程序运行出错: {str(e)}")
            raise

def main():
    """主函数"""
    app = AutoGenNews()
    
    # 启动调度器
    app.scheduler.start()
    
    # 保持程序运行
    try:
        while True:
            pass
    except KeyboardInterrupt:
        logger.info("程序已停止")

if __name__ == "__main__":
    main() 