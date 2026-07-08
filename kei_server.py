import asyncio
import datetime
import json
import os
import random
import re

import discord
import jaconv
import MySQLdb
import requests

import commands
import kei_server_commands
import limited_time

async def on_member_join(client1, member):
    """
    けい鯖に新規メンバーが来た時用の関数
    以前に入っていたかを検知し入っていなければ初期データを設定する
    新規役職を付与する"""

    with open("./datas/user_data.json", mode="r", encoding="utf-8") as f:
        user_data_dict = json.load(f)

    first_join = False
    try:
        user_data = user_data_dict[f"{member.id}"]
    except KeyError:
        user_data_dict[f"{member.id}"] = {"ban": False, "role": [], "mcid": [], "point": 0, "speak": 0}
        user_data_json = json.dumps(user_data_dict, indent=4)
        with open("./datas/user_data.json", mode="w", encoding="utf-8") as f:
            f.write(user_data_json)
        first_join = True
    else:
        join_leave_notice_ch = client1.get_channel(709307324170240079)
        if user_data["ban"]:
            await member.ban(reason="事前BAN者入場のため")
            await join_leave_notice_ch.send(f"{member.mention}が本鯖に参加しようとしましたがBANされました")
            return

    new_role = member.guild.get_role(621641465105481738)
    await member.add_roles(new_role)

    infomation_ch = client1.get_channel(588224929300742154)
    info_embed = discord.Embed(title=f"🎉{member.name}さんようこそ{member.guild.name}へ！🎉", color=0xffff00)
    info_embed.add_field(
        name="はじめに",
        value="<#586000955053441039>をお読みください\n大体の流れはそこに書いてあります(botでも誘導します)",
        inline=False
    )
    info_embed.add_field(
        name="MCIDの報告",
        value=(
            "<#640833025822949387>でMCIDを報告してください\n"
            "複数のMCIDを持っている方はスペース区切り、または改行区切りで同時に登録ができます\n"
            "JE版マイクラを持っていない方は<@523303776120209408>のDMまで、個別に対応します"
        ),
        inline=False
    )
    info_embed.add_field(
        name="ルールへの同意",
        value=(
            "「はじめに」にあるルールに同意していただけるなら<#592581835343659030>で**/accept**を実行してください。\n"
            "人間であることの証明と日本語話者であることの証明が完了すれば新規役職が外れます"
        ),
        inline=False
    )
    info_embed.add_field(name="最後に", value="お楽しみください", inline=False)
    await infomation_ch.send(content=f"{member.mention}", embed=info_embed)

    if not first_join:
        if not len(user_data["role"]) == 0:
            role_name = ""
            for role_id in user_data["role"]:
                role = member.guild.get_role(role_id)
                await member.add_roles(role)
                role_name += f"{role.name}, "

            await infomation_ch.send(f"{member.name}さんは過去に以下の役職を保有していたため付与しました```\n{role_name}```")


async def on_member_remove(member):
    with open("./datas/user_data.json", mode="r", encoding="utf-8") as f:
        user_data_dict = json.load(f)

    try:
        user_data_dict[f"{member.id}"]["mcid"] = []
        user_data_dict[f"{member.id}"]["point"] = 0
        user_data_dict[f"{member.id}"]["speak"] = 0
    except KeyError:
        user_data_dict[f"{member.id}"] = {"ban": False, "role": [], "mcid": [], "point": 0, "speak": 0}

    connection = MySQLdb.connect(
        host=os.getenv("mysql_host"),
        user=os.getenv("mysql_user"),
        passwd=os.getenv("mysql_passwd"),
        db=os.getenv("mysql_db_name")
    )
    cursor = connection.cursor()
    cursor.execute(f"delete from uuids where id={member.id}")
    connection.commit()
    cursor.close()
    connection.close()

    user_data_json = json.dumps(user_data_dict, indent=4)
    with open("./datas/user_data.json", mode="w", encoding="utf-8") as f:
        f.write(user_data_json)


async def on_member_update(before, after, client1):
    if before.roles != after.roles:
        leave_role_tuple = (
            586009049259311105, #実験台
            628175600007512066, #発言禁止
            586000652464029697, #警告2
            586000502635102209, #警告1
            676414213517737995, #警備員
            707570554462273537, #bot停止権
            630778781963124786, #デバッガー
            586418283780112385, #int
            671524901655543858, #狩人
            674093583669788684, #侵入者
            616212704818102275, #ドM
        )
        with open("./datas/user_data.json", mode="r", encoding="utf-8") as f:
            user_data_dict = json.load(f)

        try:
            role_id_list = user_data_dict[f"{before.id}"]["role"]
        except KeyError:
            user_data_dict[f"{before.id}"] = {"ban": False, "role": [], "mcid": [], "point": 0, "speak": 0}
            role_id_list = user_data_dict[f"{before.id}"]["role"]
        role_id_list.clear()

        for role in after.roles:
            if role.id in leave_role_tuple:
                role_id_list.append(role.id)

        user_data_json = json.dumps(user_data_dict, indent=4)
        with open("./datas/user_data.json", mode="w", encoding="utf-8") as f:
            f.write(user_data_json)

        notice_ch = client1.get_channel(585999375952642067)
        int_role = before.guild.get_role(586418283780112385)
        regular_member_1_role = before.guild.get_role(641454086310461478)
        regular_member_2_role = before.guild.get_role(726246561100857345)
        regular_member_3_role = before.guild.get_role(726246637185531904)
        if not int_role in before.roles and int_role in after.roles:
            await notice_ch.send(f"{before.name}さんが{int_role.name}を獲得しました！\nおめでとうございます！")
        elif not regular_member_1_role in before.roles and regular_member_1_role in after.roles:
            await notice_ch.send(f"{before.name}さんが{regular_member_1_role.name}を獲得しました！\nおめでとうございます！")
        elif not regular_member_2_role in before.roles and regular_member_2_role in after.roles:
            await notice_ch.send(f"{before.name}さんが{regular_member_2_role.name}を獲得しました！\nおめでとうございます！")
        elif not regular_member_3_role in before.roles and regular_member_3_role in after.roles:
            await notice_ch.send(f"{before.name}さんが{regular_member_3_role.name}を獲得しました！\nおめでとうございます！")


