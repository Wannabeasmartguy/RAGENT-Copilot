import json
import random
import inspect
from loguru import logger
from copy import deepcopy
from typing import Any, Dict, List, Union, Optional, Callable
from openai import OpenAI, Stream
from openai.types.chat.chat_completion import ChatCompletion

from utils.chat.prompts import TOOL_USE_PROMPT

def function_to_json(func: Callable[..., Any]) -> str:
    # 获取函数的签名
    sig = inspect.signature(func)
    # 获取函数的文档字符串
    doc = func.__doc__
    
    # 构建参数列表
    properties = {}
    for name, param in sig.parameters.items():
        properties[name] = {
            'type': param.annotation.__name__ if hasattr(param.annotation, '__name__') else str(param.annotation),
            'description': ''  # 这里假设没有每个参数的单独描述
        }
    
    # 构建JSON结构
    function_json = {
        'type': 'function',
        'function': {
            'name': func.__name__,
            'description': doc.strip() if doc else '',
            'parameters': {
                'type': 'object',
                'properties': properties,
                'required': list(sig.parameters.keys())
            }
        }
    }
    
    return json.dumps(function_json, indent=4)

class ToolsParameterOutputParser:
    """将工具调用后返回的消息转换为JSON格式"""
    
    def __call__(self, message: Union[ChatCompletion, Stream]) -> List[Dict[str, Any]]:
        """
        根据输入消息的类型，选择适当的方法进行解析。
        
        :param message: 包含工具调用信息的消息， 可以是ChatCompletion或Stream类型
        :return: 解析后的JSON列表
        """
        if isinstance(message, Stream):
            return self._parse_stream_to_json(message)
        else:
            return self.parse_tools_to_json(message)

    def _generate_unique_id(self) -> str:
    # 生成一个随机的8位数字和字符的组合
        random_str = ''.join(random.choices('0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ', k=8))
        
        # 生成一个唯一的ID
        unique_id = f"call_{random_str}"
        
        return unique_id

    def _parse_stream_to_json(self, stream_output: Stream) -> List[Dict[str, Any]]:
        """将流式输出转换为字典格式的JSON字符串列表"""
        chunks = list(stream_output)
        stream2str = ''.join(chunk.choices[0].delta.content for chunk in chunks if chunk.choices and chunk.choices[0].delta.content is not None)
        logger.debug(stream2str)
        
        params =  [json.loads(param) for param in stream2str.split('\n') if param]
        # 给每个参数添加一个id字段
        # 创建一个可以生成唯一ID的生成器，格式为"call_{id}",id为8位随机数字和字符的组合
        
        return [{'name': param['name'], 'parameters': param['parameters'], 'tool_call_id': self._generate_unique_id()} for param in params]

    def parse_tools_to_json(self, output: ChatCompletion) -> List[Dict[str, Any]]:
        """
        将非流式输出转换为JSON格式的工具参数列表。
        
        :param output: 包含工具调用信息的消息
        :return: 解析后的JSON列表，每个元素是一个包含工具名称和参数的字典
        """
        params = [param.function for param in output.choices[0].message.tool_calls]
        tool_call_ids = [param.id for param in output.choices[0].message.tool_calls]
        
        return [{'name': param.name, 'parameters': json.loads(param.arguments), 'tool_call_id': tool_call_ids[params.index(param)]} for param in params]


def create_tools_call_completion(
        messages: List[Dict[str, Any]], 
        tools: Optional[List[Dict[str, Any]]] = None, 
        function_map: Optional[Dict[str, Any]] = None,
        *,
        model: str = "llama3.1:latest", 
        api_key: str = "noneed",
        base_url: str = "http://localhost:11434/v1",
        stream: bool = False,
    ) -> List[Dict[str, Any]]:
    """
    创建一个响应，如果检测到工具调用，则使用工具调用参数
    
    :param messages: 消息列表
    :param tools: 工具列表
    :param function_map: 函数映射，根据工具名称映射到本地函数
    :return: 包含工具调用参数的一轮完整对话
    """
    parser = ToolsParameterOutputParser()

    client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )

    try:
        # 第一步， 调用模型生成工具调用参数
        # 先删除原有的system message，把专用于tool call的system message添加到消息列表
        messages_copy = deepcopy(messages)
        messages_copy = [message for message in messages_copy if message['role'] != 'system']
        messages_copy.insert(0, {"role":"system", "content":TOOL_USE_PROMPT})
        logger.info("Trying to use tools")
        # logger.debug(f"messages input: {messages_copy}")
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
            tool_choice="auto",
            temperature=0
            # stream=stream
        )
        parsed_params = parser(response)
        logger.debug(parsed_params)
        # 添加工具调用参数到消息列表
        messages.append(dict(response.choices[0].message))

        # 第二步， 根据工具调用参数，本地运行工具，并返回结果
        function_results = [function_map[param['name']](**param['parameters']) for param in parsed_params]
        # 添加所有工具调用结果到消息列表
        for result in function_results:
            messages.append({
                "role":"tool",
                "name": parsed_params[function_results.index(result)]['name'],
                "content":result,
                "tool_call_id":parsed_params[function_results.index(result)]['tool_call_id']
            })
        
        # 第三步， 调用模型生成最终的回复
        logger.debug(f"final messages input: {messages}")
        final_response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
            tool_choice="auto",
            stream=stream
        )
        messages.append(dict(final_response.choices[0].message))
        return final_response
    
    # 对不支持tool call的模型，直接提问
    except Exception as e:
        logger.info(f"Call tools failed: {e}")
        logger.info(f"Use default chat mode without tools")
        return client.chat.completions.create(model=model, messages=messages, stream=stream)