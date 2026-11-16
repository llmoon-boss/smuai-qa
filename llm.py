import requests

from config import LLM_CONFIG, MOCK_ANSWER

SYSTEM_PROMPT = (
    "你是 SMUAI，三明学院的校园智能问答助手，负责回答在校学生的校园生活与学习相关问题。"
    "要求："
    "(1) 只回答与校园相关的合理问题；"
    "(2) 不确定的信息要明确说明，不要编造；"
    "(3) 回答简洁、分点、口语化，不超过 200 字；"
    "(4) 涉及具体政策时提示以学校官方通知为准。"
)


def chat_once(question):
    """单轮问答"""
    api_key = LLM_CONFIG["api_key"]
    if not api_key:
        return MOCK_ANSWER.format(question=question), False

    payload = {
        "model": LLM_CONFIG["model"],
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": question},
        ],
        "max_tokens": LLM_CONFIG["max_tokens"],
        "temperature": LLM_CONFIG["temperature"],
        "stream": False,
    }
    try:
        resp = requests.post(
            f"{LLM_CONFIG['base_url'].rstrip('/')}/chat/completions",
            json=payload,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            timeout=LLM_CONFIG["timeout"],
        )
        resp.raise_for_status()
        answer = resp.json()["choices"][0]["message"]["content"].strip()
        return answer, True
    except Exception as e:  # 超时、限流、网络错误等统一降级
        print(f"[llm] 调用失败：{e}")
        return "（大模型服务暂时不可用，请稍后再试；也可在知识库管理后台补充该问题的答案。）", False
