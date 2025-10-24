"""
性能测试脚本：比较优化前后的草密度计算性能
"""
import time
import numpy as np
from backend.models.species import Grass, Position
from backend.models.ecosystem import EcosystemState

def create_test_grass_list(num_grass=1000):
    """创建测试用的草列表"""
    grass_list = []
    for i in range(num_grass):
        x = np.random.uniform(0, 800)
        y = np.random.uniform(0, 600)
        grass = Grass(Position(x, y))
        grass_list.append(grass)
    return grass_list

def test_original_method(grass_list, test_grass):
    """测试原始方法的性能"""
    # 模拟原始的ecosystem_state（不包含预计算数组）
    ecosystem_state = {
        'grass_list': grass_list,
        'cow_list': [],
        'tiger_list': []
    }
    
    start_time = time.time()
    for _ in range(100):  # 重复100次测试
        density = test_grass.calculate_nearby_grass_density(ecosystem_state)
    end_time = time.time()
    
    return end_time - start_time, density

def test_optimized_method(grass_list, test_grass):
    """测试优化后方法的性能"""
    # 创建包含预计算数组的ecosystem_state
    alive_grass = [g for g in grass_list if g.alive]
    grass_positions = np.array([[g.position.x, g.position.y] for g in alive_grass])
    
    ecosystem_state = {
        'grass_list': grass_list,
        'cow_list': [],
        'tiger_list': [],
        'grass_positions_array': grass_positions,
        'alive_grass_objects': alive_grass
    }
    
    start_time = time.time()
    for _ in range(100):  # 重复100次测试
        density = test_grass.calculate_nearby_grass_density(ecosystem_state)
    end_time = time.time()
    
    return end_time - start_time, density

def main():
    print("🧪 开始性能测试...")
    
    # 创建不同规模的测试数据
    test_sizes = [100, 500, 1000, 2000]
    
    for size in test_sizes:
        print(f"\n📊 测试草数量: {size}")
        
        # 创建测试数据
        grass_list = create_test_grass_list(size)
        test_grass = grass_list[0]  # 使用第一个草作为测试对象
        
        # 测试原始方法
        original_time, original_density = test_original_method(grass_list, test_grass)
        print(f"   原始方法: {original_time:.4f}秒, 密度: {original_density:.4f}")
        
        # 测试优化方法
        optimized_time, optimized_density = test_optimized_method(grass_list, test_grass)
        print(f"   优化方法: {optimized_time:.4f}秒, 密度: {optimized_density:.4f}")
        
        # 计算性能提升
        if original_time > 0:
            speedup = original_time / optimized_time
            print(f"   🚀 性能提升: {speedup:.2f}x")
        
        # 验证结果一致性
        density_diff = abs(original_density - optimized_density)
        if density_diff < 1e-10:
            print(f"   ✅ 结果一致性: 通过")
        else:
            print(f"   ❌ 结果一致性: 失败 (差异: {density_diff})")

if __name__ == "__main__":
    main()