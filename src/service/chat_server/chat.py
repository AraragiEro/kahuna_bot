from openai import OpenAI

deepseek_r1_32b = "deepseek-r1:32b"
deepseek_ai_DeepSeek_V3 = "deepseek-ai/DeepSeek-V3"

client_online = OpenAI(
    api_key="sk-iisvedmatiudasrwuimkkwacactynyqeovryxfrnzbboqxcd",
    base_url="https://api.siliconflow.cn/v1",
)

client_local = OpenAI(
    api_key="ollama",
    base_url="http://127.0.0.1:11434/v1/",
)

def chat_once(message: str, client, model):
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": message}],
        stream=True
    )
    return response


def print_response(response) -> str:
    res = ""
    for chunk in response:
        if chunk.choices[0].delta.content is not None:
            res += chunk.choices[0].delta.content
    return res





