"""Test ChatGoogleGenerativeAI chat model."""

import json
from typing import Generator

import pytest
from langchain_core.messages import (
    AIMessage,
    AIMessageChunk,
    BaseMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from langchain_core.pydantic_v1 import BaseModel
from langchain_core.tools import tool

from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    HarmBlockThreshold,
    HarmCategory,
)
from langchain_google_genai.chat_models import ChatGoogleGenerativeAIError

_MODEL = "models/gemini-1.0-pro-001"  # TODO: Use nano when it's available.
_VISION_MODEL = "gemini-pro-vision"
_B64_string = """iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAIAAAAC64paAAABhGlDQ1BJQ0MgUHJvZmlsZQAAeJx9kT1Iw0AcxV8/xCIVQTuIKGSoTi2IijhqFYpQIdQKrTqYXPoFTRqSFBdHwbXg4Mdi1cHFWVcHV0EQ/ABxdXFSdJES/5cUWsR4cNyPd/ced+8Af6PCVDM4DqiaZaSTCSGbWxW6XxHECPoRQ0hipj4niil4jq97+Ph6F+dZ3uf+HL1K3mSATyCeZbphEW8QT29aOud94ggrSQrxOXHMoAsSP3JddvmNc9FhP8+MGJn0PHGEWCh2sNzBrGSoxFPEUUXVKN+fdVnhvMVZrdRY6578heG8trLMdZrDSGIRSxAhQEYNZVRgIU6rRoqJNO0nPPxDjl8kl0yuMhg5FlCFCsnxg//B727NwuSEmxROAF0vtv0xCnTvAs26bX8f23bzBAg8A1da219tADOfpNfbWvQI6NsGLq7bmrwHXO4Ag0+6ZEiOFKDpLxSA9zP6phwwcAv0rLm9tfZx+gBkqKvUDXBwCIwVKXvd492hzt7+PdPq7wdzbXKn5swsVgAAA8lJREFUeJx90dtPHHUUB/Dz+81vZhb2wrDI3soUKBSRcisF21iqqCRNY01NTE0k8aHpi0k18VJfjOFvUF9M44MmGrHFQqSQiKSmFloL5c4CXW6Fhb0vO3ufvczMzweiBGI9+eW8ffI95/yQqqrwv4UxBgCfJ9w/2NfSVB+Nyn6/r+vdLo7H6FkYY6yoABR2PJujj34MSo/d/nHeVLYbydmIp/bEO0fEy/+NMcbTU4/j4Vs6Lr0ccKeYuUKWS4ABVCVHmRdszbfvTgfjR8kz5Jjs+9RREl9Zy2lbVK9wU3/kWLJLCXnqza1bfVe7b9jLbIeTMcYu13Jg/aMiPrCwVFcgtDiMhnxwJ/zXVDwSdVCVMRV7nqzl2i9e/fKrw8mqSp84e2sFj3Oj8/SrF/MaicmyYhAaXu58NPAbeAeyzY0NLecmh2+ODN3BewYBAkAY43giI3kebrnsRmvV9z2D4ciOa3EBAf31Tp9sMgdxMTFm6j74/Ogb70VCYQKAAIDCXkOAIC6pkYBWdwwnpHEdf6L9dJtJKPh95DZhzFKMEWRAGL927XpWTmMA+s8DAOBYAoR483l/iHZ/8bXoODl8b9UfyH72SXepzbyRJNvjFGHKMlhvMBze+cH9+4lEuOOlU2X1tVkFTU7Om03q080NDGXV1cflRpHwaaoiiiildB8jhDLZ7HDfz2Yidba6Vn2L4fhzFrNRKy5OZ2QOZ1U5W8VtqlVH/iUHcM933zZYWS7Wtj66zZr65bzGJQt0glHgudi9XVzEl4vKw2kUPhO020oPYI1qYc+2Xc0bRXFwTLY0VXa2VibD/lBaIXm1UChN5JSRUcQQ1Tk/47Cf3x8bY7y17Y17PVYTG1UkLPBFcqik7Zoa9JcLYoHBqHhXNgd6gS1k9EJ1TQ2l9EDy1saErmQ2kGpwGC2MLOtCM8nZEV1K0tKJtEksSm26J/rHg2zzmabKisq939nHzqUH7efzd4f/nPGW6NP8ybNFrOsWQhpoCuuhnJ4hAnPhFam01K4oQMjBg/mzBjVhuvw2O++KKT+BIVxJKzQECBDLF2qu2WTMmCovtDQ1f8iyoGkUADBCCGPsdnvTW2OtFm01VeB06msvdWlpPZU0wJRG85ns84umU3k+VyxeEcWqvYUBAGsUrbvme4be99HFeisP/pwUOIZaOqQX31ISgrKmZhLHtXNXuJq68orrr5/9mBCglCLAGGPyy81votEbcjlKLrC9E8mhH3wdHRdcyyvjidSlxjftPJpD+o25JYvRHGFoZDdks1mBQhxJu9uxvwEiXuHnHbLd1AAAAABJRU5ErkJggg=="""  # noqa: E501


