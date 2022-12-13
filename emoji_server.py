import io
import json

import discord
import requests
from PIL import Image

import commands

async def on_message(client1, message, prefix, command):
    if message.content.startswith(prefix):
        if command.startswith("break "):
            await commands.total_break(message, command)

        elif command.startswith("build "):
            await commands.total_build(message, command)

        elif command.startswith("daily "):
            await commands.daily_score(message, command)

        elif command.startswith("last_login "):
            await commands.last_login(message, command)

        elif command.startswith("mcavatar "):
            await commands.mcavatar(message, command)

        elif command.startswith("stack_eval "):
            await commands.stack_eval64(message, command)

        elif command.startswith("stack_eval64 "):
            await commands.stack_eval64(message, command)

        elif command.startswith("stack_eval16 "):
            await commands.stack_eval16(message, command)

        elif command.startswith("stack_eval1 "):
            await commands.stack_eval1(message, command)

        elif command.startswith("info "):
            await commands.info(client1, message, command)

        elif command.startswith("random "):
            await commands.random_commands(message, command)

        elif command.startswith("vote "):
            await commands.vote(message, command)


async def on_emoji_update(client1, guild, before, after):
    """
    絵文字のアップデートイベントがあったら反応する"""

    different = list(set(before) ^ set(after))
    notice_ch = client1.get_channel(762654494987124756)

    if different == []: #名前の変更なら
        #変更のあった絵文字を探す
        for before_emoji in before:
            after_emoji = after[before.index(before_emoji)]
            if before_emoji.name != after_emoji.name:
                break

        before_emoji_name = before_emoji.name.replace("_", "\_")
        after_emoji_name = after_emoji.name.replace("_", "\_")

        with open("./datas/emoji_data.json", mode="r", encoding="utf-8") as f:
            emoji_data_dict = json.load(f)

        created_user_id = emoji_data_dict[f"{before_emoji.id}"]
        created_user = await client1.fetch_user(created_user_id)

        embed = discord.Embed(
            title="絵文字名前変更",
            description=f"{created_user}作成の**:{before_emoji_name}:**の名前が**:{after_emoji_name}:**に変更されました",
            color=0x00ffff
        )
        await notice_ch.send(embed=embed)

    else:
        if len(before) < len(after): #作成なら
            emoji = await guild.fetch_emoji(different[0].id)
            emoji_name = emoji.name.replace("_", "\_")
            user = client1.get_user(emoji.user.id)

            with open("./datas/emoji_data.json", mode="r", encoding="utf-8") as f:
                emoji_data_dict = json.load(f)
            emoji_data_dict[f"{emoji.id}"] = user.id
            emoji_data_json = json.dumps(emoji_data_dict, indent=4)
            with open("./datas/emoji_data.json", mode="w", encoding="utf-8") as f:
                f.write(emoji_data_json)

            res = requests.get(f"{emoji.url}")
            image = io.BytesIO(res.content)
            image.seek(0)
            emoji_ = Image.open(image)
            emoji_.save(f"./emojis/{emoji.id}.png")

            if different[0].animated: #アニメ絵文字なら
                description = f"{user}によりアニメ絵文字: **:{emoji_name}:**が作成されました"
            else:
                description = f"{user}により**:{emoji_name}:**({emoji})が作成されました"
            embed = discord.Embed(
                title="絵文字作成",
                description=description,
                color=0x00ff00
            )
            await notice_ch.send(embed=embed)

        elif len(before) > len(after): #削除なら
            emoji_name = different[0].name.replace("_", "\_")

            with open("./datas/emoji_data.json", mode="r", encoding="utf-8") as f:
                emoji_data_dict = json.load(f)

            created_user_id = emoji_data_dict[f"{different[0].id}"]
            created_user = await client1.fetch_user(created_user_id)
            del emoji_data_dict[f"{different[0].id}"]

            emoji_data_json = json.dumps(emoji_data_dict, indent=4)
            with open("./datas/emoji_data.json", mode="w", encoding="utf-8") as f:
                f.write(emoji_data_json)

            embed = discord.Embed(
                title="絵文字削除",
                description=f"{created_user}作成の**:{emoji_name}:**が削除されました",
                color=0xff0000
            )
            await notice_ch.send(embed=embed)