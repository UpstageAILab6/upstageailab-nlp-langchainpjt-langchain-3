import requests

def make_prompt(retrieved_docs, query):
    retrieved_text = "\n\n".join([doc.page_content for doc in retrieved_docs])
    prompt = f"""
            너는 복지 혜택을 추천해주는 챗봇이야.
            아래는 사용자 질문과 관련된 혜택 문서들이야."

            # Context:
            {retrieved_text}

            # Question:
            {query}

            # Answer:
            - 관련된 복지 혜택을 자연스럽고 친절하게 설명해줘
            - 대상 조건과 신청 방법도 간단히 알려줘
            - 혜택이 여러 개면 순서대로 정리해줘
            - 한글로, 부드럽고 공손한 말투로 작성해줘                    
        """
    return prompt


def query_solar(prompt, api_key, url="https://api.upstage.ai/v1/chat/completions"):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "solar-pro",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 1024,
        "stream": False
    }
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]
