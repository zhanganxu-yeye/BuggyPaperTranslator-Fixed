# 项目简介

这是一个Python脚本，用于调用Hugging Face的免费API，将英文论文的标题和摘要翻译成中文。特别针对计算机视觉和人工智能领域的学术论文优化了翻译质量。

## 快速开始

1. 环境配置

创建虚拟环境

python -m venv venv

激活虚拟环境


Windows:
venv\Scripts\activate

安装依赖包


pip install -r requirements_fixed.txt

2. 设置Hugging Face Token

在终端中设置环境变量（每次新开终端都需要设置）

Windows:

set HF_TOKEN="你的huggingface_token"

3. 运行翻译程序

python translator_legacy.py

4. 查看结果

翻译结果保存在result.csv中，包含三列：

original_title: 原始英文标题

translated_title: 翻译后的中文标题

translated_abstract: 翻译后的中文摘要

## 关键修复点：从错误到正确

1. 依赖包修复
错误版本 (requirements.txt):

request           # ❌ 少了个s

tdqm              # ❌ q和d顺序错了

huggingface       # ❌ 少了_hub

tensorflow==1.15.0 # ❌ 完全不需要

openai==0.27.0    # ❌ 接口已过时

正确版本 (requirements_fixed.txt):


requests          # ✅ 正确的HTTP请求库

tqdm              # ✅ 进度条显示

huggingface_hub   # ✅ 官方Hugging Face库

tensorflow和openai已删除，因为本项目不需要

2. Token安全修复

错误版本 (硬编码Token):

HF_TOKEN = "hf_KpRxLnmQzYuWcVbNkLoPqRsTuVwXyZaBc"  # ❌ 明文密码！

正确版本 (环境变量读取):

HF_TOKEN = os.getenv("HF_TOKEN")  # ✅ 从环境变量读取

if not HF_TOKEN:

    raise ValueError("请设置环境变量HF_TOKEN")  # ✅ 友好的错误提示

3. API客户端修复

错误版本 (过时接口):


from openai import OpenAI  # ❌ 错误的库

client = OpenAI(

    api_key=HF_TOKEN,
    
    base_url="https://api-inference.huggingface.co",  # ❌ 过时的地址
    
)

正确版本 (最新接口):

from huggingface_hub import InferenceClient  # ✅ 官方推荐

client = InferenceClient(api_key=HF_TOKEN)  # ✅ 一行搞定

4. 模型调用修复

错误版本 (错误的模型和参数):

model_name = "closeai/chatgpt-6"  # ❌ 不存在的模型

temperature=100,  # ❌ 应该是0-1，100完全错了

max_tokens=20,    # ❌ 20个token不够翻译摘要

正确版本 (正确的模型和参数):


MODEL_NAME = "openai/gpt-oss-120b:fastest"  # ✅ 推荐的模型

max_tokens=200 if is_title else 800,  # ✅ 标题200，摘要800

temperature=0.1,  # ✅ 低随机性，保证翻译准确

5. Prompt优化

错误版本 (随意不专业):

"帮我弄一下下面这个文件。"

"你能帮我翻译一下这个文档吗？"

正确版本 (专业学术Prompt):

EXPERT_TRANSLATION_SYSTEM_PROMPT = """你是一位顶尖的计算机科学学术翻译助手...

1. 术语准确：专业名词必须采用学界公认译名

2. 风格正式：使用书面化、严谨的学术中文

3. 忠实原文：不增、删、改原文信息

4. 直接输出：仅输出翻译后的中文文本..."""

6. 功能完善

错误版本 (只翻译摘要):

abstract = row['abstract']

cn_abstract = translate_text(abstract)  # ❌ 只翻译了摘要

正确版本 (翻译标题和摘要):

translated_title = translate_text(original_title, is_title=True)    # ✅ 翻译标题

translated_abstract = translate_text(str(row['abstract']), is_title=False)  # ✅ 翻译摘要

7. 数据格式修复

错误版本 (错误的列名):

row['id']  # ❌ CSV文件中没有id列

正确版本 (正确的列名):

row['title']  # ✅ CSV文件中有title列

8. 工程优化

新增功能 (原版没有):

进度显示
for index, row in tqdm(df.iterrows(), total=total_papers, desc="翻译进度")

断点续传
if os.path.exists(checkpoint_file):
    # 读取已完成的索引

重试机制
@retry(stop=stop_after_attempt(3), wait=wait_exponential(...))
def translate_text(text, is_title=False):

错误日志
with open("translation_errors.log", "a") as error_f:
    error_f.write(f"错误记录...")
文件说明
translator_legacy.py - 主程序（已修复）

requirements_fixed.txt - 正确的依赖包列表

iccv2025.csv - 输入数据（19篇ICCV2025论文）

result.csv - 翻译结果（14篇成功翻译，5篇因额度问题未完成）

注意事项

需要Hugging Face账号和Access Token

免费额度有限（$0.10），可能无法翻译全部论文

运行时间较长，一篇论文约需10-15秒

如果中断，重新运行会从上次中断处继续
