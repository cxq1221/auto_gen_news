from typing import Dict, Any
import asyncio
from datetime import datetime
from loguru import logger
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from .email import EmailNotifier

class Scheduler:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.scheduler_config = config['scheduler']
        self.scheduler = AsyncIOScheduler()
        self.email_notifier = EmailNotifier(config)
        self.retry_count = 0

    def start(self):
        """启动调度器"""
        try:
            # 设置定时任务
            run_time = self.scheduler_config['run_time']
            hour, minute = map(int, run_time.split(':'))
            
            self.scheduler.add_job(
                self._run_task,
                CronTrigger(hour=hour, minute=minute),
                id='daily_task',
                name='每日AI产品资讯生成任务'
            )
            
            self.scheduler.start()
            logger.info("调度器已启动")
            
        except Exception as e:
            logger.error(f"启动调度器失败: {str(e)}")
            raise

    async def _run_task(self):
        """执行任务"""
        try:
            from main import AutoGenNews
            app = AutoGenNews()
            await app.run()
            
            # 重置重试计数
            self.retry_count = 0
            
        except Exception as e:
            logger.error(f"执行任务失败: {str(e)}")
            await self._handle_failure()

    async def _handle_failure(self):
        """处理任务失败"""
        self.retry_count += 1
        max_attempts = self.scheduler_config['retry']['max_attempts']
        
        if self.retry_count <= max_attempts:
            # 等待一段时间后重试
            retry_interval = self.scheduler_config['retry']['interval']
            logger.info(f"任务失败，{retry_interval}秒后进行第{self.retry_count}次重试")
            await asyncio.sleep(retry_interval)
            await self._run_task()
        else:
            # 发送失败通知
            await self._send_failure_notification()

    async def _send_failure_notification(self):
        """发送失败通知"""
        try:
            subject = "AI产品资讯生成任务失败通知"
            content = f"""
            任务执行失败，已重试{self.retry_count}次。
            失败时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            请检查系统日志了解详细信息。
            """
            
            await self.email_notifier.send_email(subject, content)
            logger.info("已发送失败通知邮件")
            
        except Exception as e:
            logger.error(f"发送失败通知失败: {str(e)}")

    def stop(self):
        """停止调度器"""
        self.scheduler.shutdown()
        logger.info("调度器已停止") 