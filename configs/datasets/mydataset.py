from opencompass.datasets import MyDataset, MyDatasetEvaluator, mydataset_postprocess

# 评估配置
mydataset_eval_cfg = dict(
    evaluator=dict(
        type=MyDatasetEvaluator,
        similarity_threshold=0.7,  # 可调整相似度阈值
        # use_fuzzy_match=True
    ),
    pred_postprocessor=dict(type=mydataset_postprocess)
)

# 数据集配置
mydataset_datasets = [
    dict(
        type=MyDataset,
        path='/root/sft/opencompass/pet_data/outdata',  # 数据集路径
        name='mydataset',
        abbr='mydataset',
        reader_cfg=dict(
            input_columns=['question'],
            output_column='answer',
            train_split='train',
            test_split='test'
        ),
        infer_cfg=dict(
            prompt_template=dict(
                type='PromptTemplate',
                template=dict(
                    round=[
                        dict(
                            role='HUMAN',
                            prompt='请回答以下问题：{question}'
                        )
                    ]
                )
            ),
            retriever=dict(type='ZeroRetriever'),
            inferencer=dict(type='GenInferencer', max_out_len=512)
        ),
        eval_cfg=mydataset_eval_cfg
    )
]