def test_chat_google_genai_stream() -> None:
    """Test streaming tokens from Gemini."""
    llm = ChatGoogleGenerativeAI(model=_MODEL)

    for token in llm.stream("This is a test. Say 'foo'"):
        assert isinstance(token.content, str)


async def test_chat_google_genai_astream() -> None:
    """Test streaming tokens from Gemini."""
    llm = ChatGoogleGenerativeAI(model=_MODEL)

    async for token in llm.astream("This is a test. Say 'foo'"):
        assert isinstance(token.content, str)


async def test_chat_google_genai_abatch() -> None:
    """Test streaming tokens from ChatGoogleGenerativeAI."""
    llm = ChatGoogleGenerativeAI(model=_MODEL)

    result = await llm.abatch(
        ["This is a test. Say 'foo'", "This is a test, say 'bar'"]
    )
    for token in result:
        assert isinstance(token.content, str)


async def test_chat_google_genai_abatch_tags() -> None:
    """Test batch tokens from ChatGoogleGenerativeAI."""
    llm = ChatGoogleGenerativeAI(model=_MODEL)

    result = await llm.abatch(
        ["This is a test", "This is another test"], config={"tags": ["foo"]}
    )
    for token in result:
        assert isinstance(token.content, str)


def test_chat_google_genai_batch() -> None:
    """Test batch tokens from ChatGoogleGenerativeAI."""
    llm = ChatGoogleGenerativeAI(model=_MODEL)

    result = llm.batch(["This is a test. Say 'foo'", "This is a test, say 'bar'"])
    for token in result:
        assert isinstance(token.content, str)


async def test_chat_google_genai_ainvoke() -> None:
    """Test invoke tokens from ChatGoogleGenerativeAI."""
    llm = ChatGoogleGenerativeAI(model=_MODEL)

    result = await llm.ainvoke("This is a test. Say 'foo'", config={"tags": ["foo"]})
    assert isinstance(result.content, str)


def test_chat_google_genai_invoke() -> None:
    """Test invoke tokens from ChatGoogleGenerativeAI."""
    llm = ChatGoogleGenerativeAI(model=_MODEL)

    result = llm.invoke(
        "This is a test. Say 'foo'",
        config=dict(tags=["foo"]),
        generation_config=dict(top_k=2, top_p=1, temperature=0.7),
    )
    assert isinstance(result.content, str)
    assert not result.content.startswith(" ")


def test_chat_google_genai_invoke_multimodal() -> None:
    messages: list = [
        HumanMessage(
            content=[
                {
                    "type": "text",
                    "text": "Guess what's in this picture! You have 3 guesses.",
                },
                {
                    "type": "image_url",
                    "image_url": "data:image/png;base64," + _B64_string,
                },
            ]
        ),
    ]
    llm = ChatGoogleGenerativeAI(model=_VISION_MODEL)
    response = llm.invoke(messages)
    assert isinstance(response.content, str)
    assert len(response.content.strip()) > 0

    # Try streaming
    for chunk in llm.stream(messages):
        print(chunk)  # noqa: T201
        assert isinstance(chunk.content, str)
        assert len(chunk.content.strip()) > 0


