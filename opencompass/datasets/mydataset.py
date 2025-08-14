# flake8: noqa
# yapf: disable

import json
import re
from os import environ
from datasets import Dataset
import numpy as np
from typing import List, Dict, Any

from opencompass.openicl import BaseEvaluator
from opencompass.registry import LOAD_DATASET
from opencompass.utils import get_data_path

from .base import BaseDataset


def _parse(item):
    """解析数据项，保持原有的question和answer字段"""
    if 'question' not in item or 'answer' not in item:
        raise ValueError("数据项必须包含'question'和'answer'字段")
    
    item['question'] = item['question'].strip()
    item['answer'] = item['answer'].strip()
    
    return item


def mydataset_postprocess(text: str) -> str:
    """后处理函数，从复杂回答中提取核心答案"""
    if not isinstance(text, str):
        text = str(text)
    
    # 移除<think>标签内容
    import re
    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    
    # 提取**加粗**的内容（通常是核心答案）
    bold_matches = re.findall(r'\*\*(.*?)\*\*', text)
    if bold_matches:
        # 取第一个加粗内容作为答案
        answer = bold_matches[0].strip()
        return answer
    
    # 如果没有加粗，取第一行非空内容
    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        if line and not line.startswith('>'):
            return line
    
    return text.strip()


@LOAD_DATASET.register_module()
class MyDataset(BaseDataset):
    """自定义数据集加载器，支持加载目录下所有JSONL文件"""

    @staticmethod
    def load(path: str, **kwargs):
        """加载目录下所有JSONL格式的数据集文件
        
        Args:
            path: 数据集目录路径或单个文件路径
            **kwargs: 其他参数
            
        Returns:
            Dataset: 处理后的数据集
        """
        import os
        import glob
        
        path = get_data_path(path)
        
        # 判断是文件还是目录
        if os.path.isfile(path):
            # 单个文件
            file_paths = [path]
        elif os.path.isdir(path):
            # 目录，查找所有.jsonl文件
            file_paths = glob.glob(os.path.join(path, "*.jsonl"))
            if not file_paths:
                raise ValueError(f"目录 {path} 中没有找到.jsonl文件")
        else:
            raise FileNotFoundError(f"路径不存在: {path}")
        
        # 读取所有文件的数据
        all_data = []
        for file_path in file_paths:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line:  # 跳过空行
                            item = json.loads(line)
                            all_data.append(item)
            except FileNotFoundError:
                raise FileNotFoundError(f"数据集文件未找到: {file_path}")
            except json.JSONDecodeError as e:
                raise ValueError(f"JSON解析错误 {file_path}: {e}")
        
        if not all_data:
            raise ValueError("所有数据文件都为空")
        
        # 创建Dataset对象
        dataset = Dataset.from_list(all_data)
        
        # 应用数据解析函数
        dataset = dataset.map(_parse)
        
        return dataset


