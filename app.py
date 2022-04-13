import mesh
import django
from django.conf import settings
from aiogram.types import InputFile
from django.template import Template, Context
from aiogram import Bot, Dispatcher, executor, types

settings.configure(TEMPLATES=[{'BACKEND': 'django.template.backends.django.DjangoTemplates'}])
django.setup()
bot = Bot("2119600702:AAGkGcOHqh9iO8BnGiVc7yS388LAbHQk2X4")
dp = Dispatcher(bot)
template = """
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>ответики</title>
    <style>
        html {
            font-family: -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,"Noto Sans",sans-serif,"Apple Color Emoji","Segoe UI Emoji","Segoe UI Symbol","Noto Color Emoji";
            font-size: 16px;
            font-weight: 400;
            line-height: 1.5;
            -webkit-text-size-adjust: 100%;
            background: black;
        }
        p {
            display: block;
            margin-block-start: 1em;
            margin-block-end: 1em;
            margin-inline-start: 0;
            margin-inline-end: 0;
            margin: 0 0 20px 0;
        }
        .card {
            border-radius: 15px;
            box-sizing: border-box;
            width: 100%;
            max-width: 100%;
            display: flow-root;
            padding: 30px 30px;
            margin-bottom: 30px;
            margin-top: 30px;
            box-shadow: 0 5px 15px rgba(255,255,255,.08);
            background: white;
        }
        .cards {
            display: flow-root;
            box-sizing: content-box;
            max-width: 1200px;
            margin-left: auto;
            margin-right: auto;
            min-width: 640px;
        }
    </style>
</head>
<body>
    <div class="cards">
        {% for task, ans in tasks %}
        <div class="card">
            <p>{{ task }}</p>
            <br>
            <p><b>Ответ:</b></p>
            <p>{{ ans }}</p>
        </div>
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
        c = Context({"tasks": answers})
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
