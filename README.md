# RAGENT-Copilot

RAGENT-Copilot is a versatile desktop application designed to perform a wide range of text processing tasks using the LLM. It provides intuitive user interface buttons with a variety of shortcut options for summarizing text, translating text, composing emails and interpreting text.

> This software is a secondary development of [local-intelligence](https://github.com/beratcmn/local-intelligence) based on the perspective of integration with the RAGENT application to realize a more comprehensive RAGENT experience and provide more functionality.
>
> The development goal of this software is that it can be used either as a plug-in for RAGENT or run independently.

## Table of Contents

- [RAGENT-Copilot](#ragent-copilot)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Todo](#todo)
  - [Installation](#installation)
    - [Prerequisites](#prerequisites)
    - [Steps](#steps)
  - [Usage](#usage)
    - [Run from source](#run-from-source)
    - [Run from executable](#run-from-executable)
  - [Contributing](#contributing)
  - [License](#license)

## Features

- **Summarize Text:** Get concise summaries of lengthy text.
- **Compose Emails:** Automatically draft emails based on input text.
- **Fix Grammar:** Correct grammatical errors in your text.
- **Extract Keywords:** Identify key terms and phrases.
- **Explain Text:** Generate explanations for complex text.
- **Rephrase Generated Text:** Rephrase the generated text based on the desired tone. Tones are categorized as `Casual`, `Formal`, `Professional`, `Technical`, `Simple`.

## Todo

- [x] Ollama inference support
- [x] Add more features such as rephrasing according to desired tone of voice
- [x] Streaming output support
- [ ] Multi-language support (RAGENT-based i18n support)
- [ ] Support for model customization (RAGENT-based model customization)
- [ ] Build project as standalone executable
- [ ] Create user-friendly installers for applications

## Installation

### Prerequisites

- Python 3.8 or higher

### Steps

1. **Clone the repository:**

   ```sh
   git clone https://github.com/Wannabeasmartguy/RAGENT-Copilot.git
   cd RAGENT-Copilot
   ```

2. **Create a virtual environment:**

   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate.ps1 or venv\Scripts\activate.bat`
   ```

3. **Install the dependencies:**

   ```sh
   pip install -r requirements.txt
   ```

4. **Download ollama**

Ollama is an open source application for local inference, providing a large selection of quantitative models to run locally and an API compatible with the OpenAI API, greatly simplifying model management and inference.

This software uses Ollama for inference by default, so you will need to install Ollama first. You can download the platform-specific versions they offer from their [official website](https://ollama.com/).

Once you have downloaded and run it, type `ollama --version` in the terminal, and if the version number is output, the installation is successful.

5. **Download model:**

Currently, the default model used is `qwen2:1.5b`, which as an SLM model is able to run locally and has good performance.

You can find more information about this model [here](https://huggingface.co/Qwen/Qwen2-1.5B).

And to download the model in Ollama, just enter the following command in the terminal:

```sh
ollama pull qwen2:1.5b
```

## Usage

### Run from source

1.**Run the application:**

    In the root directory of this project, run the following command:
    ```sh
    python src/app.py
    ```

2.**To bring up the graphical user interface:**
   - Press ``CTRL + Shift + SPACE`` to bring up the application window.
   - Use the mouse to drag to select the text to be processed.
   - Select the desired task by clicking on the corresponding button.
   - The result will be displayed in a new window.

### Run from executable

1.** Download the executable file:**

   You can download the installation navigation for your operating system from [here](https://github.com/Wannabeasmartguy/RAGENT-Copilot/releases). (Currently available for Windows only)

2.**Run the Installation Navigator:**

   Double-click to launch the application installation navigation.

3.**Running the application:**

   Follow the instructions of the installation navigation, after completing the installation, you can find the shortcut of the application in the start menu and click to launch the application.

   - Press `CTRL + SPACE` or click on the taskbar icon in the lower right corner to bring up the application window.
   - Drag the mouse to select the text you want to work with.
   - Select the desired task by clicking on the corresponding button.
   - The result will be displayed in a new window.

## Contributing

If you have any suggestions or improvements, please feel free to submit a pull request or open an issue.

## License

This project is licensed under the Apache 2.0 License - see the [LICENSE](LICENSE) file for details.
