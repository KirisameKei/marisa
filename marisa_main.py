import datetime
import json
import os
import random
import re
import traceback

import discord
import requests
from discord.ext import tasks

import anzu_server
import common
import custom_commands_exe
import emoji_server
import iroha_server
import kei_server
import limited_time
import muhou
import pikachu_server
import server_log
import tetsuya_server
import wake_up

os.chdir(os.path.dirname(os.path.abspath(__file__)))
client1 = discord.Client(intents=discord.Intents.all())

where_from = os.getenv("where_from")
error_notice_webhook_url = os.getenv("error_notice_webhook")

def unexpected_error(msg=None):
    """
    予期せぬエラーが起きたときの対処
    エラーメッセージ全文と発生時刻を通知"""

    try:
        if msg is not None:
            content = (
                f"{msg.author}\n"
                f"{msg.content}\n"
                f"{msg.channel.name}\n"
            )
        else:
            content = ""
    except:
        unexpected_error()
        return

    now = datetime.datetime.now().strftime("%H:%M") #今何時？
    error_msg = f"```\n{traceback.format_exc()}```" #エラーメッセージ全文
    error_content = {
        "content": "<@523303776120209408>", #けいにメンション
        "avatar_url": "https://cdn.discordapp.com/attachments/644880761081561111/703088291066675261/warning.png",
        "embeds": [ #エラー内容・発生時間まとめ
            {
                "title": "エラーが発生しました",
                "description": content + error_msg,
                "color": 0xff0000,
                "footer": {
                    "text": now
                }
            }
        ]
    }
    requests.post(error_notice_webhook_url, json.dumps(error_content), headers={"Content-Type": "application/json"}) #エラーメッセをウェブフックに投稿


@client1.event
async def on_ready():
    try:
        loop_task.start()
        change_status.start()
        kikaku_announcement.start()
        login_notice_ch = client1.get_channel(595072269483638785)
        with open("./datas/version.txt", mode="r", encoding="utf-8") as f:
            version = f.read()
        await login_notice_ch.send(f"{client1.user.name}がログインしました(from: {where_from})\n{os.path.basename(__file__)}により起動\nversion: {version}")

    except:
        unexpected_error()


