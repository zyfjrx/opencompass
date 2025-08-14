import json
import random
import os
from typing import List, Dict

def count_lines(file_path: str) -> int:
    """
    统计文件行数
    
    Args:
        file_path (str): 文件路径
    
    Returns:
        int: 文件行数
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return sum(1 for _ in f)

def random_sample_jsonl(input_file: str, output_file: str, sample_size: int, seed: int = None) -> bool:
    """
    从JSONL文件中随机抽取指定数量的数据
    
    Args:
        input_file (str): 输入文件路径
        output_file (str): 输出文件路径
        sample_size (int): 抽取的样本数量
        seed (int, optional): 随机种子，用于结果复现
    
    Returns:
        bool: 是否成功
    """
    # 检查输入文件是否存在
    if not os.path.exists(input_file):
        print(f"错误：输入文件 {input_file} 不存在")
        return False
    
    # 设置随机种子（可选，用于结果复现）
    if seed is not None:
        random.seed(seed)
        print(f"使用随机种子: {seed}")
    
    try:
        # 统计总行数
        print("正在统计文件行数...")
        total_lines = count_lines(input_file)
        print(f"文件总行数: {total_lines}")
        
        # 检查抽取数量是否合理
        if sample_size > total_lines:
            print(f"警告：抽取数量 ({sample_size}) 大于文件总行数 ({total_lines})")
            print(f"将抽取所有 {total_lines} 行数据")
            sample_size = total_lines
        
        # 生成随机行号
        print(f"正在生成 {sample_size} 个随机行号...")
        selected_lines = sorted(random.sample(range(total_lines), sample_size))
        
        # 创建输出目录
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"创建输出目录: {output_dir}")
        
        # 读取并写入选中的行
        print("正在抽取数据...")
        selected_set = set(selected_lines)
        
        with open(input_file, 'r', encoding='utf-8') as infile, \
             open(output_file, 'w', encoding='utf-8') as outfile:
            
            for line_num, line in enumerate(infile):
                if line_num in selected_set:
                    line = line.strip()
                    if line:  # 跳过空行
                        # 验证JSON格式
                        try:
                            json.loads(line)
                            outfile.write(line + '\n')
                        except json.JSONDecodeError:
                            print(f"警告：第 {line_num + 1} 行JSON格式无效，已跳过")
        
        print(f"抽取完成！")
        print(f"输入文件: {input_file} ({total_lines} 行)")
        print(f"输出文件: {output_file} ({sample_size} 行)")
        return True
        
    except Exception as e:
        print(f"抽取过程中发生错误: {str(e)}")
        return False

def memory_efficient_sample(input_file: str, output_file: str, sample_size: int, seed: int = None) -> bool:
    """
    内存高效的随机抽取方法（适用于超大文件）
    使用蓄水池抽样算法
    
    Args:
        input_file (str): 输入文件路径
        output_file (str): 输出文件路径
        sample_size (int): 抽取的样本数量
        seed (int, optional): 随机种子
    
    Returns:
        bool: 是否成功
    """
    if not os.path.exists(input_file):
        print(f"错误：输入文件 {input_file} 不存在")
        return False
    
    if seed is not None:
        random.seed(seed)
        print(f"使用随机种子: {seed}")
    
    try:
        # 创建输出目录
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        print("使用蓄水池抽样算法进行内存高效抽取...")
        
        reservoir = []  # 蓄水池
        
        with open(input_file, 'r', encoding='utf-8') as infile:
            for i, line in enumerate(infile):
                line = line.strip()
                if not line:
                    continue
                
                # 验证JSON格式
                try:
                    json.loads(line)
                except json.JSONDecodeError:
                    print(f"警告：第 {i + 1} 行JSON格式无效，已跳过")
                    continue
                
                if len(reservoir) < sample_size:
                    # 蓄水池未满，直接添加
                    reservoir.append(line)
                else:
                    # 蓄水池已满，随机替换
                    j = random.randint(0, i)
                    if j < sample_size:
                        reservoir[j] = line
                
                # 显示进度
                if (i + 1) % 10000 == 0:
                    print(f"已处理 {i + 1} 行...")
        
        # 写入结果
        with open(output_file, 'w', encoding='utf-8') as outfile:
            for line in reservoir:
                outfile.write(line + '\n')
        
        print(f"抽取完成！")
        print(f"输入文件: {input_file}")
        print(f"输出文件: {output_file} ({len(reservoir)} 行)")
        return True
        
    except Exception as e:
        print(f"抽取过程中发生错误: {str(e)}")
        return False

def preview_sample(file_path: str, num_lines: int = 3) -> None:
    """
    预览抽取结果
    
    Args:
        file_path (str): 文件路径
        num_lines (int): 预览行数
    """
    if not os.path.exists(file_path):
        print(f"文件 {file_path} 不存在")
        return
    
    print(f"\n预览抽取结果前 {num_lines} 行：")
    print("-" * 50)
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i >= num_lines:
                break
            try:
                data = json.loads(line.strip())
                print(f"第{i+1}行:")
                for key, value in data.items():
                    if len(str(value)) > 100:
                        print(f"  {key}: {str(value)[:100]}...")
                    else:
                        print(f"  {key}: {value}")
                print()
            except json.JSONDecodeError:
                print(f"第{i+1}行: 无效的JSON格式")

if __name__ == "__main__":
    # 配置参数
    input_file = "/root/sft/opencompass/pet_data/pet_dataset.jsonl"
    output_file = "/root/sft/opencompass/pet_data/pet_dataset_100.jsonl"
    sample_size = 100
    random_seed = 42  # 设置为None则使用随机种子
    
    print("=" * 60)
    print("JSONL文件随机抽样工具")
    print("=" * 60)
    print(f"输入文件: {input_file}")
    print(f"输出文件: {output_file}")
    print(f"抽取数量: {sample_size}")
    print(f"随机种子: {random_seed}")
    print()
    
    # 检查文件是否存在
    if not os.path.exists(input_file):
        print(f"错误：输入文件不存在，请检查路径: {input_file}")
        exit(1)
    
    # 选择抽样方法
    print("选择抽样方法:")
    print("1. 标准方法（适用于中等大小文件，需要预先统计行数）")
    print("2. 内存高效方法（适用于超大文件，使用蓄水池抽样）")
    
    choice = input("请选择方法 (1/2，默认为1): ").strip()
    
    if choice == "2":
        print("\n使用内存高效方法...")
        success = memory_efficient_sample(input_file, output_file, sample_size, random_seed)
    else:
        print("\n使用标准方法...")
        success = random_sample_jsonl(input_file, output_file, sample_size, random_seed)
    
    if success:
        # 预览结果
        preview_sample(output_file)
        print("\n抽样完成！")
    else:
        print("\n抽样失败，请检查错误信息")