async def on_message(client1, message, prefix, command):
    if not message.author.bot:
        await count_message(message)

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
            await commands.random_command(message, command)

        elif command.startswith("weather "):
            await commands.weather(message, command)

        elif command.startswith("vote "):
            await commands.vote(message, command)

        elif command.startswith("name "):
            await commands.name(message, command)

        elif command.startswith("user_data"):
            await kei_server_commands.user_data(message, command)

        elif command == "mypt":
            await kei_server_commands.mypt(message)

        elif command.startswith("ranking "):
            await kei_server_commands.ranking(message, command)

        elif command == "glist":
            await kei_server_commands.glist(message, client1)

        elif command == "accept":
            await kei_server_commands.accept(message, client1)

        elif command == "marichan_invite":
            await kei_server_commands.marichan_invite(message)

        elif command.startswith("delmsg"):
            await kei_server_commands.delmsg(message, client1, command)

        elif command.startswith("mcid "):
            await kei_server_commands.edit_mcid(message, command)

        elif command.startswith("point ") or command.startswith("pt "):
            await kei_server_commands.point(message, command)

        elif command.startswith("remove_role "):
            await kei_server_commands.remove_role(message, command)

        elif command == "datas":
            await kei_server_commands.send_zip_data(message)

        elif command.startswith("before_ban "):
            await kei_server_commands.before_ban(message, client1, command)

        elif command.startswith("unban "):
            await kei_server_commands.unban(message, client1, command)

        elif command.startswith("delete_user_data "):
            await kei_server_commands.delete_user_data(message, client1, command)

        elif command == "ban_list":
            await kei_server_commands.ban_list(message, client1)

        elif command == "gban_list":
            await kei_server_commands.gban_list(message)

        elif command.startswith("global_notice "):
            await kei_server_commands.global_notice(message, client1, command)

        elif command.startswith("leave_guild "):
            #通知chを魔理沙からのお知らせとする
            await kei_server_commands.leave_guild(message, client1, command)

        #elif command.startswith("tanzaku "):
        #    await limited_time.tanzaku(message, command)

    if message.channel.id == 640833025822949387:
        await register_mcid(message, client1)

    elif message.channel.id == 634602609017225225:
        await login_bonus(message)
    
    elif message.channel.id == 603832801036468244:
        await shiritori(message)

    elif message.channel.id == 762546731417731073:
        await story(message, prefix)

    elif message.channel.id == 762546959138816070:
        await story_secret(message, prefix)

    elif message.channel.id == 639830406270681099:
        await dm_send(message, client1)

    elif message.channel.id == 722810355511984185:
        await create_new_func(client1, message)

    elif message.channel.id == 665487669953953804:
        await limited_time.simple_kikaku_join(message) #応募者に企画参加者役職を付与する
    #    await limited_time.seichi_taikai_join(message) #整地大会用の企画


async def on_reaction_add(client1, reaction, user):
    msg = reaction.message
    if user.mention in msg.content and str(reaction) == "🔄" and msg.author.id == client1.user.id:
        connection = MySQLdb.connect(
            host=os.getenv("mysql_host"),
            user=os.getenv("mysql_user"),
            passwd=os.getenv("mysql_passwd"),
            db="capcha"
        )
        cursor = connection.cursor()
        cursor.execute(f"select moji from capcha_tbl where user_id={user.id}")
        result = cursor.fetchall()
        try:
            result[0][0]
        except IndexError:
            cursor.close()
            connection.close()
            return

        mojiretsu = kei_server_commands.create_pic_capcha()
        cursor.execute(f"update capcha_tbl set moji='{mojiretsu}' where user_id='{user.id}'")
        connection.commit()
        cursor.close()
        connection.close()

        file = discord.File("capcha.png")
        await msg.delete()
        msg2 = await msg.channel.send(content=f"{user.mention}\nお読みください(ひらがな5文字)\n60秒無言でタイムアウト\nリアクションで画像変更", file=file)
        await msg2.add_reaction("🔄")


async def on_raw_reaction_add(client1, payload):
    """
    リアクションが付けられた時用の関数"""

    channel = client1.get_channel(payload.channel_id)
    user = client1.get_user(payload.user_id)
    guild = client1.get_guild(payload.guild_id)
    member = guild.get_member(payload.user_id)

    if channel.id == 664286990677573680:
        if not payload.message_id == 1174671007609532466:
            return

        if user == client1.user:
            return

        msg = await channel.fetch_message(payload.message_id)
        await msg.remove_reaction(f"{payload.emoji}", user)
        emoji_tuple = (
            "\U0001f1e6",
            "\U0001f1e7",
            "\U0001f1e8",
            "\U0001f1e9",
            "\U0001f1ea",
            "\U0001f1eb",
            "\U0001f1ec",
            "\U0001f1ed",
            "\U0001f1ee",
            "\U0001f1ef"
        )
        role_id_tuple = (
            975330354179244053, #VRC
            586123567146729475, #シュータ
            678445373324263454, #乗り鉄
            678445640027734032, #撮り鉄
            678445821603217448, #音鉄
            870467547475091467, #V
            606481478078955530, #通知ほしい
            673349311228280862, #投票通知
            848183279458189312, #amongus
            774551525083054090, #ミニゲーム
        )
        if payload.emoji.name in emoji_tuple:
            emoji_index = emoji_tuple.index(payload.emoji.name)
            role = guild.get_role(role_id_tuple[emoji_index])
            if role in member.roles:
                await member.remove_roles(role)
                system_message = await channel.send(f"{member.mention}から{role.name}を剥奪しました")
            else:
                await member.add_roles(role)
                system_message = await channel.send(f"{member.mention}に{role.name}を付与しました")

        else:
            system_message = await channel.send(f"{member.mention}その絵文字は使用できません")

        await asyncio.sleep(3)
        await system_message.delete()