def test_system_message() -> None:
    messages = [
        SystemMessage(content="Be a helful assistant."),
        HumanMessage(content="Hi, how are you?"),
    ]
    llm = ChatGoogleGenerativeAI(model="models/gemini-1.0-pro-latest")
    answer = llm.invoke(messages)
    assert isinstance(answer.content, str)


def test_chat_google_genai_invoke_multimodal_too_many_messages() -> None:
    # Only supports 1 turn...
    messages: list = [
        HumanMessage(content="Hi there"),
        AIMessage(content="Hi, how are you?"),
        HumanMessage(
            content=[
                {
                    "type": "text",
                    "text": "I'm doing great! Guess what's in this picture!",
                },
                {
                    "type": "image_url",
                    "image_url": "data:image/png;base64," + _B64_string,
                },
            ]
        ),
    ]
    llm = ChatGoogleGenerativeAI(model=_VISION_MODEL)
    with pytest.raises(ChatGoogleGenerativeAIError):
        llm.invoke(messages)


def test_chat_google_genai_invoke_multimodal_invalid_model() -> None:
    # need the vision model to support this.
    messages: list = [
        HumanMessage(
            content=[
                {
                    "type": "text",
                    "text": "I'm doing great! Guess what's in this picture!",
                },
                {
                    "type": "image_url",
                    "image_url": "data:image/png;base64," + _B64_string,
                },
            ]
        ),
    ]
    llm = ChatGoogleGenerativeAI(model=_MODEL)
    with pytest.raises(ChatGoogleGenerativeAIError):
        llm.invoke(messages)


def test_chat_google_genai_single_call_with_history() -> None:
    model = ChatGoogleGenerativeAI(model=_MODEL)
    text_question1, text_answer1 = "How much is 2+2?", "4"
    text_question2 = "How much is 3+3?"
    message1 = HumanMessage(content=text_question1)
    message2 = AIMessage(content=text_answer1)
    message3 = HumanMessage(content=text_question2)
    response = model([message1, message2, message3])
    assert isinstance(response, AIMessage)
    assert isinstance(response.content, str)


def test_chat_google_genai_system_message() -> None:
    model = ChatGoogleGenerativeAI(model=_MODEL, convert_system_message_to_human=True)
    text_question1, text_answer1 = "How much is 2+2?", "4"
    text_question2 = "How much is 3+3?"
    system_message = SystemMessage(content="You're supposed to answer math questions.")
    message1 = HumanMessage(content=text_question1)
    message2 = AIMessage(content=text_answer1)
    message3 = HumanMessage(content=text_question2)
    response = model([system_message, message1, message2, message3])
    assert isinstance(response, AIMessage)
    assert isinstance(response.content, str)


def test_generativeai_get_num_tokens_gemini() -> None:
    llm = ChatGoogleGenerativeAI(temperature=0, model="gemini-pro")
    output = llm.get_num_tokens("How are you?")
    assert output == 4


def test_safety_settings_gemini() -> None:
    safety_settings = {
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    }
    # test with safety filters on bind
    llm = ChatGoogleGenerativeAI(temperature=0, model="gemini-pro").bind(
        safety_settings=safety_settings
    )
    output = llm.invoke("how to make a bomb?")
    assert isinstance(output, AIMessage)
    assert len(output.content) > 0

    # test direct to stream
    streamed_messages = []
    output_stream = llm.stream("how to make a bomb?", safety_settings=safety_settings)
    assert isinstance(output_stream, Generator)
    for message in output_stream:
        streamed_messages.append(message)
    assert len(streamed_messages) > 0

    # test as init param
    llm = ChatGoogleGenerativeAI(
        temperature=0, model="gemini-pro", safety_settings=safety_settings
    )
    out2 = llm.invoke("how to make a bomb")
    assert isinstance(out2, AIMessage)
    assert len(out2.content) > 0


