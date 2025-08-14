from opencompass.models import OpenAISDK

api_meta_template = dict(
    round=[
        dict(role='HUMAN', api_role='HUMAN'),
        dict(role='BOT', api_role='BOT', generate=True),
    ],
    reserved_roles=[dict(role='SYSTEM', api_role='SYSTEM')],
)

models = [
    dict(
        abbr='Qwen3-14B',
        type=OpenAISDK,
        key='EMPTY', # API key
        openai_api_base='http://localhost:8001/v1', # 服务内网IP
        path='Qwen3-14B', # 请求服务时的 model name
        tokenizer_path='/root/sft/Qwen3-14B', # 请求服务时的 tokenizer name 或 path, 为None时使用默认tokenizer gpt-4
        rpm_verbose=True, # 是否打印请求速率
        meta_template=api_meta_template, # 服务请求模板
        query_per_second=10, # 服务请求速率
        max_out_len=4096, # 最大输出长度
        max_seq_len=32768, # 最大输入长度
        temperature=0.6, # 生成温度
        extra_body=dict(
            top_k=20, temperature=0.6, top_p=0.95, do_sample=True,min_p=0 
        ),
        batch_size=16, # 批处理大小
        retry=3, # 重试次数
    )
]