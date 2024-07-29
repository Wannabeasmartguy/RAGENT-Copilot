# LANGUAGE = "English"
LANGUAGE = "Chinese"

TOOL_USE_PROMPT = "You are an intelligent assistant that chooses whether or not to use a tool based on user commands."

ANSWER_USER_WITH_TOOLS_SYSTEM_PROMPT = """You are an intelligent assistant that chooses whether or not to use a tool based on user commands. 
If you use tools, just answer the question based on the output of the tool without any additional explanation. 
On the other hand, if you don't use tools, answer the question directly as best as you can."""

def get_task_prompts():
    """
    Return a list of task prompts for various text processing tasks. Each prompt is designed to guide the language model
    in performing a specific task such as summarizing, composing an email, fixing grammar, extracting keywords, or explaining text.

    :return: List of dictionaries, each containing a 'task' and its corresponding 'prompt'.
    """
    return [
        {
            "task": "Summarize",
            "prompt": """
Summarize the text below in {language}:

{text}

Summary:
""".strip(),
        },
        {
            "task": "Compose Mail",
            "prompt": """
Compose an email about the text below in {language}:

{text}

Email:
""".strip(),
        },
        {
            "task": "Fix Grammar",
            "prompt": """
Fix the grammar in the text below:

{text}

Corrected Text:
""".strip(),
        },
        {
            "task": "Extract Keywords",
            "prompt": """
List the keywords in the text below in {language}:

{text}

Keywords:
""".strip(),
        },
        {
            "task": "Explain",
            "prompt": """
Explain the text below in {language}:

{text}

Explanation:
""".strip(),
        },
        {
            "task": "Translate",
            "prompt": """
Translate the following source text to **{language}**, Output translation directly without any additional text.
Source Text: {text}
Translated Text:
""".strip(),
        }
    ]


def get_editor_prompts():
    """
    Return a list of prompts for the text editor task. Each prompt is designed to guide the language model in editing text
    to make it more concise, coherent, and engaging.

    :return: List of dictionaries, each containing an 'editor' and its corresponding 'prompt'.
    """

    # ["Casual", "Formal", "Professional", "Technical", "Simple"]

    return [
        {
            "editor": "Casual",
            "prompt": """
Rewrite the text below in a casual tone in {language}:

{text}

Rewritten Text:
""".strip(),
        },
        {
            "editor": "Formal",
            "prompt": """
Rewrite the text below in a formal tone in {language}:

{text}

Rewritten Text:
""".strip(),
        },
        {
            "editor": "Professional",
            "prompt": """
Rewrite the text below in a professional tone in {language}:

{text}

Rewritten Text:
""".strip(),
        },
        {
            "editor": "Technical",
            "prompt": """
Rewrite the text below in a technical tone in {language}:

{text}

Rewritten Text:

""".strip(),
        },
        {
            "editor": "Simple",
            "prompt": """
Rewrite the text below in a simple tone in {language}:

{text}

Rewritten Text:
""".strip(),
        },
    ]