def test_chat_function_calling_with_multiple_parts() -> None:
    @tool
    def search(
        question: str,
    ) -> str:
        """
        Useful for when you need to answer questions or visit websites.
        You should ask targeted questions.
        """
        return "brown"

    tools = [search]

    safety = {
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH
    }
    llm = ChatGoogleGenerativeAI(
        model="models/gemini-1.5-pro-latest", safety_settings=safety
    )
    llm_with_search = llm.bind(
        functions=tools,
    )
    llm_with_search_force = llm_with_search.bind(
        tool_config={
            "function_calling_config": {
                "mode": "ANY",
                "allowed_function_names": ["search"],
            }
        }
    )
    request = HumanMessage(
        content=(
            "Please tell the primary color of following birds: "
            "sparrow, hawk, crow by using searchm"
        )
    )
    response = llm_with_search_force.invoke([request])

    assert isinstance(response, AIMessage)
    assert len(response.tool_calls) > 0
    tool_call = response.tool_calls[0]
    assert tool_call["name"] == "search"

    tool_response = search("sparrow")
    tool_message = ToolMessage(
        name="search",
        content=json.dumps(tool_response),
        tool_call_id="0",
    )

    result = llm_with_search.invoke([request, response, tool_message])

    assert isinstance(result, AIMessage)
    assert "brown" in result.content
    assert len(result.tool_calls) > 0


def _check_tool_calls(response: BaseMessage, expected_name: str) -> None:
    """Check tool calls are as expected."""
    assert isinstance(response, AIMessage)
    assert isinstance(response.content, str)
    assert response.content == ""
    function_call = response.additional_kwargs.get("function_call")
    assert function_call
    assert function_call["name"] == expected_name
    arguments_str = function_call.get("arguments")
    assert arguments_str
    arguments = json.loads(arguments_str)
    assert arguments == {
        "name": "Erick",
        "age": 27.0,
    }
    tool_calls = response.tool_calls
    assert len(tool_calls) == 1
    tool_call = tool_calls[0]
    assert tool_call["name"] == expected_name
    assert tool_call["args"] == {"age": 27.0, "name": "Erick"}


@pytest.mark.extended
def test_chat_vertexai_gemini_function_calling() -> None:
    class MyModel(BaseModel):
        name: str
        age: int

    safety = {
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH
    }
    # Test .bind_tools with BaseModel
    message = HumanMessage(content="My name is Erick and I am 27 years old")
    model = ChatGoogleGenerativeAI(model=_MODEL, safety_settings=safety).bind_tools(
        [MyModel]
    )
    response = model.invoke([message])
    _check_tool_calls(response, "MyModel")

    # Test .bind_tools with function
    def my_model(name: str, age: int) -> None:
        """Invoke this with names and ages."""
        pass

    model = ChatGoogleGenerativeAI(model=_MODEL, safety_settings=safety).bind_tools(
        [my_model]
    )
    response = model.invoke([message])
    _check_tool_calls(response, "my_model")

    # Test .bind_tools with tool
    @tool
    def my_tool(name: str, age: int) -> None:
        """Invoke this with names and ages."""
        pass

    model = ChatGoogleGenerativeAI(model=_MODEL, safety_settings=safety).bind_tools(
        [my_tool]
    )
    response = model.invoke([message])
    _check_tool_calls(response, "my_tool")

    # Test streaming
    stream = model.stream([message])
    first = True
    for chunk in stream:
        if first:
            gathered = chunk
            first = False
        else:
            gathered = gathered + chunk  # type: ignore
    assert isinstance(gathered, AIMessageChunk)
    assert len(gathered.tool_call_chunks) == 1
    tool_call_chunk = gathered.tool_call_chunks[0]
    assert tool_call_chunk["name"] == "my_tool"
    assert tool_call_chunk["args"] == '{"age": 27.0, "name": "Erick"}'
