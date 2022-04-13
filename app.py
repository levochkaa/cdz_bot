import os

import mesh
import django
from django.conf import settings
from aiogram.types import InputFile
from django.template import Template, Context
from aiogram import Bot, Dispatcher, executor, types

from dotenv import load_dotenv
load_dotenv()

TEMPLATES = [{'BACKEND': 'django.template.backends.django.DjangoTemplates'}]
settings.configure(TEMPLATES=TEMPLATES)
django.setup()
bot = Bot(os.environ['TOKEN'])
dp = Dispatcher(bot)
template = """
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Ответы для {{ user_id }}</title>
    <style>
        html {
            font-family: -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,"Noto Sans",sans-serif,"Apple Color Emoji","Segoe UI Emoji","Segoe UI Symbol","Noto Color Emoji";
            font-size: 16px;
            font-weight: 400;
            line-height: 1.5;
            -webkit-text-size-adjust: 100%;
            background: black;
            color: #666;
        }
        body {
            display: block;
            margin: 8px;
            background: black;
            border-radius: 15px;
        }
        p {
            display: block;
            margin-block-start: 1em;
            margin-block-end: 1em;
            margin-inline-start: 0;
            margin-inline-end: 0;
            margin: 0 0 20px 0;
        }
        hr {
            margin: 0 0 20px 0;
            text-align: inherit;
            display: block;
            unicode-bidi: isolate;
            margin-block-start: 0.5em;
            margin-block-end: 0.5em;
            margin-inline-start: auto;
            margin-inline-end: auto;
            overflow: hidden;
            border-style: inset;
            border-width: 1px;
        }
        .uk-card{
            border-radius: 15px;
            box-sizing: border-box;
            width: 100%;
            max-width: 100%;
            display: flow-root;
            padding: 30px 30px;
            box-shadow: 0 5px 15px rgba(255,255,255,.08);
        }
        .uk-container {
            display: flow-root;
            box-sizing: content-box;
            max-width: 1200px;
            margin-left: auto;
            margin-right: auto;
            padding-left: 30px;
            padding-right: 30px;
            min-width: 640px;
        }
        .uk-divider-icon {
            position: relative;
            height: 10px;
            background-image: url(data:image/svg+xml;charset=UTF-8,%3Csvg%20width%3D%2220%22%20height%3D%2220%22%20viewBox%3D%220%200%2020%2020%22%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%3E%0A%20%20%20%20%3Ccircle%20fill%3D%22none%22%20stroke%3D%22%23e5e5e5%22%20stroke-width%3D%222%22%20cx%3D%2210%22%20cy%3D%2210%22%20r%3D%227%22%20%2F%3E%0A%3C%2Fsvg%3E%0A);
            background-repeat: no-repeat;
            background-position: 50% 50%;
        }
    </style>
</head>
<body>
    <div id="tasks" class="uk-container">
        {% for task, ans in tasks %}
        <hr class="uk-divider-icon" style="visibility: hidden">
        <div class="uk-card" style="background: white;">
            <p>{{ task }}</p>
            <br>
            <p><b>Ответ:</b></p>
            <p>{{ ans }}</p>
        </div>
        <hr class="uk-divider-icon" style="visibility: hidden">
        {% endfor %}
    </div>
</body>
</html>
"""
t = Template(template)

@dp.message_handler(content_types='text')
async def send_text(message: types.Message):
    try:
        answers = mesh.get_answers(message.text)
        for task, ans in answers:
            await message.answer(f"{task}\n"
                                 f"Ответ: {ans}")
        c = Context({"user_id": message.from_user.id,
                     "tasks": answers})
        with open('index.html', 'w') as i:
            i.write(t.render(c))
        await message.answer_document(InputFile('index.html'),
                                      caption="ответики сайтиком")
    except Exception as e:
        await message.answer("типо ошибка но ответы мб норм")
        await bot.send_message(845543257, f"Bug Report:\n"
                                          f"{e}\n"
                                          f"{message.text}\n"
                                          f"@{message.from_user.username}")


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    executor.start_polling(dp)
