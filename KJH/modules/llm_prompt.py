import requests

def make_prompt(retrieved_docs, query):
    if not retrieved_docs:
        return (
            "You are an assistant for answering questions about Korean government support policies.\n"
            "There is no retrieved context available.\n"
            f"Answer the following question as best as you can or say '잘 모르겠습니다.'\n\n"
            f"# Question:\n{query}\n\n# Answer:"
        )

    retrieved_text = "\n\n".join([doc.page_content for doc in retrieved_docs])
    prompt = f"""
        You are an assistant for answering questions about Korean government support policies.
        Use the following retrieved context to answer the user's question.
        If the answer is not in the context, say "잘 모르겠습니다."
        Respond in Korean.

        # Context:
        {retrieved_text}

        # Question:
        {query}

        # Answer:
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