async def count_members(client1):
    """
    サーバにいる人数を数えて記録する関数"""

    with open("./datas/count_members.json", mode="r", encoding="utf-8") as f:
        members_dict = json.load(f)
    today = datetime.date.today().strftime(r"%Y%m%d")
    guild = client1.get_guild(585998962050203672)
    members_dict[today] = len(guild.members)
    members_json = json.dumps(members_dict, indent=4)
    with open("./datas/count_members.json", mode="w", encoding="utf-8") as f:
        f.write(members_json)


async def change_date(client1):
    """
    日付変更お知らせ用関数"""

    notice_ch = client1.get_channel(710021903879897098)
    today = datetime.date.today()

    today_str = today.strftime(r"%Y/%m/%d")
    finished_percentage = round((datetime.date.today().timetuple()[7] - 1) / 365 * 100, 2) #正直動きがわからないのとうるう年はバグる
    if datetime.date.today() >= datetime.date(today.year, 6, 29):
        year_seichi = today.year + 1
    else:
        year_seichi = today.year
    seichisaba_birthday = datetime.date(year_seichi, 6, 29)
    how_many_days = str(seichisaba_birthday - today)
    how_many_days = how_many_days.replace(how_many_days[-13:], "")
    text = (
        f"本日の日付: {today_str}\n"
        f"{today.year}年の{finished_percentage}%が終了しました\n"
        f"整地鯖{year_seichi-2016}周年まであと{how_many_days}日です"
    )

    daily_embed = discord.Embed(title=f"日付変更をお知らせします", description=text, color=0xfffffe)

    yesterday_str = (today - datetime.timedelta(days=1)).strftime(r"%Y%m%d")
    before_yesterday_str = (today - datetime.timedelta(days=2)).strftime(r"%Y%m%d")
    with open("./datas/count_message.json", mode="r", encoding="utf-8") as f:
        message_dict = json.load(f)
    yesterday_messages = message_dict[yesterday_str]
    before_yesterday_messages = message_dict[before_yesterday_str]
    plus_minus = yesterday_messages - before_yesterday_messages
    if plus_minus > 0:
        plus_minus = f"+{plus_minus}"
    else:
        plus_minus = f"{plus_minus}"
    daily_embed.add_field(name="messages", value=f"昨日の発言数: {yesterday_messages}\n前日比: {plus_minus}", inline=True)

    with open("./datas/count_members.json", mode="r", encoding="utf-8") as f:
        members_dict = json.load(f)
    today_members = members_dict[datetime.date.today().strftime(r"%Y%m%d")]
    yesterday_members = members_dict[yesterday_str]
    plus_minus = today_members - yesterday_members
    if plus_minus > 0:
        plus_minus = f"+{plus_minus}"
    else:
        plus_minus = f"{plus_minus}"
    daily_embed.add_field(name="members", value=f"今の人数: {today_members}\n前日比: {plus_minus}", inline=True)

    await notice_ch.send(embed=daily_embed)


async def jms_notice(client1):
    """
    毎日9:10に雑談チャンネルでメンションを飛ばす"""

    ch = client1.get_channel(597130965927723048)
    async for msg in ch.history(limit=100):
        if msg.author.id == client1.user.id and "<@&673349311228280862>" in msg.content:
            await msg.delete()
            break

    await ch.send(
        "<@&673349311228280862>\n"
        "https://minecraft.jp/servers/54d3529e4ddda180780041a7/vote\n\n"
        "https://minecraftservers.org/server/575658"
    )


async def check_new_seichiserver_player_and_int_role_getter(client1):
    """
    新たに21億以上掘った人がいないか確認する"""

    connection = MySQLdb.connect(
        host=os.getenv("mysql_host"),
        user=os.getenv("mysql_user"),
        passwd=os.getenv("mysql_passwd"),
        db=os.getenv("mysql_db_name")
    )
    cursor = connection.cursor()
    cursor.execute("select id, uuid from uuids")
    result = cursor.fetchall()
    cursor.close()
    connection.close()

    with open("./datas/player_data.json", mode="r", encoding="utf-8") as f:
        player_data_dict = json.load(f)

    guild = client1.get_guild(585998962050203672)
    seichiserver_role = guild.get_role(616790954200006717)
    int_role = guild.get_role(586418283780112385)
    for user_id, uuid in result:
        uuid = re.sub(r"(\w{8})(\w{4})(\w{4})(\w{4})(\w{12})", r"\1-\2-\3-\4-\5", uuid)
        try:
            seichi_break = player_data_dict[uuid]["total_break"]
        except KeyError:
            pass
        else:
            member = guild.get_member(user_id)
            if seichiserver_role not in member.roles:
                await member.add_roles(seichiserver_role)

            if seichi_break >= 2100000000:
                await member.add_roles(int_role)


async def kei_daily_score(client1):
    """
    kei_3104の日間整地量を表示"""

    with open("./datas/player_data.json", mode="r", encoding="utf-8") as f:
        player_data_dict = json.load(f)

    total = player_data_dict["73b41f61-3b2b-4730-b775-564516101b3c"]["total_break"]
    today = player_data_dict["73b41f61-3b2b-4730-b775-564516101b3c"]["break"]

    daily = total - today
    daily = "{:,}".format(daily)
    channel = client1.get_channel(793478659775266826)
    embed = discord.Embed(
        description=f"本日のkei_3104の整地量は大体 **{daily}** くらいでした",
        color=random.randint(0x000000, 0xffffff)
    )
    embed.set_author(name="kei_3104", icon_url=f"https://minotar.net/helm/kei_3104/100.png")
    await channel.send(embed=embed)