@client1.event
async def on_message(message):
    if message.content == "/bot_stop":
        if message.guild is None:
            await message.channel.send("このコマンドはけいの実験サーバでのみ使用可能です")
            return
        kei_ex_guild = client1.get_guild(585998962050203672)
        if message.guild != kei_ex_guild:
            await message.channel.send("このコマンドはけいの実験サーバでのみ使用可能です")
            return
        can_bot_stop_role = kei_ex_guild.get_role(707570554462273537)
        if not can_bot_stop_role in message.author.roles:
            await message.channel.send("何様のつもり？")
            doM_role = message.guild.get_role(616212704818102275)
            await message.author.add_roles(doM_role)
            return

        await client1.close()
        now = datetime.datetime.now().strftime(r"%Y年%m月%d日　%H:%M")
        stop_msg = f"{message.author.mention}により{client1.user.name}が停止させられました"
        main_content = {
            "username": "BOT STOP",
            "avatar_url": "https://cdn.discordapp.com/attachments/644880761081561111/703088291066675261/warning.png",
            "content": "<@523303776120209408>",
            "embeds": [
                {
                    "title": "botが停止させられました",
                    "description": stop_msg,
                    "color": 0xff0000,
                    "footer": {
                        "text": now
                    }
                }
            ]
        }
        requests.post(error_notice_webhook_url, json.dumps(main_content), headers={"Content-Type": "application/json"}) #エラーメッセをウェブフックに投稿
        return

    if client1.user in message.mentions:
        fileplace = discord.__file__.replace("\\", "\\\\").replace("_", "\_")
        await message.channel.send(f"{where_from}\n{os.path.basename(__file__)}\n{discord.__version__}\n{fileplace}")

    try:
        if message.guild is not None:
            if message.guild.id == 585998962050203672: #けい鯖なら
                await server_log.server_log_on_message(client1, message)

        if message.content.startswith("#") or message.content.startswith("//") or \
            (message.clean_content.startswith("/*") and message.clean_content.endswith("*/")):
            return

        if re.compile(r"https://(ptb.|canary.|)discord(app|).com/channels/").search(message.content):
            url_filter = re.split(r"https://(ptb.|canary.|)discord(app|).com/channels/", message.content)
            for url in url_filter:
                if re.search(r"\d+/\d+/\d+", url):
                    await common.quote_message(client1, message, url) #メッセリンク展開用関数

        if message.guild is None:
            if message.author.id != client1.user.id:
                if message.channel == message.author.dm_channel:
                    await dm(client1, message)
            return
        #以下DMでは反応しない

        command = None
        if message.guild is not None:
            with open("./datas/custom_prefix.json", mode="r", encoding="utf-8") as f:
                custom_frefix_dict = json.load(f)
            try:
                prefix = custom_frefix_dict[f"{message.guild.id}"]
            except KeyError:
                if not message.guild is None:
                    custom_frefix_dict[f"{message.guild.id}"] = "/"
                    custom_frefix_json = json.dumps(custom_frefix_dict, indent=4, ensure_ascii=False)
                    with open("./datas/custom_prefix.json", mode="w", encoding="utf-8") as f:
                        f.write(custom_frefix_json)
                prefix = "/"

        if message.content.startswith(prefix):
            prefix_length = len(prefix)
            command = message.content[prefix_length:]
            if command[0] == " ":
                command = command[1:]

        if "おはよう" in message.content or "こんにちは" in message.content or\
            "こんばんは" in message.content or "おやすみ" in message.content or "ありがとう" in message.content:
            await common.greeting(message)

        if message.content == "少し放置" or message.content == "学校終わって三条":
            await common.end_reaction(message)

        if message.content.startswith(prefix):
            with open("./datas/custom_commands.json", mode="r", encoding="utf-8") as f:
                custom_commands_dict = json.load(f)

            if f"{message.guild.id}" in custom_commands_dict.keys():
                if not message.author.bot:
                    custom_commands = custom_commands_dict[f"{message.guild.id}"]
                    await custom_commands_exe.on_message(message, custom_commands, command)

            form_tuple = (
                "report",
                "failure",
                "idea",
                "opinion",
                "donation",
                "inquiry",
                "formal",
                "informal",
                "form"
            )
            if command in form_tuple:
                await common.form_link(message, command)

            elif command == "new_func":
                await common.new_function(client1, message)

            elif command == "bug_report":
                await common.bug_report(client1, message)

            elif command.startswith("prefix "):
                await common.change_prefix(message)

            elif command.startswith("set_notice_ch"):
                await common.set_notice_ch(message, client1, command)

            elif command == "check_notice_ch":
                await common.check_notice_ch(message)

            elif command.startswith("help"):
                if prefix != "/":
                    await common.help(message, command, client1)

        if message.content.startswith("/help"): #カスタムプレフィックスを忘れた人の救済用
            await common.help(message, message.content.replace("/", ""), client1)

        if message.guild.id == 585998962050203672: #けいの実験サーバ
            await kei_server.on_message(client1, message, prefix, command)

        elif message.guild.id == 587909823665012757: #無法地帯
            await muhou.on_message(client1, message, prefix, command)

        elif message.guild.id == 735632039050477649: #第2絵文字サーバ
            await emoji_server.on_message(client1, message, prefix, command)

        elif message.guild.id in (876143248471621652, 660445544296218650): #いろは鯖なら
            await iroha_server.on_message(client1, message, prefix, command)

        elif message.guild.id in (659375053707673600, 863367920612802610): #あんず鯖なら
            await anzu_server.on_message(client1, message, prefix, command)

        elif message.guild.id == 812096632714690601: #起きてー鯖なら
            await wake_up.on_message(client1, message, prefix, command)

        elif message.guild.id == 985092628594978867: #ピカチュウ鯖(プロセカ用鯖)なら
            await pikachu_server.on_message(client1, message, prefix, command)

        elif message.guild.id == 731437075622133861: #徹夜太郎鯖なら
            await tetsuya_server.on_message(client1, message, prefix, command)

    except:
        unexpected_error(msg=message)


@client1.event
async def on_message_delete(message):
    try:
        if message.guild is None:
            return

        if message.guild.id == 585998962050203672: #けい鯖なら
            await server_log.server_log_on_message_delete(client1, message)

    except:
        unexpected_error(msg=message)


@client1.event
async def on_message_edit(before, after):
    try:
        if before.guild is None:
            return

        if before.guild.id == 585998962050203672: #けい鯖なら
            await server_log.server_log_on_message_update(client1, before, after)

    except:
        unexpected_error(msg=after)


@client1.event
async def on_guild_join(guild):
    try:
        await common.on_guild_join(client1, guild)

    except:
        unexpected_error()


@client1.event
async def on_guild_remove(guild):
    try:
        await common.on_guild_remove(client1, guild)

    except:
        unexpected_error()


@client1.event
async def on_member_join(member):
    try:
        await common.on_member_join(client1, member)

    except:
        unexpected_error()


@client1.event
async def on_member_remove(member):
    try:
        await common.on_member_remove(client1, member)

    except:
        unexpected_error()


@client1.event
async def on_member_update(before, after):
    try:
        if before.guild.id == 585998962050203672:
            await kei_server.on_member_update(before, after, client1)

    except:
        unexpected_error()


