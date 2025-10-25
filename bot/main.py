import asyncio
import os
from typing import Any, Awaitable, Callable

import openai
from aiogram import BaseMiddleware, Bot, Dispatcher, Router
from aiogram.filters import CommandStart
from aiogram.types import Message, TelegramObject, Update
from langchain.chat_models import init_chat_model
from langchain_core.messages import AIMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent

TOKEN = os.environ.get("TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)

prompt = """
Ты ассистент. Ты выполняешь просьбы пользователей.
У тебя есть доступ к манипулятору (механической руки) С помощью инструмента "move" ты можешь передвинуть кубик на позиции от 1 до 4. Если пользователь просит позицию меньше 1 или больше 4, скажи что ты не можешь.
С помощью инструмента sleep ты можешь подождать какое-то количество секунд
"""

bot = Bot(TOKEN)

router = Router()

agent: Any = None


async def transcribe(message: Message):
    assert message.voice
    voice_file = await bot.get_file(message.voice.file_id)
    voice_path = f"temp_voice_{message.message_id}.ogg"

    assert voice_file.file_path

    await bot.download_file(voice_file.file_path, voice_path)
    # Конвертируем и распознаем
    with open(voice_path, "rb") as audio_file:
        text = openai_client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language="ru",
            response_format="text",
        )

    os.remove(voice_path)

    return text


class RecognitionMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        update: TelegramObject,
        data: dict[str, Any],
    ):
        assert isinstance(update, Update)
        try:
            if update.message and update.message.text:
                data["input"] = update.message.text
            elif update.message and update.message.voice:
                data["input"] = await transcribe(update.message)
            else:
                data["input"] = None
        except Exception as e:
            print(e)
            data["text"] = None

        return await handler(update, data)


@router.message(CommandStart())
async def start(message: Message):
    await message.answer("Hello world")


@router.message()
async def query(message: Message, input: str | None):
    if input is None:
        await message.answer("Нет ввода")
        return
    print("running")
    assert agent
    response = await agent.ainvoke({"messages": [{"role": "user", "content": input}]})
    print(response)
    aim: AIMessage = response["messages"][-1]
    await message.answer(aim.content)


async def main():
    global agent
    client = MultiServerMCPClient(
        {"robot": {"url": "http://localhost:8000/mcp", "transport": "streamable_http"}}
    )
    mcp_tools = await client.get_tools()

    llm = init_chat_model(
        "gpt-4.1-nano", model_provider="openai", api_key=OPENAI_API_KEY
    )

    agent = create_react_agent(
        model=llm,
        tools=mcp_tools,
        prompt=prompt,
    )

    dp = Dispatcher()
    dp.update.middleware(RecognitionMiddleware())
    dp.include_router(router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
