from opencompass.models import HuggingFacewithChatTemplate

models = [
    dict(
        type=HuggingFacewithChatTemplate,
        abbr='qwen3-14b-instruct-hf',
        path='/root/sft/Qwen3-14B',
        gen_config=dict(
            top_k=20, temperature=0.6, top_p=0.95, do_sample=True, enable_thinking=True
        ),
        max_seq_len=32768,
        max_out_len=32000,
        batch_size=16,
        run_cfg=dict(num_gpus=1),
    )
]
