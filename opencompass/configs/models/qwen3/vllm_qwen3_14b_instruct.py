from opencompass.models import VLLMwithChatTemplate

models = [
    dict(
        type=VLLMwithChatTemplate,
        abbr='qwen3-14b-vllm',
        path='/root/sft/Qwen3-14B',
        model_kwargs=dict(tensor_parallel_size=1),
        max_out_len=4096,
        batch_size=16,
        generation_kwargs=dict(
            top_k=20, temperature=0.6, top_p=0.95, do_sample=True, enable_thinking=True
        ),
        run_cfg=dict(num_gpus=0),
    )
]
