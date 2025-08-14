from mmengine.config import read_base

with read_base():
    from .configs.datasets.mydataset import mydataset_datasets
    from .opencompass.configs.models.qwen3.lmdeploy_qwen3_14b import models  # 修正路径

datasets = mydataset_datasets

# 工作目录配置
work_dir = './outputs/mydataset_eval'

# 其他配置
summarizer = dict(
    dataset_abbrs=[
        ['mydataset', 'accuracy'],
        ['mydataset', 'avg_semantic_similarity'],
        ['mydataset', 'avg_overall_score'],
    ],
    summary_groups=[
        {
            'name': 'mydataset_accuracy',
            'subsets': [['mydataset', 'accuracy']],
        },
        {
            'name': 'mydataset_semantic',
            'subsets': [['mydataset', 'avg_semantic_similarity']],
        }
    ]
)