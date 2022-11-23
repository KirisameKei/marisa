import random

import commands

async def on_message(client1, message, prefix, command):
    if message.author.name == "MEE6":
        await anti_mee6(message)

    if message.content.startswith(prefix):
        if command.startswith("break "):
            await commands.total_break(message, command)

        elif command.startswith("build "):
            await commands.total_build(message, command)

        elif command.startswith("daily"):
            await commands.daily_score(message, command)

        elif command.startswith("last_login "):
            await commands.last_login(message)

        elif command.startswith("mcavatar "):
            await commands.mcavatar(message)

        elif command.startswith("stack_eval "):
            await commands.stack_eval64(message)

        elif command.startswith("stack_eval64 "):
            await commands.stack_eval64(message)

        elif command.startswith("stack_eval16 "):
            await commands.stack_eval16(message)

        elif command.startswith("stack_eval1 "):
            await commands.stack_eval1(message)

        elif command.startswith("info "):
            await commands.info(client1, message)

        elif command.startswith("random "):
            await commands.random_commands(message)

        elif command.startswith("weather "):
            await commands.weather(message)

        elif command.startswith("vote "):
            await commands.vote(message)

        elif command.startswith("name "):
            await commands.name(message)


async def change_guild_icon(client1):
    guild = client1.get_guild(587909823665012757)
    pict_list = [
        "kero.png",
        "rem.png",
        "anan_1919.png",
        "poop.png",
        "who.jpg",
        "anzu_pic1.jpg",
        "anzu_pic2.jpg",
        "puha_RIM.jpg",
        "kawaii.png"
    ]
    pict = random.choice(pict_list)
    img = open(f"./pictures/{pict}", mode="rb").read()
    await guild.edit(icon=img)


async def anti_mee6(message):
    await message.add_reaction("🖕")
    anti_message_list = [
        ":middle_finger:",
        "少し静かにしていただけますか？",
        "ちょっと黙っててもらっていいですか？",
        "お引き取りください",
        "f*ck",
        "たいそうにぎやかなご様子でいらっしゃいますところまことに恐縮でございますが、ご逝去あそばしていただければ幸甚に存じます"
    ]
    await message.channel.send(f"{message.author.mention}\n{random.choice(anti_message_list)}")