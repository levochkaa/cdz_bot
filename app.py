import os

import re
import mesh
import django
from dotenv import load_dotenv
from django.conf import settings
from django.template import Template, Context
from aiogram import Bot, Dispatcher, executor, types

load_dotenv()
settings.configure(TEMPLATES=[{'BACKEND': 'django.template.backends.django.DjangoTemplates'}])
django.setup()
bot = Bot(os.environ['TOKEN'])
dp = Dispatcher(bot)
template = Template("""
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
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
        img {
            margin-bottom: 30px
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
            padding-left: 30px;
            padding-right: 30px;
            min-width: 640px;
        }
    </style>
</head>
<body>
    <div class="cards">
        {% for item in tasks %}
        <div class="card">
            <p>{{ item.task }}</p>
            {% if item.photo != None %}
                <img src="{{ item.photo }}">
            {% endif %}
            <p><b>Ответ:</b></p>
            <p>{{ item.ans }}</p>
        </div>
        {% endfor %}
    </div>
</body>
</html>
""")

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer("кидай ссылку")

@dp.message_handler(content_types='text')
async def send_text(message: types.Message):
    if re.search(r"https://uchebnik.mos.ru/[\S][^>]+", message.text) == None:
        return await message.answer("это не ссылка")
    try:
        answers, fixed_answers = mesh.get_answers(message.text), []
        for task, ans in answers:
            r = re.search(r"https://uchebnik.mos.ru/[\S][^>]+", task)
            ans = ans if ans != "" else "сорян, ответа нет, пиши сам"
            if r == None:
                await message.answer(f"{task}\n"
                                    f"Ответ: {ans}")
                fixed_answers.append({
                    "task": task,
                    "ans": ans,
                    "photo": None
                })
            else:
                start = r.span()[0]
                await message.answer_photo(photo=f"{task[start:-2]}",
                                           caption=f"{task[:start - 1]}\n"
                                           f"Ответ: {ans}")
                fixed_answers.append({
                    "task": task[:start - 1],
                    "ans": ans,
                    "photo": task[start:-2]
                })
        with open('site.html', 'w') as site:
            site.write(template.render(Context({"tasks": fixed_answers})))
        await message.answer_document(types.InputFile('site.html'),
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