async def shiritori_reset(client1):
    """
    一週間に一度しりとりチャンネルをリセットする関数"""

    ch = client1.get_channel(603832801036468244)
    await ch.purge(limit=None)
    start_msg_tuple = (
        "しりとり",
        "霧雨魔理沙(きりさめまりさ)",
        "多々良小傘(たたらこがさ)",
        "リリカ・プリズムリバー"
    )
    await ch.send(random.choice(start_msg_tuple))


async def record_story(client1):
    """
    毎週月曜日の朝3:30に物語を記録"""

    record_ch = client1.get_channel(762553442040021032)

    with open("./datas/story.txt", mode="r", encoding="utf-8") as f:
        story = f.read()

    if story == "":
        story = "今週は物語は書かれませんでした・・・"

    while True:
        if len(story) > 2000:
            embed = discord.Embed(description=story[:2000], color=0x00ffff)
            await record_ch.send(embed=embed)
            story = story[2000:]
        else:
            embed = discord.Embed(description=story, color=0x00ffff)
            await record_ch.send(embed=embed)
            break

    with open("./datas/story_secret.txt", mode="r", encoding="utf-8") as f:
        story = f.read()

    if story == "":
        story = "今週は物語は書かれませんでした・・・"

    while True:
        if len(story) > 2000:
            embed = discord.Embed(description=story[:2000], color=0xaa00aa)
            await record_ch.send(embed=embed)
            story = story[2000:]
        else:
            embed = discord.Embed(description=story, color=0xaa00aa)
            await record_ch.send(embed=embed)
            break

    with open("./datas/story.txt", mode="w", encoding="utf-8") as f:
        f.write("")

    with open("./datas/story_secret.txt", mode="w", encoding="utf-8") as f:
        f.write("")

    ch = client1.get_channel(762546731417731073)
    await ch.send("----キリトリ----")
    ch = client1.get_channel(762546959138816070)
    await ch.purge()
    await ch.send("----キリトリ----")


async def check_mcid_exist_now(client1):
    """
    現在登録されているMCIDが存在するかをチェックする関数
    存在しない場合更新する"""

    with open("./datas/user_data.json", mode="r", encoding="utf-8") as f:
        user_data_dict = json.load(f)

    description = ""
    alart_ch = client1.get_channel(595072269483638785) #1組

    with open("./datas/user_data.json", mode="r", encoding="utf-8") as f:
        user_data_dict = json.load(f)

    connection = MySQLdb.connect(
        host=os.getenv("mysql_host"),
        user=os.getenv("mysql_user"),
        passwd=os.getenv("mysql_passwd"),
        db=os.getenv("mysql_db_name")
    )

    description = ""
    for user_id in user_data_dict.keys():
        mcid_list = user_data_dict[user_id]["mcid"]
        if mcid_list == []:
            continue

        changed_mcid_list = []
        for mcid in mcid_list:
            cursor = connection.cursor()
            cursor.execute(f"select uuid from uuids where mcid='{mcid}'")
            result = cursor.fetchall()
            cursor.close()

            try:
                uuid = result[0][0]
            except IndexError:
                await alart_ch.send(f"IndexError: {mcid}")
                continue

            url = f"https://api.mojang.com/user/profile/{uuid}"

            try:
                res = requests.get(url)
                res.raise_for_status()
            except requests.exceptions.HTTPError:
                await alart_ch.send(f"{mcid}の検証中にHTTPErrorが発生しました")
                continue

            data = res.json()
            try:
                correct_mcid = data["name"]
            except KeyError:
                await alart_ch.send(f"<@523303776120209408> {mcid}: ({uuid})は消された可能性があります。確認されたい") #1組に送信
            else:
                if correct_mcid != mcid:
                    cursor = connection.cursor()
                    cursor.execute(f"update uuids set mcid='{correct_mcid}' where mcid='{mcid}'")
                    connection.commit()
                    cursor.close()
                    changed_mcid_list.append((mcid, correct_mcid))

        for mcid, correct_mcid in changed_mcid_list:
            mcid_list.remove(mcid)
            mcid_list.append(correct_mcid)
            description += f"<@{user_id}>の{mcid}を{correct_mcid}に置換します\n"
        user_data_dict[user_id]["mcid"] = mcid_list

    connection.close()

    user_data_json = json.dumps(user_data_dict, indent=4)
    with open("./datas/user_data.json", mode="w", encoding="utf-8") as f:
        f.write(user_data_json)

    description = description.replace("_", "\_")
    if description == "":
        description = "今週のMCID更新はありません"
    embed = discord.Embed(description=description)
    await alart_ch.send(embed=embed)


async def marichan_birthday(client1):
    """
    6/28は魔理沙botの誕生日です"""

    ch = client1.get_channel(585999375952642067)
    embed = discord.Embed(
        title="Happy Birthday!!:tada:",
        description=(
            "本日、6月28日は魔理沙bot生誕七周年です。\n"
            "記念に現時刻から23:59(botの指示による)までに本サーバで「ガチャ券を寄こせ」と言うとガチャ券を7st進呈します。\n"
            "(インできる時間が合わない場合寄付箱への配達とする可能性があります)\n"
            "(文字は正確に打ちましょう、検索に引っかからないと対象になりません)"
        ),
        color=0xffff00
    )
    await ch.send(content=client1.get_guild(585998962050203672).get_role(585998962050203672).name, embed=embed)


async def marichan_birthday_finish(client1):
    """
    しゅーりょーカンカンカン"""

    ch = client1.get_channel(585999375952642067)
    await ch.send("あはははは！おわりですおわりです！！！！")

#ーーーーここまでメイン、以下補助関数ーーーー

