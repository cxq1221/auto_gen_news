import os
import sys
import pytest

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

@pytest.fixture(autouse=True)
def setup_test_env():
    """设置测试环境"""
    # 确保测试目录存在
    os.makedirs(os.path.join(project_root, 'tests', 'data'), exist_ok=True)
    os.makedirs(os.path.join(project_root, 'tests', 'output'), exist_ok=True)
    
    yield
    
    # 清理测试数据
    # TODO: 如果需要，在这里添加清理代码 