@client1.event
async def on_guild_channel_create(channel):
    try:
        guild_name = channel.guild.name

        if isinstance(channel, discord.CategoryChannel):
            ch_description = f"{guild_name}でカテゴリチャンネル「{channel.name}」が作成されました"
        elif isinstance(channel, discord.VoiceChannel):
            ch_description = f"{guild_name}でボイスチャンネル「{channel.name}」が作成されました"
        else:
            ch_description = f"{guild_name}でテキストチャンネル「{channel.name}」が作成されました\n{channel.mention}"
        
        now = datetime.datetime.now().strftime(r"%Y/%m/%d-%H:%M")
        ch_embed = discord.Embed(title="チャンネル作成", description=ch_description, color=0xfffffe)
        ch_embed.set_footer(text=now, icon_url=channel.guild.icon_url)
        ch_notice_ch = client1.get_channel(682732694768975884)
        await ch_notice_ch.send(embed=ch_embed)

        if isinstance(channel, discord.CategoryChannel):
            return

        if channel.guild.id == 585998962050203672: #けい鯖なら
            with open("./datas/channels_id.json", mode="r", encoding="utf-8") as f:
                channels_id_dict = json.load(f)

            log_server = client1.get_guild(707794528848838676)
            new_ch = await log_server.create_text_channel(name=channel.name)
            channels_id_dict[f"{channel.id}"] = new_ch.id

            channels_id_json = json.dumps(channels_id_dict, indent=4)
            with open("./datas/channels_id.json", mode="w", encoding="utf-8") as f:
                f.write(channels_id_json)

    except:
        unexpected_error()


@client1.event
async def on_guild_channel_delete(channel):
    try:
        guild_name = channel.guild.name

        if isinstance(channel, discord.CategoryChannel):
            channel_type = "カテゴリチャンネル"
        elif isinstance(channel, discord.VoiceChannel):
            channel_type = "ボイスチャンネル"
        else:
            channel_type = "テキストチャンネル"

        now = datetime.datetime.now().strftime(r"%Y/%m/%d-%H:%M")
        ch_description = f"{guild_name}で{channel_type}「{channel.name}」が削除されました"
        ch_embed = discord.Embed(title="チャンネル削除", description=ch_description, color=0xff0000)
        ch_embed.set_footer(text=now, icon_url=channel.guild.icon_url)
        ch_notice_ch = client1.get_channel(682732694768975884)
        await ch_notice_ch.send(embed=ch_embed)

        if channel.guild.id == 585998962050203672: #けい鯖なら
            with open("./datas/channels_id.json", mode="r", encoding="utf-8") as f:
                channels_id_dict = json.load(f)
            try:
                del channels_id_dict[f"{channel.id}"]
            except KeyError:
                pass
            else:
                channels_id_json = json.dumps(channels_id_dict, indent=4)
                with open("./datas/channels_id.json", mode="w", encoding="utf-8") as f:
                    f.write(channels_id_json)

    except:
        unexpected_error()


@client1.event
async def on_guild_channel_update(before, after):
    try:
        guild_name = before.guild.name

        if before.name != after.name:
            if isinstance(before, discord.CategoryChannel):
                ch_description = f"{guild_name}のカテゴリチャンネル「{before.name}」が「{after.name}」に変更されました"
            elif isinstance(before, discord.VoiceChannel):
                ch_description = f"{guild_name}のボイスチャンネル「{before.name}」が「{after.name}」に変更されました"
            else:
                ch_description = f"{guild_name}のテキストチャンネル「{before.name}」が「{after.name}」に変更されました\n{after.mention}"
            
            now = datetime.datetime.now().strftime(r"%Y/%m/%d-%H:%M")
            ch_embed = discord.Embed(title="チャンネルアップデート", description=ch_description, color=0x0000ff)
            ch_embed.set_footer(text=now, icon_url=before.guild.icon_url)
            ch_notice_ch = client1.get_channel(682732694768975884)
            await ch_notice_ch.send(embed=ch_embed)

        if isinstance(before, discord.CategoryChannel):
            return

        if before.guild.id == 585998962050203672: #けい鯖なら
            with open("./datas/channels_id.json", mode="r", encoding="utf-8") as f:
                channels_id_dict = json.load(f)
            try:
                log_channel_id = channels_id_dict[f"{before.id}"]
            except KeyError:
                notice_ch = client1.get_channel(636359382359080961) #python開発やることリスト
                await notice_ch.send(f"<@523303776120209408>\n{guild_name}:{before.name}→{after.name}\n{after.mention}")
            else:
                log_channel = client1.get_channel(log_channel_id)
                await log_channel.edit(name=after.name)

    except:
        unexpected_error()


@client1.event
async def on_reaction_add(reaction, user):
    try:
        if reaction.message.guild.id == 585998962050203672: #けいの実験サーバ
            await kei_server.on_reaction_add(client1, reaction, user)

    except:
        unexpected_error()