async def count_message(message):
    """
    投稿されたメッセージ数を数える"""

    with open("./datas/count_message.json", mode="r") as f:
        counter_dict = json.load(f)

    today = datetime.date.today().strftime(r"%Y%m%d")
    try:
        counter_dict[today] += 1
    except KeyError:
        counter_dict[today] = 1

    counter_json = json.dumps(counter_dict, indent=4)
    with open("./datas/count_message.json", mode="w") as f:
        f.write(counter_json)

    if message.channel.id in (586075792950296576, 691901316133290035): #スパム許可、ミニゲームなら
        return

    with open("./datas/user_data.json", mode="r") as f:
        user_data_dict = json.load(f)

    try:
        user_data_dict[f"{message.author.id}"]["speak"] += 1
    except KeyError:
        user_data_dict[f"{message.author.id}"] = {"ban": False, "role": [], "mcid": [], "point": 0, "speak": 0}
        user_data_dict[f"{message.author.id}"]["speak"] = 1

    regular_member_1_role = message.guild.get_role(641454086310461478)
    regular_member_2_role = message.guild.get_role(726246561100857345)
    regular_member_3_role = message.guild.get_role(726246637185531904)
    now = datetime.datetime.now()
    joined_time = message.author.joined_at + datetime.timedelta(hours=9)
    joined_time = joined_time.replace(tzinfo=None)

    if regular_member_3_role in message.author.roles:
        pass
    elif regular_member_2_role in message.author.roles:
        if user_data_dict[f"{message.author.id}"]["speak"] >= 3000 and joined_time + datetime.timedelta(days=365) <= now:
            await message.author.add_roles(regular_member_3_role)
            await message.author.remove_roles(regular_member_2_role)
    elif regular_member_1_role in message.author.roles:
        if user_data_dict[f"{message.author.id}"]["speak"] >= 2000 and joined_time + datetime.timedelta(days=182, hours=12) <= now:
            await message.author.add_roles(regular_member_2_role)
            await message.author.remove_roles(regular_member_1_role)
    else:
        if user_data_dict[f"{message.author.id}"]["speak"] >= 1000:
            await message.author.add_roles(regular_member_1_role)

    user_data_json = json.dumps(user_data_dict, indent=4)
    with open("./datas/user_data.json", mode="w") as f:
        f.write(user_data_json)


