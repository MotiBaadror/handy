import litellm


class Response:
    def __init__(self, type: str, content: str | None = None):
        self.type = type
        self.content = content


class Brain:
    def __init__(self, model: str, api_key: str):
        self.model = model
        self.api_key = api_key

    def call(self, messages: list[dict]) -> Response:
        result = litellm.completion(
            model=self.model,
            messages=messages,
            api_key=self.api_key,
        )
        message = result.choices[0].message

        if message.tool_calls:
            return Response(type="tool_call")

        content = message.content
        if content and content.strip():
            return Response(type="content", content=content)

        return Response(type="empty")
