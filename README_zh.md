# RAGENT-Copilot

RAGENT-Copilot 是一款多功能的桌面应用程序，旨在使用 LLM 执行多种文本处理任务。它提供了直观的用户界面按钮，提供总结文本、翻译文本、撰写邮件和解释文本等多种快捷选项。

> 本软件是基于与 RAGENT 应用集成的角度，对[local-intelligence](https://github.com/beratcmn/local-intelligence)进行二次开发，以实现 RAGENT 更加全面的体验和提供更多功能。
>
> 本软件的开发目标是既可以作为 RAGENT 的插件，也可以独立运行。

## 目录

- [RAGENT-Copilot](#ragent-copilot)
  - [目录](#目录)
  - [功能](#功能)
  - [安装](#安装)
    - [先决条件](#先决条件)
    - [步骤](#步骤)
  - [使用](#使用)
    - [从源码运行](#从源码运行)
    - [从可执行文件运行](#从可执行文件运行)
  - [贡献](#贡献)
  - [许可证](#许可证)

## 功能

- **总结文本：** 获取冗长文本的简明摘要。
- **撰写电子邮件：** 根据输入文本自动起草电子邮件。
- **修正语法：** 纠正文本中的语法错误。
- **提取关键词：** 识别关键术语和短语。
- **解释文本：** 生成复杂文本的解释。
- **改写生成的文本：** 根据所需的语气改写生成的文本。语气分为 "休闲（`Casual`）"、"正式（`Formal`）"、"专业（`Professional`）"、"技术（`Technical`）" 和 "简单（`Simple`）"。

- [x] Ollama inference 支持
- [x] 增加更多功能，例如根据所需的语气重新措辞
- [x] 支持流式输出
- [ ] 支持多语言（基于 RAGENT 的 i18n 支持）
- [ ] 支持模型自定义配置（基于 RAGENT 的模型自定义配置）
- [ ] 将项目构建独立可执行文件
- [ ] 为应用程序创建用户友好型安装程序

## 安装

### 先决条件

- Python 3.8 或更高版本

### 步骤

1.**克隆版本库：**

   ```sh
   git clone https://github.com/Wannabeasmartguy/RAGENT-Copilot.git
   cd RAGENT-Copilot
   ```

2.**创建虚拟环境：**

   ```sh
   python -m venv venv
   source venv/bin/activate # 在 Windows 上使用 `venv\Scripts\activate.ps1 或 venv\Scripts\activate.bat`.
   ```

3.**安装依赖项：**

   ```sh
   pip install -r requirements.txt
   ```

4.**下载ollama**

Ollama 是一个本地推理的开源应用程序，提供了大量可供选择的量化模型以便在本地运行，并且提供了与 OpenAI API 相兼容的 API ，大大简化了模型的管理和推理。

本软件默认使用 Ollama 进行推理，因此需要先安装 Ollama。您可以前往它们[官方网站](https://ollama.com/)下载它们提供的各平台版本。

下载成功并运行后，在终端输入 `ollama --version` ，如果输出版本号，则说明安装成功。

5. **下载模型：**

目前，默认使用的模型为 `qwen2:1.5b` ，作为 SLM 模型，它能够在本地运行，并且具有较好的性能。

您可以在[这里](https://huggingface.co/Qwen/Qwen2-1.5B)找到更多关于该模型的信息。

而要在 Ollama 中下载该模型，只需要在终端输入以下命令：

```sh
ollama pull qwen2:1.5b
```

## 使用

### 从源码运行

1.**运行应用程序：**

    在本项目的根目录下，运行以下命令：
    ```sh
    python src/app.py
    ```

2.**唤出图形用户界面：**
   - 按 `CTRL + Shift + SPACE` 键唤出应用程序窗口。
   - 使用鼠标拖动选定需要处理的文本。
   - 点击相应的按钮，选择所需的任务。
   - 结果将显示在新窗口中。

### 从可执行文件运行

1.**下载可执行文件：**

   您可以从[这里](https://github.com/Wannabeasmartguy/RAGENT-Copilot/releases)下载适用于您的操作系统的安装导航。（目前仅提供 Windows 版本）

2.**运行安装导航：**

   双击即可启动应用安装导航。

3.**运行应用程序：**

   跟随安装导航的指示，完成安装后，您可以在开始菜单中找到应用程序的快捷方式，单击即可启动应用程序。 

   - 按 `CTRL + SPACE` 键或单击右下角的任务栏图标唤出应用程序窗口。
   - 使用鼠标拖动选定需要处理的文本。
   - 点击相应的按钮，选择所需的任务。
   - 结果将显示在新窗口中。

## 贡献

如果您有任何建议或改进，请随时提交拉取请求或提 issue 。

## 许可证

本项目根据 Apache License 2.0 许可证授权。有关详细信息，请参阅 LICENSE 文件。