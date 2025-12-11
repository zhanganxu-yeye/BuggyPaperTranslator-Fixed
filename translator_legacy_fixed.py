import os
import time
import pandas as pd
from tqdm import tqdm
from huggingface_hub import InferenceClient
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import requests.exceptions

# ========== 配置部分 ==========
HF_TOKEN = os.getenv("HF_TOKEN")
if not HF_TOKEN:
    raise ValueError(
        "请设置环境变量 HF_TOKEN：在命令行执行 set HF_TOKEN=\"你的token\" (Windows) "
        "或 export HF_TOKEN=\"你的token\" (Mac/Linux)"
    )

client = InferenceClient(api_key=HF_TOKEN)

# 使用教授推荐的模型
MODEL_NAME = "openai/gpt-oss-120b:fastest"

# 精心设计的专业学术翻译System Prompt
EXPERT_TRANSLATION_SYSTEM_PROMPT = """你是一位顶尖的计算机科学学术翻译助手，专门处理计算机视觉与人工智能领域的论文。
请将用户提供的英文论文标题或摘要严格、准确地翻译为中文。
请严格遵守以下核心要求：
1.  **术语准确**：专业名词（如Diffusion Models, CLIP, Transformer）必须采用学界公认译名。若无统一译名，可谨慎保留英文。
2.  **风格正式**：使用书面化、严谨的学术中文，避免口语化表达。
3.  **忠实原文**：不增、删、改原文信息，完整保留其逻辑关系和学术语气。
4.  **直接输出**：仅输出翻译后的中文文本，不要添加任何解释、引导词（如“翻译如下：”）或备注。

请开始你的翻译工作。"""

# ========== 翻译函数（带重试机制） ==========
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((requests.exceptions.RequestException, Exception))
)
def translate_text(text, is_title=False):
    """
    翻译单条文本（标题或摘要），具有重试机制。
    is_title: 是否为标题，用于调整参数。
    """
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": EXPERT_TRANSLATION_SYSTEM_PROMPT},
                {"role": "user", "content": text}
            ],
            # 参数设置：标题需要更少的token，摘要需要更多
            max_tokens=200 if is_title else 800,
            temperature=0.1,  # 低随机性，保证翻译的准确性和一致性
            top_p=0.9,
        )
        # 从诊断确认的结构中提取内容
        translated_text = response.choices[0].message.content.strip()
        return translated_text
            
    except Exception as e:
        print(f"翻译出错（将重试）: {str(e)[:100]}...")
        raise

# ========== 主函数 ==========
def main():
    input_file = "iccv2025.csv"
    output_file = "result.csv"
    checkpoint_file = "checkpoint.txt"

    print("=" * 70)
    print("学术论文翻译工具启动 (最终版)")
    print(f"使用模型: {MODEL_NAME}")
    print("功能：同时翻译论文标题与摘要")
    print("=" * 70)

    try:
        df = pd.read_csv(input_file)
        print(f"成功读取文件: {input_file}，共 {len(df)} 篇论文")
    except FileNotFoundError:
        print(f"错误：找不到文件 {input_file}")
        return

    file_mode = "a" if os.path.exists(output_file) else "w"
    write_header = not os.path.exists(output_file)

    completed_indices = set()
    if os.path.exists(checkpoint_file):
        with open(checkpoint_file, "r", encoding="utf-8") as f:
            completed_indices = set(int(line.strip()) for line in f)
        print(f"从检查点恢复: 已跳过 {len(completed_indices)} 篇已翻译论文")

    with open(output_file, file_mode, encoding="utf-8") as out_f:
        if write_header:
            # 输出包含：原始标题，翻译后标题，翻译后摘要
            out_f.write("original_title,translated_title,translated_abstract\n")

        total_papers = len(df)
        for index, row in tqdm(df.iterrows(), total=total_papers, desc="翻译进度"):
            if index in completed_indices:
                continue

            original_title = str(row['title'])
            if pd.isna(row['abstract']):
                print(f"警告: 论文 '{original_title[:30]}...' 无摘要，跳过")
                continue

            try:
                # 分别翻译标题和摘要
                print(f"\n处理第 {index+1} 篇: {original_title[:50]}...")
                print("  翻译标题...")
                translated_title = translate_text(original_title, is_title=True)
                print("  翻译摘要...")
                translated_abstract = translate_text(str(row['abstract']), is_title=False)

                # 写入结果，确保CSV格式正确（用引号包裹字段）
                out_f.write(f'\"{original_title}\",\"{translated_title}\",\"{translated_abstract}\"\n')
                out_f.flush()

                # 更新检查点（记录索引）
                with open(checkpoint_file, "a", encoding="utf-8") as checkpoint_f:
                    checkpoint_f.write(f"{index}\n")

                # 避免触发Rate Limit，免费模型需要稍长间隔
                time.sleep(3)

            except Exception as e:
                error_msg = f"论文 '{original_title[:30]}...' 处理失败: {str(e)[:50]}..."
                print(error_msg)
                with open("translation_errors.log", "a", encoding="utf-8") as error_f:
                    error_f.write(f"Index:{index},Title:\"{original_title}\",Error:{str(e)}\n")

    print("\n" + "=" * 70)
    print("✅ 翻译完成！")
    print(f"   结果文件: {output_file} (包含原始标题、译后标题、译后摘要)")
    print(f"   检查点: {checkpoint_file}")
    print("=" * 70)

if __name__ == "__main__":
    main()
