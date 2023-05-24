import datetime
import io
import json

import discord
import requests
import PIL
from PIL import Image

async def server_log_on_message(client1, message):
    """
    けい鯖、いろは鯖でメッセージが投稿されたときの関数"""

    with open("./datas/channels_id.json", mode="r", encoding="utf-8") as f:
        channels_id_dict = json.load(f)
    try:
        log_channel_id = channels_id_dict[f"{message.channel.id}"]
    except KeyError:
        notice_ch = client1.get_channel(636359382359080961) #python開発やることリスト
        await notice_ch.send(f"<@523303776120209408>\n{message.channel.mention}の辞書登録あく！")
        return

    log_channel = client1.get_channel(log_channel_id)
    if message.attachments or message.content or message.embeds:
        message_embed = discord.Embed(description=message.content, color=0xfffffe)
        message_embed.set_author(name=f"{message.author.name} ({message.id})", icon_url=message.author.avatar.url)
        message_embed.set_footer(text=datetime.datetime.now().strftime(r"%Y/%m/%d-%H:%M"))
        if message.attachments:
            res = requests.get(message.attachments[0].url)
            image = io.BytesIO(res.content)
            image.seek(0)
            try:
                image = Image.open(image)
            except PIL.UnidentifiedImageError:
                return
            image.save("attachment.png")
            f = discord.File("attachment.png", filename="attachment.png")
            message_embed.set_image(url="attachment://attachment.png")

        if message.content or message.attachments:
            try:
                await log_channel.send(file=f, embed=message_embed)
            except AttributeError:
                await log_channel.send(embed=message_embed)

        if len(message.attachments) >= 2:
            for attachment in message.attachments[1:]:
                res = requests.get(attachment.url)
                image = io.BytesIO(res.content)
                image.seek(0)
                image = Image.open(image)
                image.save("attachment.png")
                f = discord.File("attachment.png", filename="attachment.png")
                message_embed = discord.Embed(color=0xfffffe).set_image(url="attachment://attachment.png")
                await log_channel.send(file=f, embed=message_embed)

        for embed in message.embeds:
            await log_channel.send(embed=embed)


async def server_log_on_message_delete(client1, message):
    """
    けい鯖、いろは鯖でメッセージが削除されたときの関数"""

    with open("./datas/channels_id.json", mode="r", encoding="utf-8") as f:
        channels_id_dict = json.load(f)
    try:
        log_channel_id = channels_id_dict[f"{message.channel.id}"]
    except KeyError:
        notice_ch = client1.get_channel(636359382359080961) #python開発やることリスト
        await notice_ch.send(f"<@523303776120209408>\n{message.channel.mention}の辞書登録あく！")
        return

    log_channel = client1.get_channel(log_channel_id)
    if message.attachments or message.embeds or message.content:
        message_embed = discord.Embed(description=message.content, color=0xff0000)
        message_embed.set_author(name=f"{message.author.name} ({message.id})", icon_url=message.author.avatar.url)
        message_embed.set_footer(text=datetime.datetime.now().strftime(r"%Y/%m/%d-%H:%M"))
        if message.attachments:
            res = requests.get(message.attachments[0].url)
            image = io.BytesIO(res.content)
            image.seek(0)
            image = Image.open(image)
            image.save("attachment.png")
            f = discord.File("attachment.png", filename="attachment.png")
            message_embed.set_image(url="attachment://attachment.png")

        if message.content or message.attachments:
            try:
                await log_channel.send(file=f, embed=message_embed)
            except AttributeError:
                await log_channel.send(embed=message_embed)

        if len(message.attachments) >= 2:
            for attachment in message.attachments[1:]:
                res = requests.get(attachment.url)
                image = io.BytesIO(res.content)
                image.seek(0)
                image = Image.open(image)
                image.save("attachment.png")
                f = discord.File("attachment.png", filename="attachment.png")
                message_embed = discord.Embed(color=0xff0000).set_image(url="attachment://attachment.png")
                await log_channel.send(file=f, embed=message_embed)

        for embed in message.embeds:
            await log_channel.send(embed=embed, content="削除されたembed")


async def server_log_on_message_update(client1, before, after):
    """
    けい鯖、HJK、いろは鯖でメッセージが編集されたときの関数"""

    with open("./datas/channels_id.json", mode="r", encoding="utf-8") as f:
        channels_id_dict = json.load(f)
    try:
        log_channel_id = channels_id_dict[f"{before.channel.id}"]
    except KeyError:
        notice_ch = client1.get_channel(636359382359080961) #python開発やることリスト
        await notice_ch.send(f"<@523303776120209408>\n{before.channel.mention}の辞書登録あく！")
        return

    if before.content == after.content and before.embeds == after.embeds:
        return

    log_channel = client1.get_channel(log_channel_id)
    if before.attachments or before.content or before.embeds:
        message_embed = discord.Embed(description=f"**編集前**\n{before.content}", color=0x0000ff)
        message_embed.set_author(name=f"{before.author.name} ({before.id})", icon_url=before.author.avatar.url)
        message_embed.set_footer(text=datetime.datetime.now().strftime(r"%Y/%m/%d-%H:%M"))
        if before.attachments:
            res = requests.get(before.attachments[0].url)
            image = io.BytesIO(res.content)
            image.seek(0)
            image = Image.open(image)
            image.save("attachment.png")
            f = discord.File("attachment.png", filename="attachment.png")
            message_embed.set_image(url="attachment://attachment.png")

        if before.content or before.attachments:
            try:
                await log_channel.send(file=f, embed=message_embed)
            except AttributeError:
                await log_channel.send(embed=message_embed)

        if len(before.attachments) >= 2:
            for attachment in before.attachments[1:]:
                res = requests.get(attachment.url)
                image = io.BytesIO(res.content)
                image.seek(0)
                image = Image.open(image)
                image.save("attachment.png")
                f = discord.File("attachment.png", filename="attachment.png")
                message_embed = discord.Embed(color=0x0000ff).set_image(url="attachment://attachment.png")
                await log_channel.send(file=f, embed=message_embed)

        for embed in before.embeds:
            await log_channel.send(content="編集前のembed", embed=embed)

    if after.attachments or after.content or after.embeds:
        message_embed = discord.Embed(description=f"**編集後**\n{after.content}", color=0x00ff00)
        message_embed.set_author(name=f"{after.author.name} ({after.id})", icon_url=after.author.avatar.url)
        message_embed.set_footer(text=datetime.datetime.now().strftime(r"%Y/%m/%d-%H:%M"))
        if after.attachments:
            res = requests.get(after.attachments[0].url)
            image = io.BytesIO(res.content)
            image.seek(0)
            image = Image.open(image)
            image.save("attachment.png")
            f = discord.File("attachment.png", filename="attachment.png")
            message_embed.set_image(url="attachment://attachment.png")

        if after.content or after.attachments:
            try:
                await log_channel.send(file=f, embed=message_embed)
            except AttributeError:
                await log_channel.send(embed=message_embed)

        if len(after.attachments) >= 2:
            for attachment in after.attachments[1:]:
                res = requests.get(attachment.url)
                image = io.BytesIO(res.content)
                image.seek(0)
                image = Image.open(image)
                image.save("attachment.png")
                f = discord.File("attachment.png", filename="attachment.png")
                message_embed = discord.Embed(color=0x00ff00).set_image(url="attachment://attachment.png")
                await log_channel.send(file=f, embed=message_embed)

        for embed in after.embeds:
            await log_channel.send(content="編集後のembed", embed=embed)