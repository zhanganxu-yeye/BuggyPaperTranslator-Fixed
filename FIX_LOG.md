**修复日志：从零开始的Python项目求生记**

*1.完全看不懂的阶段*

问题：只学过C语言的大二学生，看到Python项目完全懵了。什么pandas、API、token，完全不懂。

解决：先用deepseek帮我解读了README里的各种名词概念，明白了这是一个用Hugging Face API翻译论文的项目。

*2.注册地狱*

问题：注册Hugging Face账号时，不知道什么原因，反复换节点都注册不成功。

解决：最后在闲鱼上找了位大神帮忙，终于注册成功，账号名是AnatoleYY。

*3.Git仓库获取失败*

问题：克隆教授给的GitHub仓库时，遇到SSL证书错误，无法下载代码。

解决：尝试用git config --global http.sslVerify false关闭SSL验证，但还是不行。后来最终直接通过浏览器下载了ZIP压缩包。在自己GitHub上新建了仓库BuggyPaperTranslator-Fixed来管理修改。

*4.Python环境问题*

问题：我的电脑没装Python，第一次装了个最新的3.14.0a5版本。运行代码时直接出现Segmentation fault错误。查了半天发现是Python 3.14是Alpha测试版，极其不稳定

解决：卸载3.14，重新安装了稳定的Python 3.11.9。学会了用虚拟环境：python -m venv venv。终于看到了正常的Python输出，不是段错误了！

*5.修改依赖包*

问题：原始的requirements.txt里一堆错误：

request ❌（应该是requests，少了个s）

tdqm ❌（应该是tqdm，q和d顺序错了）

huggingface ❌（应该是huggingface_hub，少了_hub）

还有完全不需要的tensorflow和openai

解决：查了每个包的作用，理解了：

pandas：处理表格数据（类似Excel）

tqdm：显示进度条

huggingface_hub：访问Hugging Face的库

tenacity：重试机制

创建了正确的requirements_fixed.txt

*6.解决Token安全问题*

问题：原始代码里直接把Token写在代码里：HF_TOKEN = "hf_KpRxLnmQ..."，这是极其危险的！

解决：学到一个重要原则：永远不要硬编码敏感信息。改成从环境变量读取：os.getenv("HF_TOKEN")。学会了在终端设置环境变量：export HF_TOKEN="我的token"

*7.API接口更改*

问题：原始代码用的openai库和base_url已经过时了，完全不工作。

解决：

查阅Hugging Face最新文档

找到官方推荐的InferenceClient

把原来复杂的客户端初始化简化为一行：

client = InferenceClient(api_key=HF_TOKEN)  # 新版

原来的是：

client = OpenAI(api_key=HF_TOKEN, base_url="过时的地址")  # 旧版

*8.模型选择*

问题：

一开始试图用deepseek推荐给我的Helsinki-NLP/opus-mt-en-zh（专用翻译模型）

但发现它不支持chat接口，只支持translation接口，是一个翻译专用，这不符合项目需求。而且无法使用System Prompt优化翻译质量

解决：

测试了教授推荐的openai/gpt-oss-120b:fastest

终于可以用chat接口了，而且支持System Prompt

同时测试了备用模型microsoft/Phi-3-mini-4k-instruct作为备选方案

*9.Prompt设计*

问题：原始Prompt是"帮我弄一下下面这个文件。"，太随意了，翻译质量差。

解决：设计专业的学术翻译Prompt

明确要求：

术语准确（专业名词用学界公认译名）

风格正式（学术中文，不用口语）

忠实原文（不增删改信息）

直接输出（不加"翻译如下："这类废话）

*10.数据格式坑*

问题：代码里写的是row['id']，但CSV文件里没有id列，只有title列。导致程序崩溃，报KeyError错误

解决：用pandas打印了所有列名确认：print(df.columns)。发现列名是title、abstract、authors等。把代码中所有row['id']都改成了row['title']

*11.需求理解偏差*

问题：教授要求翻译"标题和摘要"，但我只翻译了摘要，忘了标题。

解决：

重新读了一遍需求文档，确认是要翻译两者。修改代码，对每篇论文分别翻译标题和摘要。优化参数：标题用max_tokens=200，摘要用max_tokens=800

*12.临近胜利的无奈突发情况：huggingface免费额度耗尽*


问题：翻译到一半，Hugging Face发邮件说免费额度用完了（$0.10额度）
解决：

庆幸已经实现了断点续传功能

检查发现19篇论文翻译了14篇

用占位符标记了未翻译的论文，保证CSV格式完整，且最终结果虽然不完整，但说明断点续传功能成功！

****最终成果****

经过13天的努力，终于：

✅ 环境配置完成（Python 3.11.9 + 虚拟环境）

✅ 所有依赖包正确安装

✅ 代码成功运行，翻译了14篇论文

✅ 实现了断点续传、进度显示、异常重试

✅ 提交了完整的修复后代码仓库

学到的重要经验：

不要用Alpha版本的Python：稳定版才是王道

敏感信息放环境变量：Token绝对不能写死在代码里

先验证数据格式：不要假设CSV文件有什么列

完整理解需求：标题和摘要都要翻译

为网络服务添加重试：API调用可能失败，要有重试机制

云服务有免费额度：用完就没了，要有应对方案

虽然最后因为额度问题没有全部翻译完，但整个项目从不能运行到能稳定运行，我已经学到了很多。