async def register_mcid(message, client1):
    """
    MCID報告システム"""

    if message.author.bot:
        return

    message_content = message.content.replace("\\", "")
    p = re.compile(r"^[a-zA-Z0-9_\\\n →]+$")
    if not p.fullmatch(message_content):
        await message.channel.send("MCID(報告/変更報告)に使えない文字が含まれています")
        return

    if len(message_content.split("→")) == 1: #MCIDの追加

        right_mcid_length_list = []
        for mcid in tuple(set(message_content.split())): #重複を弾いてtupleにする
            if not kei_server_commands.check_mcid_length(mcid):
                mcid = mcid.replace("_", "\_")
                await message.channel.send(f"**{mcid}**はMCIDとして成り立ちません")
            else:
                right_mcid_length_list.append(mcid)

        right_mcid_not_yet_list = []
        for mcid in right_mcid_length_list:
            if not kei_server_commands.check_mcid_yet(mcid):
                mcid = mcid.replace("_", "\_")
                await message.channel.send(f"**{mcid}**は既に登録されています")
            else:
                right_mcid_not_yet_list.append(mcid)

        right_mcid_exsit_list = []
        for mcid in right_mcid_not_yet_list:
            mcid_uuid_tuple = kei_server_commands.check_mcid_exist(mcid)
            if mcid_uuid_tuple is None:
                await message.channel.send("現在データ参照元が使用できない状態です。しばらくたってからもう一度お試しください。")
                return

            if not mcid_uuid_tuple:
                mcid = mcid.replace("_", "\_")
                await message.channel.send(
                    f"**{mcid}**は```\n・存在しない\n・MCIDを変更した```\n"
                    "可能性があります。\n__**意図的に間違った入力を繰り返していると判断された場合処罰の対象になります。**__"
                )
            else:
                right_mcid_exsit_list.append(mcid_uuid_tuple) #mcid_uuid_tupleは(mcid, uuid)

        if len(right_mcid_exsit_list) == 0:
            return

        with open("./datas/user_data.json", mode="r", encoding="utf-8") as f:
            user_data_dict = json.load(f)

        try:
            user_data = user_data_dict[f"{message.author.id}"]
        except KeyError:
            user_data_dict[f"{message.author.id}"] = {"ban": False, "role": [], "mcid": [], "point": 0, "speak": 0}
            user_data = user_data_dict[f"{message.author.id}"]

        mcid_list = user_data["mcid"]
        if len(mcid_list) != 0:
            msg = await message.channel.send(
                "既に登録されているMCIDがあります。変更の間違いではありませんか？追加で宜しいですか？\n"
                "変更->「🇨」\n追加->「🇦」\nをリアクションしてください"
            )
            await msg.add_reaction("🇨")
            await msg.add_reaction("🇦")
            def check(reaction, user):
                return user == message.author and (str(reaction.emoji) == "🇦" or str(reaction.emoji) == "🇨")
            try:
                reply = await client1.wait_for("reaction_add", check=check, timeout=60)
            except asyncio.TimeoutError:
                await message.channel.send("タイムアウトしました。最初からやり直してください")
                return
            else:
                if str(reply[0].emoji) == "🇨":
                    await message.channel.send("変更申請の形式は旧MCID→新MCIDです。最初からやり直してください。")
                    return

        connection = MySQLdb.connect(
            host=os.getenv("mysql_host"),
            user=os.getenv("mysql_user"),
            passwd=os.getenv("mysql_passwd"),
            db=os.getenv("mysql_db_name")
        )
        cursor = connection.cursor()
        register_mcid_list = []
        for mcid, uuid in right_mcid_exsit_list:
            mcid_list.append(mcid)
            register_mcid_list.append(mcid)
            cursor.execute(f"insert into uuids (id, uuid, mcid) values ({message.author.id}, '{uuid}', '{mcid}')")
            connection.commit()

        cursor.close()
        connection.close()

        user_data_json = json.dumps(user_data_dict, indent=4)
        with open("./datas/user_data.json", mode="w", encoding="utf-8") as f:
            f.write(user_data_json)

        crafter_role = message.guild.get_role(586123363513008139)
        if crafter_role not in message.author.roles:
            await message.author.add_roles(crafter_role)

        seichiserver_role = message.guild.get_role(616790954200006717)
        if seichiserver_role not in message.author.roles:
            with open("./datas/player_data.json", mode="r", encoding="utf-8") as f:
                player_data_dict = json.load(f)

            for mcid, uuid in right_mcid_exsit_list:
                uuid = re.sub(r"(\w{8})(\w{4})(\w{4})(\w{4})(\w{12})", r"\1-\2-\3-\4-\5", uuid)
                if uuid in player_data_dict.keys():
                    await message.author.add_roles(seichiserver_role)
                    break

        mcid_list_str = ", ".join(register_mcid_list).replace("_", "\_")
        await message.channel.send(f"MCIDの登録が完了しました。登録されたMCID: {mcid_list_str}")

        new_role = message.guild.get_role(621641465105481738)
        accept_able_role = message.guild.get_role(626062897633689620)
        if new_role in message.author.roles:
            await message.author.add_roles(accept_able_role)
            await message.channel.send("MCIDの報告ありがとうございます。ルールに同意していただけるなら<#592581835343659030>で**/accept**をお願いします。")

    elif len(message_content.split("→")) == 2: #MCIDの変更
        before_mcid = message_content.split("→")[0]
        after_mcid = message_content.split("→")[1]

        if before_mcid == after_mcid:
            await message.channel.send("何を変更したんですか？")
            return

        if not kei_server_commands.check_mcid_length(after_mcid):
            print(after_mcid)
            after_mcid = after_mcid.replace("_", "\_")
            await message.channel.send(f"**{after_mcid}**はMCIDとして成り立ちません")
            return

        if not kei_server_commands.check_mcid_yet(after_mcid):
            after_mcid = after_mcid.replace("_", "\_")
            await message.channel.send(f"**{after_mcid}**は既に登録されています")
            return

        mcid_uuid_tuple = kei_server_commands.check_mcid_exist(after_mcid)
        if mcid_uuid_tuple is None:
            await message.channel.send("現在データ参照元が使用できない状態です。しばらくたってからもう一度お試しください。")
            return

        if not mcid_uuid_tuple:
            after_mcid = after_mcid.replace("_", "\_")
            await message.channel.send(
                f"**{after_mcid}**は```\n・存在しない\n・MCIDを変更した```\n"
                "可能性があります。\n__**意図的に間違った入力を繰り返していると判断された場合処罰の対象になります。**__"
            )
            return

        with open("./datas/user_data.json", mode="r", encoding="utf-8") as f:
            user_data_dict = json.load(f)

        try:
            user_data = user_data_dict[f"{message.author.id}"]
        except KeyError:
            user_data_dict[f"{message.author.id}"] = {"ban": False, "role": [], "mcid": [], "point": 0, "speak": 0}
            user_data = user_data_dict[f"{message.author.id}"]

        mcid_list = user_data["mcid"]
        flag = False
        for mcid in mcid_list:
            if before_mcid.lower() == mcid.lower():
                index = mcid_list.index(mcid)
                mcid_list[index] = after_mcid
                flag = True
                break

        if not flag:
            str(mcid_list).replace("_", "\_")
            await message.channel.send(f"**{before_mcid}**は登録されていません。現在あなたが登録しているMCID:\n{mcid_list}")
            return

        connection = MySQLdb.connect(
            host=os.getenv("mysql_host"),
            user=os.getenv("mysql_user"),
            passwd=os.getenv("mysql_passwd"),
            db=os.getenv("mysql_db_name")
        )
        cursor = connection.cursor()
        cursor.execute(f"update uuids set mcid='{after_mcid}' where mcid='{before_mcid}'")
        connection.commit()
        cursor.close()
        connection.close()

        user_data_json = json.dumps(user_data_dict, indent=4)
        with open("./datas/user_data.json", mode="w", encoding="utf-8") as f:
            f.write(user_data_json)

        before_mcid = before_mcid.replace("_", "\_")
        after_mcid = after_mcid.replace("_", "\_")
        await message.channel.send(f"MCIDの変更が登録されました\n**{before_mcid}**→**{after_mcid}**")

    else:
        await message.channel.send("MCIDの変更申請は1アカウントずつ行ってください。")


