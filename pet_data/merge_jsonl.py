import json
import os

def merge_jsonl_files(file1_path, file2_path, output_path):
    """
    合并两个JSONL文件
    
    Args:
        file1_path (str): 第一个JSONL文件路径
        file2_path (str): 第二个JSONL文件路径
        output_path (str): 输出文件路径
    """
    # 检查输入文件是否存在
    if not os.path.exists(file1_path):
        print(f"错误：文件 {file1_path} 不存在")
        return False
    
    if not os.path.exists(file2_path):
        print(f"错误：文件 {file2_path} 不存在")
        return False
    
    try:
        with open(output_path, 'w', encoding='utf-8') as output_file:
            # 读取并写入第一个文件的内容
            print(f"正在读取第一个文件: {file1_path}")
            with open(file1_path, 'r', encoding='utf-8') as f1:
                line_count1 = 0
                for line in f1:
                    line = line.strip()
                    if line:  # 跳过空行
                        # 验证JSON格式
                        try:
                            json.loads(line)
                            output_file.write(line + '\n')
                            line_count1 += 1
                        except json.JSONDecodeError:
                            print(f"警告：第一个文件中发现无效的JSON行，已跳过")
            
            # 读取并写入第二个文件的内容
            print(f"正在读取第二个文件: {file2_path}")
            with open(file2_path, 'r', encoding='utf-8') as f2:
                line_count2 = 0
                for line in f2:
                    line = line.strip()
                    if line:  # 跳过空行
                        # 验证JSON格式
                        try:
                            json.loads(line)
                            output_file.write(line + '\n')
                            line_count2 += 1
                        except json.JSONDecodeError:
                            print(f"警告：第二个文件中发现无效的JSON行，已跳过")
        
        print(f"合并完成！")
        print(f"第一个文件: {line_count1} 行")
        print(f"第二个文件: {line_count2} 行")
        print(f"总计: {line_count1 + line_count2} 行")
        print(f"输出文件: {output_path}")
        return True
        
    except Exception as e:
        print(f"合并过程中发生错误: {str(e)}")
        return False

def preview_merged_file(file_path, num_lines=3):
    """
    预览合并后的文件内容
    
    Args:
        file_path (str): 文件路径
        num_lines (int): 预览行数
    """
    if not os.path.exists(file_path):
        print(f"文件 {file_path} 不存在")
        return
    
    print(f"\n预览合并后的文件前 {num_lines} 行：")
    print("-" * 50)
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i >= num_lines:
                break
            try:
                data = json.loads(line.strip())
                print(f"第{i+1}行:")
                for key, value in data.items():
                    # 限制显示长度
                    if len(str(value)) > 100:
                        print(f"  {key}: {str(value)[:100]}...")
                    else:
                        print(f"  {key}: {value}")
                print()
            except json.JSONDecodeError:
                print(f"第{i+1}行: 无效的JSON格式")

if __name__ == "__main__":
    # 设置文件路径
    file1 = "/root/sft/opencompass/pet_data/pet_dataset_en.jsonl"
    file2 = "/root/sft/opencompass/pet_data/pet_dataset_zh.jsonl"
    
    # 如果用户没有输入，提供一个示例路径
    if not file2:
        print("未输入第二个文件路径，请手动设置 file2 变量")
        # file2 = "/path/to/second/file.jsonl"  # 请修改为实际路径
        exit(1)
    
    # 生成输出文件名
    output_file = "/root/sft/opencompass/pet_data/pet_dataset.jsonl"
    
    print(f"准备合并以下文件:")
    print(f"文件1: {file1}")
    print(f"文件2: {file2}")
    print(f"输出: {output_file}")
    print()
    
    # 执行合并
    success = merge_jsonl_files(file1, file2, output_file)
    
    if success:
        # 预览合并结果
        preview_merged_file(output_file)
    else:
        print("合并失败，请检查文件路径和格式")