from openai import OpenAI
import os

endpoint_id = os.environ.get("RUNPOD_ENDPOINT_ID")
api_key = os.environ.get("RUNPOD_API_KEY")

client = OpenAI(
    base_url=f"https://api.runpod.ai/v2/vllm-s3pvquqjat694h/openai/v1",
    api_key='4EO5ZALI90E137V0AACNHQ7QNT0ANQBX3OWT461W',
)

chat_completion = client.chat.completions.create(
    model="h2oai/llama-3-8b-instruct-awq",
    messages=[{"role": "user", "content": "Tell me a short story about space, only a few sentences"}]
)

print(chat_completion)
