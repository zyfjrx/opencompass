import json

def convert_json_to_jsonl(input_file, output_file):
    """
    将JSON格式的数据转换为JSONL格式
    instruction字段映射为question，output字段映射为answer
    """
    # 读取原始JSON文件
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 转换并写入JSONL文件
    with open(output_file, 'w', encoding='utf-8') as f:
        for item in data:
            # 创建新的数据结构
            new_item = {
                "question": item.get("instruction", ""),
                "answer": item.get("output", "")
            }
            # 写入JSONL格式（每行一个JSON对象）
            f.write(json.dumps(new_item, ensure_ascii=False) + '\n')
    
    print(f"转换完成！已将 {input_file} 转换为 {output_file}")
    print(f"共处理了 {len(data)} 条记录")

if __name__ == "__main__":
    # 设置输入和输出文件路径
    input_file = "/root/sft/opencompass/pet_data/distill/distill-pet-health-medical.json"
    output_file = "/root/sft/opencompass/pet_data/outdata/distill-pet-health-medical.jsonl"
    
    # 执行转换
    convert_json_to_jsonl(input_file, output_file)
    
    # 验证转换结果
    print("\n转换后的前两行内容预览：")
    with open(output_file, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i < 2:  # 只显示前两行
                data = json.loads(line)
                print(f"第{i+1}行: question前50字符: {data['question'][:50]}...")
                print(f"第{i+1}行: answer前50字符: {data['answer'][:50]}...")
                print()