class MyDatasetSemanticEvaluator(BaseEvaluator):
    """基于语义理解的评估器"""

    def __init__(self, similarity_threshold=0.75, use_embedding=True, model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
        """
        Args:
            similarity_threshold: 语义相似度阈值
            use_embedding: 是否使用词向量模型
            model_name: 预训练模型名称
        """
        self.similarity_threshold = similarity_threshold
        self.use_embedding = use_embedding
        self.model_name = model_name
        
        if use_embedding:
            try:
                from sentence_transformers import SentenceTransformer
                self.model = SentenceTransformer(model_name)
                print(f"已加载语义模型: {model_name}")
            except ImportError:
                print("警告: sentence-transformers未安装，回退到传统匹配")
                self.use_embedding = False
                self.model = None
            except Exception as e:
                print(f"警告: 模型加载失败 {e}，回退到传统匹配")
                self.use_embedding = False
                self.model = None

    def extract_core_meaning(self, text: str) -> str:
        """提取文本的核心含义"""
        if not isinstance(text, str):
            text = str(text)
        
        # 移除无关信息
        text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # 移除加粗标记但保留内容
        
        # 移除常见的填充词和语气词
        filler_words = [
            '嗯', '啊', '呃', '那个', '这个', '就是说', '我觉得', '我认为', 
            '可能', '应该', '大概', '基本上', '一般来说', '通常',
            'um', 'uh', 'well', 'you know', 'i think', 'i believe'
        ]
        
        for word in filler_words:
            text = re.sub(rf'\b{re.escape(word)}\b', '', text, flags=re.IGNORECASE)
        
        # 清理多余空格
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text

    def semantic_similarity(self, text1: str, text2: str) -> float:
        """计算两个文本的语义相似度"""
        if not self.use_embedding or self.model is None:
            return self.fallback_similarity(text1, text2)
        
        try:
            # 提取核心含义
            core1 = self.extract_core_meaning(text1)
            core2 = self.extract_core_meaning(text2)
            
            if not core1 or not core2:
                return 0.0
            
            # 计算语义向量
            embeddings = self.model.encode([core1, core2])
            
            # 计算余弦相似度
            from sklearn.metrics.pairwise import cosine_similarity
            similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
            
            return float(similarity)
            
        except Exception as e:
            print(f"语义相似度计算失败: {e}，使用备用方法")
            return self.fallback_similarity(text1, text2)

    def fallback_similarity(self, text1: str, text2: str) -> float:
        """备用相似度计算方法（改进的传统方法）"""
        # 提取核心含义
        core1 = self.extract_core_meaning(text1).lower()
        core2 = self.extract_core_meaning(text2).lower()
        
        if core1 == core2:
            return 1.0
        
        # 使用更智能的词汇匹配
        words1 = set(re.findall(r'\b\w+\b', core1))
        words2 = set(re.findall(r'\b\w+\b', core2))
        
        if not words1 or not words2:
            return 0.0
        
        # 计算词汇重叠度
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        jaccard = len(intersection) / len(union) if union else 0.0
        
        # 检查关键概念包含关系
        if words1.issubset(words2) or words2.issubset(words1):
            jaccard = max(jaccard, 0.8)
        
        # 检查部分匹配（适用于中文）
        if any(w1 in core2 or w2 in core1 for w1 in words1 for w2 in words2):
            jaccard = max(jaccard, 0.6)
        
        return jaccard

    def evaluate_answer_quality(self, prediction: str, reference: str) -> Dict[str, Any]:
        """评估答案质量的多维度分析"""
        # 语义相似度
        semantic_score = self.semantic_similarity(prediction, reference)
        
        # 完整性评估（答案是否完整回答了问题）
        pred_core = self.extract_core_meaning(prediction)
        ref_core = self.extract_core_meaning(reference)
        
        completeness = min(len(pred_core) / max(len(ref_core), 1), 1.0) if ref_core else 0.0
        
        # 准确性评估
        accuracy = semantic_score
        
        # 综合评分
        overall_score = (semantic_score * 0.7 + completeness * 0.3)
        
        return {
            'semantic_similarity': round(semantic_score, 3),
            'completeness': round(completeness, 3),
            'accuracy': round(accuracy, 3),
            'overall_score': round(overall_score, 3),
            'is_correct': overall_score >= self.similarity_threshold
        }

    def score(self, predictions: List[str], references: List[str]) -> Dict[str, Any]:
        """计算评估分数"""
        if len(predictions) != len(references):
            return {
                'error': 'predictions and references have different length'
            }
        
        correct = 0
        total = len(predictions)
        details = []
        semantic_scores = []
        overall_scores = []
        
        for pred, ref in zip(predictions, references):
            # 多维度评估
            evaluation = self.evaluate_answer_quality(pred, ref)
            
            semantic_scores.append(evaluation['semantic_similarity'])
            overall_scores.append(evaluation['overall_score'])
            
            if evaluation['is_correct']:
                correct += 1
            
            detail = {
                'prediction': pred,
                'reference': ref,
                'semantic_similarity': evaluation['semantic_similarity'],
                'completeness': evaluation['completeness'],
                'overall_score': evaluation['overall_score'],
                'is_correct': evaluation['is_correct'],
                'threshold': self.similarity_threshold
            }
            details.append(detail)
        
        # 计算统计指标
        accuracy = 100 * correct / total if total > 0 else 0
        avg_semantic_similarity = sum(semantic_scores) / len(semantic_scores) if semantic_scores else 0
        avg_overall_score = sum(overall_scores) / len(overall_scores) if overall_scores else 0
        
        result = {
            'accuracy': round(accuracy, 2),
            'avg_semantic_similarity': round(avg_semantic_similarity, 3),
            'avg_overall_score': round(avg_overall_score, 3),
            'total': total,
            'correct': correct,
            'threshold': self.similarity_threshold,
            'evaluation_method': 'semantic_based',
            'model_used': self.model_name if self.use_embedding else 'fallback',
            'details': details
        }
        
        return result


# 保持原有的MyDatasetEvaluator作为备用
class MyDatasetEvaluator(MyDatasetSemanticEvaluator):
    """默认评估器，使用语义评估"""
    pass