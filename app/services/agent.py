import json

from openai import OpenAI

from app.config import LLM_API_KEY, LLM_MODEL


class Agent:
    """
    Minimal tool-calling agent.

    Learning goal:
        Understand the mechanics of:

        User
          ↓
        LLM
          ↓
        Tool call
          ↓
        Application executes tool
          ↓
        Tool result
          ↓
        LLM
          ↓
        Final answer

    IMPORTANT:
        The LLM does NOT execute Python functions.

        The LLM only decides:
            - whether a tool is useful
            - which tool to call
            - what arguments to provide

        The application is responsible for:
            - validating the tool
            - parsing arguments
            - executing the tool
            - handling errors
            - returning the tool result to the LLM
    """

    SYSTEM_PROMPT = (
        "You are a helpful AI assistant. "
        "Use available tools when they are useful. "
        "Answer clearly and concisely."
    )

    def __init__(self):
        self.model = LLM_MODEL

        # OpenRouter exposes an OpenAI-compatible API.
        #
        # We are intentionally using the OpenAI SDK directly instead
        # of LangChain/LangGraph so that we understand the mechanics
        # of tool calling first.
        self.client = OpenAI(
            api_key=LLM_API_KEY,
            base_url="https://openrouter.ai/api/v1",
        )

    # ------------------------------------------------------------------
    # TOOL IMPLEMENTATION
    # ------------------------------------------------------------------

    @staticmethod
    def add_numbers(a: int, b: int) -> int:
        """
        Actual Python implementation of the tool.

        The LLM never executes this function directly.

        The flow is:

            LLM says:
                "I want to call add_numbers with a=25, b=17"

            Application:
                self.add_numbers(a=25, b=17)

            Python:
                returns 42
        """
        return a + b

    # ------------------------------------------------------------------
    # TOOL DEFINITIONS
    # ------------------------------------------------------------------

    @staticmethod
    def get_tools() -> list[dict]:
        """
        Return the tool definitions that are sent to the LLM.

        This is NOT the Python function itself.

        It is a description/schema telling the model:

            "This capability exists."
            "This is its name."
            "These arguments are required."
            "These arguments must be integers."
        """

        return [
            {
                "type": "function",
                "function": {
                    "name": "add_numbers",
                    "description": "Add two numbers together.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "a": {
                                "type": "integer",
                                "description": "The first number.",
                            },
                            "b": {
                                "type": "integer",
                                "description": "The second number.",
                            },
                        },
                        "required": ["a", "b"],
                    },
                },
            }
        ]

    # ------------------------------------------------------------------
    # TOOL EXECUTION
    # ------------------------------------------------------------------

    def execute_tool(self, tool_name: str, arguments: dict):
        """
        Execute a tool requested by the LLM.

        IMPORTANT SECURITY BOUNDARY:

        Never blindly execute whatever function name the model provides.

        The application must maintain control over which tools are
        actually executable.

        For now we use an explicit if-condition because there is only
        one tool.

        Later, this can become a tool registry.
        """

        if tool_name == "add_numbers":
            return self.add_numbers(**arguments)

        # Unknown tools must never be executed.
        raise ValueError(f"Unknown tool: {tool_name}")

    # ------------------------------------------------------------------
    # MAIN AGENT LOOP
    # ------------------------------------------------------------------

    def chat(self, message: str) -> str:
        """
        Process one user message.

        Current learning implementation:

            1. Send user message + tool definitions to LLM.
            2. Check whether LLM requested a tool.
            3. If no tool:
                   return normal LLM response.
            4. If tool requested:
                   execute tool in Python.
            5. Send tool result back to LLM.
            6. Return final LLM response.

        LIMITATION:

            This implementation supports only ONE LLM → tool →
            LLM cycle.

            It does NOT yet implement an unlimited/repeated agent loop.

        For example:

            User
              ↓
            LLM
              ↓
            Tool
              ↓
            LLM
              ↓
            Final answer

        But not yet:

            LLM
              ↓
            Tool A
              ↓
            LLM
              ↓
            Tool B
              ↓
            LLM
              ↓
            Tool C
              ↓
            Final answer

        We will introduce a proper iterative agent loop later.
        """

        # --------------------------------------------------------------
        # STEP 1 — CREATE INITIAL CONVERSATION
        # --------------------------------------------------------------

        messages = [
            {
                "role": "system",
                "content": self.SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": message,
            },
        ]

        # --------------------------------------------------------------
        # STEP 2 — TELL THE MODEL WHICH TOOLS ARE AVAILABLE
        # --------------------------------------------------------------

        tools = self.get_tools()

        # --------------------------------------------------------------
        # STEP 3 — ASK THE MODEL WHAT TO DO
        # --------------------------------------------------------------

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=tools,
        )

        assistant_message = response.choices[0].message

        print("\n--- LLM RESPONSE ---")
        print("Content:", assistant_message.content)
        print("Tool calls:", assistant_message.tool_calls)
        
        # --------------------------------------------------------------
        # STEP 4 — MODEL DID NOT REQUEST A TOOL
        # --------------------------------------------------------------

        if not assistant_message.tool_calls:
            """
            Example:

                User:
                    "What is the capital of France?"

                LLM:
                    "The capital of France is Paris."

            No tool is necessary.

            Therefore we simply return the model's answer.
            """

            return assistant_message.content or ""

        # --------------------------------------------------------------
        # STEP 5 — MODEL REQUESTED ONE OR MORE TOOLS
        # --------------------------------------------------------------

        # The assistant message containing tool_calls must be added
        # back into the conversation.

        messages.append(assistant_message)

        # IMPORTANT:
        #
        # tool_calls is a list.
        #
        # A model can request multiple tools in one response.
        #
        # Example:
        #
        #   tool_calls = [
        #       add_numbers(10, 20),
        #       add_numbers(30, 40)
        #   ]
        #
        # Therefore we should not assume there is only one tool call.

        for tool_call in assistant_message.tool_calls:

            # ----------------------------------------------------------
            # STEP 5A — GET TOOL NAME
            # ----------------------------------------------------------

            tool_name = tool_call.function.name

            # ----------------------------------------------------------
            # STEP 5B — GET TOOL ARGUMENTS
            # ----------------------------------------------------------

            # Tool arguments are returned as JSON text.

            try:
                arguments = json.loads(tool_call.function.arguments)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"Invalid JSON arguments for tool '{tool_name}'"
                ) from exc

            # ----------------------------------------------------------
            # STEP 5C — EXECUTE TOOL
            # ----------------------------------------------------------

            # The LLM requested the tool.
            #
            # Python/application executes it.
            #
            # The model itself never executes Python code.

            try:
                result = self.execute_tool(
                    tool_name=tool_name,
                    arguments=arguments,
                )
            except Exception as exc:
                # For this learning implementation we raise the error.
                #
                # A production agent would usually convert tool failures
                # into a structured tool result and allow the LLM to
                # explain/recover when appropriate.
                raise RuntimeError(
                    f"Tool '{tool_name}' execution failed"
                ) from exc

            # ----------------------------------------------------------
            # STEP 5D — RETURN TOOL RESULT TO THE MODEL
            # ----------------------------------------------------------

            messages.append(
                {
                    "role": "tool",

                    # This ID connects the tool result with the exact
                    # tool call requested by the model.
                    "tool_call_id": tool_call.id,

                    # Tool results are sent back as content.
                    "content": json.dumps(result),
                }
            )

        # --------------------------------------------------------------
        # STEP 6 — ASK THE MODEL TO PRODUCE THE FINAL ANSWER
        # --------------------------------------------------------------

        final_response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=tools,
        )

        final_message = final_response.choices[0].message

        # --------------------------------------------------------------
        # STEP 7 — RETURN FINAL ANSWER
        # --------------------------------------------------------------

        return final_message.content or ""