@client1.event
async def on_raw_reaction_add(payload):
    try:
        if payload.guild_id == 585998962050203672: #けい鯖
            await kei_server.on_raw_reaction_add(client1, payload)

    except:
        unexpected_error()


@client1.event
async def on_guild_emojis_update(guild, before, after):
    try:
        if guild.id == 735632039050477649:
            await emoji_server.on_emoji_update(client1, guild, before, after)

    except:
        unexpected_error()


@tasks.loop(seconds=60)
async def loop_task():
    try:
        await client1.wait_until_ready()
        now = datetime.datetime.now()

        #毎日0時0分 日付変更通知と統計表示
        if now.hour == 0 and now.minute == 0:
            await kei_server.count_members(client1)
            await kei_server.change_date(client1)

        #毎日0時0分 mcidとuuidの紐づけjsonをクリア
        if now.hour == 4 and now.minute == 30:
            clear_cache()

        #毎日9時10分 整地鯖への投票リンク
        if now.hour == 9 and now.minute == 10:
            await kei_server.jms_notice(client1)

        #毎日12時 無法地帯鯖アイコン変更
        if now.hour == 12 and now.minute == 0:
            await muhou.change_guild_icon(client1)

        #毎日18時15分 新たに21億以上掘った人がいるかチェック
        if now.hour == 18 and now.minute == 15:
            await kei_server.check_new_int_role_getter(client1)

        #毎日23時59分 kei_3104の日間整地量を表示
        if now.hour == 23 and now.minute == 59:
            await kei_server.kei_daily_score(client1)

        #毎週日曜日3時0分 しりとりチャンネルリセット
        if now.weekday() == 6 and now.hour == 3 and now.minute == 0:
            await kei_server.shiritori_reset(client1)

        #毎週月曜日3時15分 物語保存
        if now.weekday() == 0 and now.hour == 3 and now.minute == 15:
            await kei_server.record_story(client1)

        #毎週水曜日4時35分 MCIDの更新を検知
        if now.weekday() == 2 and now.hour == 4 and now.minute == 35:
            await kei_server.check_mcid_exist_now(client1)

        #毎年6月28日0時0分 魔理沙bot誕生日記念プレゼント企画開始通知
        if now.month == 6 and now.day == 28 and now.hour == 0 and now.minute == 0:
            await kei_server.marichan_birthday(client1)

        #毎年6月28日23時59分 魔理沙bot誕生日記念プレゼント企画終了通知
        if now.month == 6 and now.day == 28 and now.hour == 23 and now.minute == 59:
            await kei_server.marichan_birthday_finish(client1)

    except:
        unexpected_error()


@tasks.loop(seconds=600)
async def change_status():
    try:
        await client1.wait_until_ready()

        presense_list = [
            "users",
            "channels",
            "guilds",
            "https://discord.gg/nrvMKBT",
            "某MEE6より優秀",
            "けいが作成！"
        ]
        presense = random.choice(presense_list)
        if presense == "users":
            presense = f"{len(client1.users)}人を監視中"

        if presense == "channels":
            i = 0
            for guild in client1.guilds:
                for ch in guild.channels:
                    i += 1
            presense = f"{i}チャンネルを監視中"

        if presense == "guilds":
            presense = f"{len(client1.guilds)}サーバを監視中"

        game = discord.Game(presense)
        try:
            await client1.change_presence(status=discord.Status.online, activity=game)
        except ConnectionResetError:
            pass

    except:
        unexpected_error()


@tasks.loop(seconds=60)
async def kikaku_announcement():
    try:
        await client1.wait_until_ready()
        now = datetime.datetime.now()

        #if now.month == 7 and now.day == 31 and now.hour == 0 and now.minute == 10:
        if now.hour == 0 and now.minute == 10:
            #await limited_time.simple_kikaku_result(client1) #応募者の中からn人選ぶシンプルな企画
            #await limited_time.complex_kikaku_result(client1) #総額いくらを当選人数人でランダムに分配する企画
            await limited_time.seichi_taikai_result(client1) #整地大会用の企画
    except:
        unexpected_error()

#ーーーーここまでメイン、以下補助関数ーーーー

async def dm(client1, message):
    if message.author.bot:
        return

    send_ch = client1.get_channel(639830406270681099)
    dm_embed = discord.Embed(description=message.content)
    dm_embed.set_author(name=f"{message.author.name}\n{message.author.id}", icon_url=message.author.display_avatar.url)
    await send_ch.send(embed=dm_embed)


def clear_cache():
    with open("./datas/mcid_uuid_cache.json", mode="w", encoding="utf-8") as f:
        f.write(r"{}")


client1.run(os.getenv("discord_bot_token_1"))