async def login_bonus(message):
    """
    ログボ"""

    if message.author.bot:
        return

    msg = jaconv.h2z(message.clean_content, ignore="", kana=True, ascii=True, digit=True) #全て全角にする
    msg = jaconv.z2h(msg, ignore="", kana=False, ascii=True, digit=True) #英数のみ半角にする
    msg = jaconv.kata2hira(msg, ignore="") #全てひらがなにする
    msg = msg.lower() #小文字にする
    space_tuple = (
        '\u0009', '\u0020', '\u00A0', '\u00AD', '\u034F', '\u061C', '\u115F', '\u1160', '\u17B4', '\u17B5',
        '\u180E', '\u2000', '\u2001', '\u2002', '\u2003', '\u2004', '\u2005', '\u2006', '\u2007', '\u2008',
        '\u2009', '\u200A', '\u200B', '\u200C', '\u200D', '\u200E', '\u200F', '\u202F', '\u205F', '\u2060',
        '\u2061', '\u2062', '\u2063', '\u2064', '\u206A', '\u206B', '\u206C', '\u206D', '\u206E', '\u206F',
        '\u3000', '\u2800', '\u3164', '\uFEFF', '\uFFA0', '\u1D159', '\u1D173', '\u1D174', '\u1D175', '\u1D176',
        '\u1D177', '\u1D178', '\u1D179', '\u1D17A'
    )
    for space in space_tuple:
        msg = msg.replace(space, "")
    msg = msg.replace("\n", "").replace("゛", "").replace("っ", "").replace("-", "").replace("ー", "") #邪魔な装飾を消す(全角スペースはz2hで消えてる)
    msg = msg.replace("chan", "ちゃん").replace("tyan", "ちゃん").replace("tan", "たん") #英語でのちゃん付けを変換
    msg = msg.replace("ma", "ま").replace("ri", "り").replace("sa", "さ") #ローマ字をひらがなに変換
    print(msg)
    #この時点で全角ひらがなと半角英数のみ
    NG_word_tuple = (
        "魔理",
        "まりさ",
        "まりちゃん",
        "まりたん",
    )
    for NG_word in NG_word_tuple:
        if NG_word in msg:
            await message.channel.send("強制はずれ")
            return

    with open("./datas/word.json", mode="r", encoding="utf-8") as f:
        word_dict = json.load(f)

    flag = False
    for key in word_dict.keys():
        if key in message.content:
            get_pt = word_dict[key]
            touraku = f"指定ワードを引きました！: {key}"
            flag = True
            break

    if flag:
        del word_dict[key]
        word_json = json.dumps(word_dict, indent=4, ensure_ascii=False)
        with open("./datas/word.json", mode="w", encoding="utf-8") as f:
            f.write(word_json)

    else:
        kouho_tuple = ("おめでとう！", "はずれ", "はずれ")
        touraku = random.choice(kouho_tuple)
        if touraku == "はずれ":
            await message.channel.send(touraku)
            return

        get_pt = random.randint(1,32)

    with open("./datas/user_data.json", mode="r", encoding="utf-8") as f:
        user_data_dict = json.load(f)

    try:
        had_pt = user_data_dict[f"{message.author.id}"]["point"]
    except KeyError:
        user_data_dict[f"{message.author.id}"] = {"ban": False, "role": [], "mcid": [], "point": 0, "speak": 0}
        had_pt = user_data_dict[f"{message.author.id}"]["point"]

    after_pt = had_pt + get_pt
    if after_pt < 0:
        after_pt = 0

    user_data_dict[f"{message.author.id}"]["point"] = after_pt
    user_data_json = json.dumps(user_data_dict, indent=4)
    with open("./datas/user_data.json", mode="w", encoding="utf-8") as f:
        f.write(user_data_json)

    await message.channel.send(f"{touraku}\n{get_pt}ptゲット！\n{message.author.name}の保有pt: {had_pt}→{after_pt}")


async def shiritori(message):
    """
    しりとりチャンネルでメッセージがんかンで終わったら対処する"""

    if message.content.endswith("ん") or message.content.endswith("ン"):
        shiritori_nn_list = (
            "ンジャメナ",
            "ンゴロンゴロ",
            "ンカイ",
            "ンガミ湖",
            "ンズワニ島","ンゼレコレ",
            "ンスタ",
            "ンスカ",
            "ンジャジジャ島"
        )
        await message.channel.send(random.choice(shiritori_nn_list))


async def story(message, prefix):
    """
    物語作ろうぜ"""

    if message.author.bot:
        return

    if not message.content:
        await message.delete()
        return

    if message.content.startswith(prefix):
        return

    with open("./datas/story.txt", mode="a", encoding="utf-8") as f:
        f.write(f"{message.content}\n")


async def story_secret(message, prefix):
    """
    物語作ろうぜ
    でも前々文は見えないぜ"""

    if message.author.bot:
        return

    if not message.content:
        await message.delete()
        return

    if message.content.startswith(prefix):
        await message.delete()
        await message.channel.send(f"{message.author.mention}\nこのチャンネルでのコマンド使用はできません", delete_after=5)
        return

    with open("./datas/story_secret.txt", mode="a", encoding="utf-8") as f:
        f.write(f"{message.content}\n")

    embed = discord.Embed(description=message.content)
    embed.set_author(name=message.author.name, icon_url=message.author.display_avatar.url)
    await message.channel.purge()
    await message.channel.send(embed=embed)


async def dm_send(message, client1):
    """
    指定ユーザーにDMを送る
    user_id␣内容"""

    if message.author.bot:
        return

    if not message.author.id == 523303776120209408:
        await message.channel.send("何様のつもり？")
        doM_role = message.guild.get_role(616212704818102275)
        await message.author.add_roles(doM_role)
        return

    if len(message.content.split()) == 1:
        await message.channel.send("内容をいれてください")
        return

    try:
        user_id = int(message.content.split()[0])
    except ValueError:
        await message.channel.send("不正なIDです")
        return

    user = client1.get_user(user_id)
    if user is None:
        await message.channel.send("監視下にないユーザーIDです")
        return

    msg = message.content.replace(message.content.split()[0], "")

    try:
        await user.send(msg)
    except discord.errors.Forbidden:
        await message.channel.send("権限がありません")


