import litellm


class Response:
    def __init__(self, type: str, content: str | None = None, tool_calls=None):
        self.type = type
        self.content = content
        self.tool_calls = tool_calls  # raw tool calls from LLM


class Brain:
    def __init__(self, model: str, api_key: str, tools: list | None = None):
        self.model = model
        self.api_key = api_key
        self.tools = tools or []  # list of tool schemas to pass to LLM

    def call(self, messages: list[dict]) -> Response:
        result = litellm.completion(
            model=self.model,
            messages=messages,
            api_key=self.api_key,
            tools=self.tools or None,
        )
        message = result.choices[0].message

        if message.tool_calls:
            return Response(type="tool_call", tool_calls=message.tool_calls)

        content = message.content
        if content and content.strip():
            return Response(type="content", content=content)

        # reasoning models (e.g. deepseek, o1) emit thinking tokens with no visible content
        if getattr(message, "reasoning_content", None):
            return Response(type="reasoning")

        return Response(type="empty")
