from mmengine.config import read_base

with read_base():
    from opencompass.configs.datasets.subjective.alignbench.alignbench_judgeby_critiquellm import alignbench_datasets
    from opencompass.configs.datasets.subjective.alpaca_eval.alpacav2_judgeby_gpt4 import alpacav2_datasets
    from opencompass.configs.datasets.subjective.compassarena.compassarena_compare import compassarena_datasets
    from opencompass.configs.datasets.subjective.arena_hard.arena_hard_compare import arenahard_datasets
    from opencompass.configs.datasets.subjective.compassbench.compassbench_compare import compassbench_datasets
    from opencompass.configs.datasets.subjective.fofo.fofo_judge import fofo_datasets
    from opencompass.configs.datasets.subjective.wildbench.wildbench_pair_judge import wildbench_datasets
    from opencompass.configs.datasets.subjective.multiround.mtbench_single_judge_diff_temp import mtbench_datasets
    from opencompass.configs.datasets.subjective.multiround.mtbench101_judge import mtbench101_datasets

from opencompass.models import (HuggingFace, HuggingFaceCausalLM,
                                HuggingFaceChatGLM3, OpenAI)
from opencompass.partitioners import NaivePartitioner, SizePartitioner
from opencompass.partitioners.sub_naive import SubjectiveNaivePartitioner
from opencompass.partitioners.sub_num_worker import \
    SubjectiveNumWorkerPartitioner
from opencompass.partitioners.sub_size import SubjectiveSizePartitioner
from opencompass.runners import LocalRunner, SlurmSequentialRunner
from opencompass.summarizers import SubjectiveSummarizer
from opencompass.tasks import OpenICLInferTask
from opencompass.tasks.subjective_eval import SubjectiveEvalTask

api_meta_template = dict(round=[
    dict(role='HUMAN', api_role='HUMAN'),
    dict(role='BOT', api_role='BOT', generate=True),
])

# -------------Inference Stage ----------------------------------------
# For subjective evaluation, we often set do sample for models
models = [
    dict(
        type=HuggingFaceChatGLM3,
        abbr='chatglm3-6b-hf',
        path='THUDM/chatglm3-6b',
        tokenizer_path='THUDM/chatglm3-6b',
        model_kwargs=dict(
            device_map='auto',
            trust_remote_code=True,
        ),
        tokenizer_kwargs=dict(
            padding_side='left',
            truncation_side='left',
            trust_remote_code=True,
        ),
        generation_kwargs=dict(
            do_sample=
            True,  #For subjective evaluation, we suggest you do set do_sample when running model inference!
        ),
        meta_template=api_meta_template,
        max_out_len=2048,
        max_seq_len=4096,
        batch_size=8,
        run_cfg=dict(num_gpus=1, num_procs=1),
    )
]

datasets = [
    *alignbench_datasets, *alpacav2_datasets, *arenahard_datasets,
    *compassarena_datasets, *compassbench_datasets, *fofo_datasets,
    *mtbench_datasets, *mtbench101_datasets, *wildbench_datasets
]  # add datasets you want

infer = dict(
    partitioner=dict(type=NaivePartitioner),
    runner=dict(type=LocalRunner,
                max_num_workers=16,
                task=dict(type=OpenICLInferTask)),
)
# -------------Evalation Stage ----------------------------------------

## ------------- JudgeLLM Configuration
judge_models = [
    dict(
        abbr='GPT4-Turbo',
        type=OpenAI,
        path='gpt-4-1106-preview',
        key=
        'xxxx',  # The key will be obtained from $OPENAI_API_KEY, but you can write down your key here as well
        meta_template=api_meta_template,
        query_per_second=16,
        max_out_len=2048,
        max_seq_len=2048,
        batch_size=8,
        temperature=0,
    )
]

## ------------- Evaluation Configuration
eval = dict(
    partitioner=dict(
        type=SubjectiveNaivePartitioner,
        models=models,
        judge_models=judge_models,
    ),
    runner=dict(type=LocalRunner,
                max_num_workers=16,
                task=dict(type=SubjectiveEvalTask)),
)

summarizer = dict(type=SubjectiveSummarizer, function='subjective')
work_dir = 'outputs/subjective/'