async def create_new_func(client1, message):
    """
    PHPから送られてくるwebhookデータを解析し条件に合致するようならJSONに書き込む
    条件に合致しなければリクエスト者に対してDMを送る"""

    if not message.author.id == 722810440362491995:
        return

    request_list = message.content.split("\n")
    user_id = int(request_list[0])
    user = client1.get_user(user_id)
    try:
        guild_id = int(request_list[1])
    except ValueError:
        await user.send(f"サーバID:{request_list[1]} は不正です。リクエストは却下されました。")
        return

    guild = client1.get_guild(guild_id)
    if guild is None:
        await user.send(f"サーバID:{guild_id} を持つサーバは存在しないか本botの監視下にありません。リクエストは却下されました。")
        return

    member = guild.get_member(user_id)
    if member is None:
        await user.send(f"あなたはサーバ:{guild.name} に入っていません。リクエストは却下されました。")
        return

    if not member.guild_permissions.administrator:
        await user.send(f"あなたはサーバ:{guild.name} の管理者権限を持っていません。リクエストは却下されました。")
        return

    about_ch = request_list[3].split()
    if about_ch[0] == "all_ok":
        ch_permmission = {"disable_c": []}
    elif about_ch[0] == "able":
        ch_permmission = {"able_c": []}
        for ch in about_ch[1:]:
            try:
                ch_id = int(ch)
            except ValueError:
                await user.send(f"チャンネルID:{ch} は不正です。リクエストは却下されました。")
                return
            channel = guild.get_channel(ch_id)
            if channel is None:
                await user.send(f"チャンネルID:{ch_id} を持つチャンネルは{guild.name}に存在しません。リクエストは却下されました。")
                return
            ch_permmission["able_c"].append(ch_id)
    else:
        ch_permmission = {"disable_c": []}
        for ch in about_ch[1:]:
            try:
                ch_id = int(ch)
            except ValueError:
                await user.send(f"チャンネルID:{ch} は不正です。リクエストは却下されました。")
                return
            channel = guild.get_channel(ch_id)
            if channel is None:
                await user.send(f"チャンネルID:{ch_id} を持つチャンネルは{guild.name}に存在しません。リクエストは却下されました。")
                return
            ch_permmission["disable_c"].append(ch_id)

    about_role = request_list[4].split()
    if about_role == "all_ok":
        role_permission = {"disable_r": []}
    elif about_role == "able":
        role_permission = {"able_r": []}
        for role_ in about_role[1:]:
            try:
                role_id = int(role_)
            except ValueError:
                await user.send(f"役職ID:{role_} は不正です。リクエストは却下されました。")
                return
            role = guild.get_role(role_id)
            if role is None:
                await user.send(f"役職ID:{role_id} を持つ役職は{guild.name}に存在しません。リクエストは却下されました。")
                return
            role_permission["able_r"].append(role_id)
    else:
        role_permission = {"disable_r": []}
        for role_ in about_role[1:]:
            try:
                role_id = int(role_)
            except ValueError:
                await user.send(f"役職ID:{role_} は不正です。リクエストは却下されました。")
                return
            role = guild.get_role(role_id)
            if role is None:
                await user.send(f"役職ID:{role_id} を持つ役職は{guild.name}に存在しません。リクエストは却下されました。")
                return
            role_permission["disable_r"].append(role_id)

    send_message = request_list[5].split()
    if send_message[0] == "None":
        msg_dict = {"message": []}
    else:
        msg_dict = {"message": []}
        for msg in send_message:
            msg_dict["message"].append(msg)
    add_role = request_list[6].split()
    if add_role[0] == "None":
        add_role_dict = {"add_role": []}
    else:
        add_role_dict = {"add_role": []}
        for role_ in add_role:
            try:
                role_id = int(role_)
            except ValueError:
                await user.send(f"役職ID:{role_} は不正です。リクエストは却下されました。")
                return
            role = guild.get_role(role_id)
            if role is None:
                await user.send(f"役職ID:{role_id} を持つ役職は{guild.name}に存在しません。リクエストは却下されました。")
                return
            add_role_dict["add_role"].append(role_id)
    remove_role = request_list[7].split()
    if remove_role[0] == "None":
        remove_role_dict = {"remove_role": []}
    else:
        remove_role_dict = {"remove_role": []}
        for role_ in remove_role:
            try:
                role_id = int(role_)
            except ValueError:
                await user.send(f"役職ID:{role_} は不正です。リクエストは却下されました。")
                return
            role = guild.get_role(role_id)
            if role is None:
                await user.send(f"役職ID:{role_id} を持つ役職は{guild.name}に存在しません。リクエストは却下されました。")
                return
            remove_role_dict["remove_role"].append(role_id)

    with open("./datas/custom_commands.json", mode="r", encoding="utf-8") as f:
        custom_commands_dict = json.load(f)

    try:
        custom_commands = custom_commands_dict[f"{guild_id}"]
    except KeyError:
        custom_commands_dict[f"{guild_id}"] = {}
        custom_commands = custom_commands_dict[f"{guild_id}"]

    command = {}
    command.update(ch_permmission)
    command.update(role_permission)
    command.update(msg_dict)
    command.update(add_role_dict)
    command.update(remove_role_dict)

    trigger = request_list[2]

    custom_commands[trigger] = command

    custom_commands_json = json.dumps(custom_commands_dict, indent=4, ensure_ascii=False)
    with open("./datas/custom_commands.json", mode="w", encoding="utf-8") as f:
        f.write(custom_commands_json)

    await user.send(f"新規コマンド:{trigger}を登録しました。")


async def check_kei_login(client1):
    url = f"https://api.conarin.com/seichi/ranking/players/kei_3104?duration=total&types=break_count"
    notice_ch = client1.get_channel(595072269483638785)
    try:
        res = requests.get(url)
        res.raise_for_status()
        kei_data_dict = res.json()
    except requests.exceptions.HTTPError:
        await notice_ch.send("<@523303776120209408>\nログイン日時の取得に失敗しました。自分で確認してください")
        return
    
    last_login_datetime_str = kei_data_dict["lastLoginAt"]
    last_login_datetime_jst = datetime.datetime.strptime(last_login_datetime_str, r"%Y-%m-%dT%H:%M:%S+09:00")
    before_15min = datetime.datetime.now() - datetime.timedelta(minutes=15)
    if before_15min > last_login_datetime_jst:
        await notice_ch.send("<@523303776120209408>\nkei_3104が整地鯖にログインしていないようです")