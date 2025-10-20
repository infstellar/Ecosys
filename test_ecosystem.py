#!/usr/bin/env python3
"""
生态系统模拟器测试文件
Test file for the Ecosystem Simulator
"""

import sys
import os
import unittest
from unittest.mock import Mock, patch

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import backend modules
from backend.models.ecosystem import EcosystemConfig, EcosystemState
from backend.interface.api import EcosystemAPI, Command, CommandType

# Import frontend modules
from frontend.ui.control_panel import ConfigManager


class TestEcosystemBackend(unittest.TestCase):
    """测试后端生态系统功能"""
    
    def setUp(self):
        """设置测试环境"""
        self.config = EcosystemConfig(
            world_width=100,
            world_height=100,
            initial_grass_count=50,
            initial_cow_count=10,
            initial_tiger_count=2,
            max_grass_count=200,
            max_cow_count=50,
            max_tiger_count=10
        )
        self.ecosystem = EcosystemState(self.config)
        self.api = EcosystemAPI()
    
    def test_ecosystem_config_creation(self):
        """测试生态系统配置创建"""
        self.assertEqual(self.config.world_width, 100)
        self.assertEqual(self.config.world_height, 100)
        self.assertEqual(self.config.initial_grass_count, 50)
        self.assertEqual(self.config.initial_cow_count, 10)
        self.assertEqual(self.config.initial_tiger_count, 2)
    
    def test_ecosystem_initialization(self):
        """测试生态系统初始化"""
        self.assertIsNotNone(self.ecosystem.grass_list)
        self.assertIsNotNone(self.ecosystem.cow_list)
        self.assertIsNotNone(self.ecosystem.tiger_list)
        self.assertEqual(self.ecosystem.config.world_width, 100)
        self.assertEqual(self.ecosystem.config.world_height, 100)
    
    def test_api_commands(self):
        """测试API命令"""
        # 测试重置命令
        reset_command = Command(CommandType.RESET_SIMULATION, {"config": self.config})
        result = self.api.execute_command(reset_command)
        self.assertTrue(result.success)
        
        # 测试开始命令
        start_command = Command(CommandType.START_SIMULATION, {})
        result = self.api.execute_command(start_command)
        self.assertTrue(result.success)
        
        # 测试暂停命令
        pause_command = Command(CommandType.PAUSE_SIMULATION, {})
        result = self.api.execute_command(pause_command)
        self.assertTrue(result.success)
    
    def test_simulation_step(self):
        """测试模拟步进"""
        # 重置模拟
        reset_command = Command(CommandType.RESET_SIMULATION, {"config": self.config})
        self.api.execute_command(reset_command)
        
        # 执行一步模拟
        step_command = Command(CommandType.STEP_SIMULATION, {})
        result = self.api.execute_command(step_command)
        self.assertTrue(result.success)
    
    def test_get_data(self):
        """测试获取数据"""
        # 重置模拟
        reset_command = Command(CommandType.RESET_SIMULATION, {"config": self.config})
        self.api.execute_command(reset_command)
        
        # 获取数据
        get_data_command = Command(CommandType.GET_DATA, {})
        result = self.api.execute_command(get_data_command)
        self.assertTrue(result.success)
        self.assertIn("species_data", result.data)
        self.assertIn("world_data", result.data)


class TestFrontendComponents(unittest.TestCase):
    """测试前端组件"""
    
    def setUp(self):
        """设置测试环境"""
        self.config_manager = ConfigManager()
    
    @patch('pygame.init')
    @patch('pygame.display.set_mode')
    def test_config_manager(self, mock_display, mock_init):
        """测试配置管理器"""
        config = self.config_manager.get_config()
        self.assertIsInstance(config, dict)
        self.assertIn("world_width", config)
        self.assertIn("world_height", config)
        self.assertIn("initial_grass", config)
        self.assertIn("initial_cows", config)
        self.assertIn("initial_tigers", config)
    
    @patch('pygame.init')
    @patch('pygame.display.set_mode')
    def test_config_update(self, mock_display, mock_init):
        """测试配置更新"""
        new_config = {
            "world_width": 150,
            "world_height": 150,
            "initial_grass": 75
        }
        self.config_manager.update_config(new_config)
        updated_config = self.config_manager.get_config()
        self.assertEqual(updated_config["world_width"], 150)
        self.assertEqual(updated_config["world_height"], 150)
        self.assertEqual(updated_config["initial_grass"], 75)


def run_tests():
    """运行所有测试"""
    print("🧪 运行生态系统模拟器测试...")
    print("🧪 Running Ecosystem Simulator Tests...")
    print("=" * 60)
    
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加测试类
    suite.addTests(loader.loadTestsFromTestCase(TestEcosystemBackend))
    suite.addTests(loader.loadTestsFromTestCase(TestFrontendComponents))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 输出结果
    print("\n" + "=" * 60)
    if result.wasSuccessful():
        print("✅ 所有测试通过！All tests passed!")
        print(f"✅ 运行了 {result.testsRun} 个测试")
        return True
    else:
        print("❌ 测试失败！Some tests failed!")
        print(f"❌ 失败: {len(result.failures)}, 错误: {len(result.errors)}")
        return False


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)