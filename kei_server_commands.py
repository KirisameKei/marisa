import asyncio
import datetime
import json
import os
import random
import shutil
import re

import discord
import MySQLdb
import requests
from PIL import Image, ImageDraw, ImageFont

async def user_data(message, command):
    """
    けい鯖のユーザーのデータを表示する関数"""

    try:
        user_id = int(command.split()[1])
    except ValueError:
        await message.channel.send("不正な引数です")
        return
    except IndexError:
        user_id = message.author.id

    member = message.guild.get_member(user_id)
    if member is None:
        await message.channel.send("そんな人この鯖にいません")
        return

    with open("./datas/user_data.json", mode="r", encoding="utf-8") as f:
        user_data_dict = json.load(f)

    user_data = user_data_dict[f"{member.id}"]

    user_data_embed = discord.Embed(color=0xfffffe)
    user_data_embed.set_author(name=f"{member.name}", icon_url=member.display_avatar.url)

    roles = ""
    for role in reversed(member.roles):
        roles += f"{role.mention}\n"
    user_data_embed.add_field(name="roles", value=roles, inline=True)

    mcids = ""
    for mcid in user_data["mcid"]:
        mcid = mcid.replace("_", "\_")
        mcids += f"{mcid}\n"
    counter = len(user_data["mcid"])
    mcids += f"以上{counter}アカ"
    user_data_embed.add_field(name="MCID", value=mcids, inline=True)

    point = user_data["point"]
    user_data_embed.add_field(name="point", value=f"{point}", inline=True)

    speak = user_data["speak"]
    user_data_embed.add_field(name="speak", value=f"{speak}", inline=True)

    joined_time = (member.joined_at + datetime.timedelta(hours=9)).strftime(r"%Y/%m/%d-%H:%M")
    user_data_embed.add_field(name="joined", value=joined_time, inline=True)

    await message.channel.send(embed=user_data_embed)


async def mypt(message):
    """
    自分のpt保有量を確認する関数"""

    with open("./datas/user_data.json", mode="r", encoding="utf-8") as f:
        user_data_dict = json.load(f)

    try:
        had_pt = user_data_dict[f"{message.author.id}"]["point"]
    except KeyError:
        user_data_dict[f"{message.author.id}"] = {"ban": False, "role": [], "mcid": [], "point": 0, "speak": 0}
        had_pt = 0

    await message.channel.send(f"{message.author.name}さんは{had_pt}pt保有しています。")


async def ranking(message, command):
    """
    第一引数にpointかspeakを"""

    operation = command.split()[1]
    try:
        page = int(command.split()[2])
    except ValueError:
        await message.channel.send("ページ数が不正です")
        return
    except IndexError:
        page = 1

    if operation in ("point", "pt"):
        operation = "point"
        title = "ポイントランキング"
    elif operation == "speak":
        title = "発言数ランキング"
    else:
        await message.channel.send("引数が不正です。\nヒント: `/ranking␣[point, pt, speak]`")
        return

    with open("./datas/user_data.json", mode="r", encoding="utf-8") as f:
        user_data_dict = json.load(f)

    description = ""
    start = (page - 1) * 20
    i = 0
    for key, value in sorted(user_data_dict.items(), key=lambda x: -x[1][operation]):
        if i >= start:
            if i >= page * 20:
                break
            member = message.guild.get_member(int(key))
            point = value[operation]
            if member is None:
                description += f"{i+1}位: None: {point}\n"
            else:
                description += f"{i+1}位: {member.name}: {point}\n"
        i += 1

    embed = discord.Embed(title=f"{title} ({page}頁)", description=f"```\n{description}```", color=0x005500)
    await message.channel.send(embed=embed)


async def glist(message, client1):
    """
    bot参加鯖の一覧を表示"""

    text = ""
    for guild in client1.guilds:
        text += f"{guild.name}\n{guild.id}\n{guild.owner}\n\n"
    text += f"以上{len(client1.guilds)}鯖"
    await message.channel.send(embed=discord.Embed(title="参加鯖一覧", description=text))


async def accept(message, client1):
    """
    新規役職剥奪用関数"""

    new_role = message.guild.get_role(621641465105481738)
    accept_able_role = message.guild.get_role(626062897633689620)
    crafter_role = message.guild.get_role(586123363513008139)

    if not new_role in message.author.roles:
        await message.channel.send("もう新規役職付いてないよ^^")
        return

    if not accept_able_role in message.author.roles:
        await message.channel.send("まず<#640833025822949387>をお願いします\nマイクラJava版を所持していない場合はお手数ですがKirisameKeiまでご連絡ください。")
        return

    if not message.channel.id == 592581835343659030:
        await message.channel.send("説明読みました？チャンネル違いますよ？")
        return

    mojiretsu = create_pic_capcha()

    connection = MySQLdb.connect(
        host=os.getenv("mysql_host"),
        user=os.getenv("mysql_user"),
        passwd=os.getenv("mysql_passwd"),
        db="capcha"
    )
    cursor = connection.cursor()
    cursor.execute(f"insert into capcha_tbl (user_id, moji) values ({message.author.id}, '{mojiretsu}')")
    connection.commit()
    cursor.close()
    connection.close()

    file = discord.File("capcha.png")
    msg = await message.channel.send(
        content=f"{message.author.mention}\nお読みください(ひらがな5文字)\n60秒無言でタイムアウト\nリアクションで画像変更",
        file=file
    )
    await msg.add_reaction("🔄")

    def check1(m):
        return (m.channel == message.channel and m.author.id == message.author.id) or\
                (m.channel == message.channel and m.author.id == client1.user.id)

    while True:
        try:
            reply = await client1.wait_for("message", check=check1, timeout=60)
        except asyncio.TimeoutError:
            await message.channel.send(f"{message.author.mention}\nタイムアウトしました。acceptコマンドを打つところからやり直してください。")
            connection = MySQLdb.connect(
                host=os.getenv("mysql_host"),
                user=os.getenv("mysql_user"),
                passwd=os.getenv("mysql_passwd"),
                db="capcha"
            )
            cursor = connection.cursor()
            cursor.execute(f"delete from capcha_tbl where user_id={message.author.id}")
            connection.commit()
            cursor.close()
            connection.close()
            return

        connection = MySQLdb.connect(
            host=os.getenv("mysql_host"),
            user=os.getenv("mysql_user"),
            passwd=os.getenv("mysql_passwd"),
            db="capcha"
        )
        cursor = connection.cursor()
        cursor.execute(f"select moji from capcha_tbl where user_id={message.author.id}")
        result = cursor.fetchall()
        right_mojiretsu = result[0][0]
        cursor.close()
        connection.close()

        if reply.author.id == client1.user.id:
            pass #タイマーリセット
        elif reply.content == right_mojiretsu:
            connection = MySQLdb.connect(
                host=os.getenv("mysql_host"),
                user=os.getenv("mysql_user"),
                passwd=os.getenv("mysql_passwd"),
                db="capcha"
            )
            cursor = connection.cursor()
            cursor.execute(f"delete from capcha_tbl where user_id={message.author.id}")
            connection.commit()
            cursor.close()
            connection.close()
            break
        else:
            await message.channel.send(f"{message.author.mention}\n違います。やり直してください。\n読めない場合は🔄をリアクションすることで画像を変更できます")

    await message.channel.send(
        f"{message.author.mention}\nあなたはたぶん人間です。第一認証を突破しました。\n"
        "次の文章をひらがなで書いてください。```\n一月一日日曜日、今日は元日です。```"
    )

    def check2(m):
        return m.author == message.author

    for i in range(3):
        try:
            reply = await client1.wait_for("message", check=check2, timeout=120)
        except asyncio.TimeoutError:
            await message.channel.send("タイムアウトしました。acceptコマンドを打つところからやり直してください。")
            return
        answer_filter = re.compile(r"いちがつ(ついたち|いちにち)にちようび(、|,|，|)(きょう|こんにち|こんじつ)はがんじつです(。|.|．|)")
        if answer_filter.fullmatch(reply.content):
            await message.author.remove_roles(new_role)
            await message.author.remove_roles(accept_able_role)
            await message.author.add_roles(crafter_role)
            await message.channel.send(
                f"{message.author.mention}\nあなたはたぶん日本語ユーザーです。第二認証を突破しました。\n"
                f"改めまして{message.author.name}さんようこそ{message.guild.name}へ！\n"
                "<#664286990677573680>に自分がほしい役職があったらぜひ付けてみてください！\n"
                "もしよろしければ<#586571234276540449>もしていただけると嬉しいです！"
            )
            return
        else:
            if i != 2:
                description = "そうは読まないと思います。もう一度書いてみてください。"
                if "がんたん" in reply.content:
                    description += "\nそれ本当に「元旦(がんたん)」ですか？落ち着いてよく見てみましょう"
                await message.channel.send(f"{message.author.mention}\n{description}")

    await message.channel.send(
        f"{message.author.mention}\n"
        "3回間違えました。You made mistake 3 times.\n"
        "日本語のお勉強を頑張りましょう。Please study Japanese.\n"
        '日本語が分かるようになったら再度acceptしてください。Type "/accept" when you can understand Japanese.'
    )


async def marichan_invite(message):
    """
    魔理沙bot招待コマンドが実行されたとき用の関数"""

    await message.delete()
    await message.channel.send("コマンド漏洩防止のためコマンドを削除しました", delete_after=5)

    invite_url = os.getenv("marichan_invite_url")
    try:
        await message.author.send(invite_url)
        marichan_inviter_role = message.guild.get_role(663542711290429446) #魔理沙bot導入者
        await message.author.add_roles(marichan_inviter_role)
    except discord.errors.Forbidden:
        await message.channel.send("権限エラー。DMを解放してください。")
        return

    await message.channel.send("DMに招待urlを送信しました。管理者権限を持っているサーバに入れられます。")


async def delmsg(message, client1, command):
    """
    管理者持ちが実行したら実行チャンネルのメッセージを削除する
    管理者なしが実行したら怒ってドM役職を付ける"""

    if message.author.bot:
        return

    admin_role = message.guild.get_role(585999549055631408)
    if not (admin_role in message.author.roles):
        await message.channel.send("何様のつもり？")
        doM_role = message.guild.get_role(616212704818102275)
        await message.author.add_roles(doM_role)
        return

    if command == "delmsg":
        msg = await message.channel.send("このチャンネルのメッセージを**全削除**しようとしています\nよろしいですか？")
        await msg.add_reaction("👍")
        await msg.add_reaction("👎")
        def check(reaction, user):
            return user == message.author and (str(reaction.emoji) == "👍" or str(reaction.emoji) == "👎")
        try:
            reply = await client1.wait_for("reaction_add", check=check, timeout=60)
        except asyncio.TimeoutError:
            await message.channel.send("タイムアウトしました。最初からやり直してください")
            return

        reaction = reply[0]
        if str(reaction.emoji) == "👎":
            await message.channel.send("キャンセルしました")
            return

        await message.channel.purge(limit=None)
        return

    try:
        arg_No1 = command.split()[1]
    except IndexError:
        await message.channel.send("コマンドが間違っています")
        return

    if arg_No1 == "area":
        try:
            start_msg_id = int(command.split()[2])
            end_msg_id = int(command.split()[3])
        except ValueError:
            await message.channel.send("不正な引数です\nヒント:`/delmsg n` or `/delmsg area msgID msgID`")
            return
        start_msg = await message.channel.fetch_message(start_msg_id)
        end_msg = await message.channel.fetch_message(end_msg_id)
        if start_msg is None or end_msg is None:
            await message.channel.send("そのメッセージは存在しません")
            return
        start_msg_time = start_msg.created_at
        end_msg_time = end_msg.created_at
        await message.channel.purge(after=start_msg_time, before=end_msg_time)
        return

    try:
        how_many_del = int(arg_No1)
    except ValueError:
        await message.channel.send("不正な引数です\nヒント:`/delmsg␣n` or `/delmsg␣area␣msgID␣msgID`")
        return

    await message.channel.purge(limit=how_many_del+1)


async def edit_mcid(message, command):
    """
    登録されているMCIDを編集(追加/削除)する関数"""

    if message.author.bot:
        return

    admin_role = message.guild.get_role(585999549055631408)
    if not (admin_role in message.author.roles):
        await message.channel.send("何様のつもり？")
        doM_role = message.guild.get_role(616212704818102275)
        await message.author.add_roles(doM_role)
        return

    try:
        operation = command.split()[1]
        user_id = int(command.split()[2])
        mcid = command.split()[3].replace("\\", "")
    except ValueError:
        await message.channel.send("userIDとして成り立ちません")
        return
    except IndexError:
        await message.channel.send("引数が足りません\nヒント: `/mcid␣[add, del]␣userid␣MCID`")
        return

    p = re.compile(r"^[a-zA-Z0-9_]+$")
    if not p.fullmatch(mcid):
        await message.channel.send("MCID編集に使えない文字が含まれています")
        return

    if operation == "add":
        if not check_mcid_length(mcid):
            mcid = mcid.replace("_", "\_")
            await message.channel.send(f"{mcid}はMCIDとして成り立ちません")
            return

        if not check_mcid_yet(mcid):
            mcid = mcid.replace("_", "\_")
            await message.channel.send(f"{mcid}は既に登録されています")
            return

        mcid_uuid_tuple = check_mcid_exist(mcid)
        if mcid_uuid_tuple is None:
            await message.channel.send("現在データ参照元が使用できない状態です。しばらくたってからもう一度お試しください。")
            return

        if not mcid_uuid_tuple:
            await message.channel.send("存在しないMCIDです")
            return

        mcid = mcid_uuid_tuple[0]
        uuid = mcid_uuid_tuple[1]
        with open("./datas/user_data.json", mode="r", encoding="utf-8") as f:
            user_data_dict = json.load(f)

        try:
            user_data = user_data_dict[f"{user_id}"]
        except KeyError:
            user_data_dict[f"{user_id}"] = {"ban": False, "role": [], "mcid": [], "point": 0, "speak": 0}
            user_data = user_data_dict[f"{user_id}"]
        mcid_list = user_data["mcid"]

        mcid_list.append(mcid)

        connection = MySQLdb.connect(
            host=os.getenv("mysql_host"),
            user=os.getenv("mysql_user"),
            passwd=os.getenv("mysql_passwd"),
            db=os.getenv("mysql_db_name")
        )
        cursor = connection.cursor()
        cursor.execute(f"insert into uuids (id, uuid, mcid) values ({user_id}, '{uuid}', '{mcid}')")
        connection.commit()
        cursor.close()
        connection.close()

        user_data_json = json.dumps(user_data_dict, indent=4)
        with open("./datas/user_data.json", mode="w", encoding="utf-8") as f:
            f.write(user_data_json)

        member_name = message.guild.get_member(user_id).name
        mcid = mcid.replace("_", "\_")
        await message.channel.send(f"{member_name}のMCIDに{mcid}を追加しました")

    elif operation == "del":
        with open("./datas/user_data.json", mode="r", encoding="utf-8") as f:
            user_data_dict = json.load(f)

        try:
            user_data = user_data_dict[f"{user_id}"]
        except KeyError:
            user_data_dict[f"{user_id}"] = {"ban": False, "role": [], "mcid": [], "point": 0, "speak": 0}
            user_data = user_data_dict[f"{user_id}"]
        mcid_list = user_data["mcid"]

        deleted = False
        for registered_mcid in mcid_list:
            if registered_mcid.lower() == mcid.lower():
                mcid_list.remove(registered_mcid)
                deleted = True
                break

        if not deleted:
            member_name = message.guild.get_member(user_id).name
            mcid = mcid.replace("_", "\_")
            await message.channel.send(f"{member_name}は{mcid}というMCIDを登録していません")
            return

        connection = MySQLdb.connect(
            host=os.getenv("mysql_host"),
            user=os.getenv("mysql_user"),
            passwd=os.getenv("mysql_passwd"),
            db=os.getenv("mysql_db_name")
        )
        cursor = connection.cursor()
        cursor.execute(f"delete from uuids where mcid='{mcid}'")
        connection.commit()
        cursor.close()
        connection.close()

        user_data_json = json.dumps(user_data_dict, indent=4)
        with open("./datas/user_data.json", mode="w", encoding="utf-8") as f:
            f.write(user_data_json)

        member_name = message.guild.get_member(user_id).name
        mcid = mcid.replace("_", "\\_")
        await message.channel.send(f"{member_name}のMCID、{mcid}を削除しました")

    else:
        await message.channel.send("第一引数が不正です\nヒント: `/mcid␣[add, del]␣userid␣MCID`")


async def point(message, command):
    """
    第一引数：操作(付与、剥奪、セット、補償、合計算出)
    第二引数：対象のID(sumでは不要)
    第三引数(crd、sumでは不要)：pt"""

    if message.author.bot:
        return

    admin_role = message.guild.get_role(585999549055631408)
    if not (admin_role in message.author.roles):
        await message.channel.send("何様のつもり？")
        doM_role = message.guild.get_role(616212704818102275)
        await message.author.add_roles(doM_role)
        return

    operation = command.split()[1]

    with open("./datas/user_data.json", mode="r", encoding="utf-8") as f:
        user_data_dict = json.load(f)

    if operation == "sum":

        pt = 0
        for user_data in user_data_dict.values():
            pt += user_data["point"]

        lc, amari = divmod(pt, 3456)
        st, ko = divmod(amari, 64)

        await message.channel.send(f"合計{pt}pt({lc}LC+{st}st+{ko})")
        return

    try:
        user_id = int(command.split()[2])
    except IndexError:
        await message.channel.send("引数が足りません\nヒント：/pt␣[add, use, set, crd, sum]␣ID␣(n(n≧0))")
        return
    except ValueError:
        await message.channel.send("ユーザーIDは半角数字です")
        return

    if operation == "crd":
        member = message.guild.get_member(user_id)
        if member is None:
            await message.channel.send("そんな人この鯖にいません")
            return

        kouho_tuple = ("おめでとう！", "はずれ", "はずれ")
        touraku = random.choice(kouho_tuple)
        if touraku == "はずれ":
            await message.channel.send(f"{member.name}への補填結果: {touraku}")
            return

        get_pt = random.randint(1,32)
        
        with open("./datas/user_data.json", mode="r", encoding="utf-8") as f:
            user_data_dict = json.load(f)
        
        try:
            before_pt = user_data_dict[f"{member.id}"]["point"]
        except KeyError:
            user_data_dict[f"{member.id}"] = {"ban": False, "role": [], "mcid": [], "point": 0, "speak": 0}
            before_pt = user_data_dict[f"{member.id}"]["point"]

        user_data_dict[f"{member.id}"]["point"] = before_pt + get_pt

        user_data_json = json.dumps(user_data_dict, indent=4)
        with open("./datas/user_data.json", mode="w", encoding="utf-8") as f:
            f.write(user_data_json)
        
        await message.channel.send(f"{member.name}への補填結果: {touraku}{get_pt}ptゲット！\n{member.name}の保有pt: {before_pt}→{before_pt+get_pt}")
        return

    try:
        pt = int(command.split()[3])
    except IndexError:
        await message.channel.send("引数が足りません\nヒント：/pt␣[add, use, set, crd, sum]␣ID␣(n(n≧0))")
        return
    except ValueError:
        await message.channel.send("add/use/setするpt数がが不正です\nヒント：/pt␣[add, use, set, crd, sum]␣ID␣(n(n≧0))")
        return

    if pt < 0:
        await message.channel.send("負の値を扱うことはできません。")
        return

    if operation == "add":
        member = message.guild.get_member(user_id)
        if member is None:
            await message.channel.send("そんな人この鯖にいません")
            return

        try:
            before_pt = user_data_dict[f"{member.id}"]["point"]
        except KeyError:
            user_data_dict[f"{member.id}"] = {"ban": False, "role": [], "mcid": [], "point": 0, "speak": 0}
            before_pt = user_data_dict[f"{member.id}"]["point"]

        after_pt = before_pt + pt

    elif operation == "use":
        member = message.guild.get_member(user_id)
        if member is None:
            await message.channel.send("そんな人この鯖にいません")
            return

        try:
            before_pt = user_data_dict[f"{member.id}"]["point"]
        except KeyError:
            user_data_dict[f"{member.id}"] = {"ban": False, "role": [], "mcid": [], "point": 0, "speak": 0}
            before_pt = user_data_dict[f"{message.author.id}"]["point"]

        if (before_pt-pt) < 0:
            await message.channel.send(f"ptが足りません\n{member.name}の保有pt: {before_pt}")
            return

        after_pt = before_pt - pt

    elif operation == "set":
        member = message.guild.get_member(user_id)
        if member is None:
            await message.channel.send("そんな人この鯖にいません")
            return

        try:
            before_pt = user_data_dict[f"{member.id}"]["point"]
        except KeyError:
            user_data_dict[f"{member.id}"] = {"ban": False, "role": [], "mcid": [], "point": 0, "speak": 0}
            before_pt = user_data_dict[f"{member.id}"]["point"]

        after_pt = pt

    else:
        await message.channel.send("引数が不正です\nヒント：`/pt␣[add, use, set, crd, sum]␣ID␣(n(n≧0))`")
        return

    user_data_dict[f"{member.id}"]["point"] = after_pt
    user_data_json = json.dumps(user_data_dict, indent=4)
    with open("./datas/user_data.json", mode="w", encoding="utf-8") as f:
        f.write(user_data_json)

    await message.channel.send(f"{member.name}の保有pt: {before_pt}→{after_pt}")


async def remove_role(message, command):
    """
    引数のIDを持つ役職を一斉に外す"""

    if message.author.bot:
        return

    admin_role = message.guild.get_role(585999549055631408)
    if not (admin_role in message.author.roles):
        await message.channel.send("何様のつもり？")
        doM_role = message.guild.get_role(616212704818102275)
        await message.author.add_roles(doM_role)
        return

    try:
        role_id = int(command.split()[1])
    except ValueError:
        await message.channel.send("不正な引数です\nヒント:`/remove_role␣roleID`")
        return

    role = message.guild.get_role(role_id)
    n = 0
    for mem in role.members:
        try:
            await mem.remove_roles(role)
            n += 1
        except discord.errors.Forbidden:
            pass

    await message.channel.send(f"{n}人から@{role.name}を剝奪しました")


async def send_zip_data(message):
    """
    データ類を全部引っ張ってくる関数"""

    if not message.author.id == 523303776120209408:
        await message.channel.send("何様のつもり？")
        doM_role = message.guild.get_role(616212704818102275)
        await message.author.add_roles(doM_role)
        return

    shutil.make_archive("datas", format="zip", base_dir="./datas")
    f = discord.File("datas.zip")
    await message.author.send(file=f)


async def before_ban(message, client1, command):
    """
    第一引数のIDを持つユーザーを事前BANする関数"""

    if not message.author.id == 523303776120209408:
        await message.channel.send("何様のつもり？")
        doM_role = message.guild.get_role(616212704818102275)
        await message.author.add_roles(doM_role)
        return

    try:
        user_id = int(command.split()[1])
    except ValueError:
        await message.channel.send("不正な引数です")
        return

    try:
        banned_user = await client1.fetch_user(user_id)
    except discord.errors.NotFound:
        await message.channel.send("IDが間違っています")
        return

    with open("./datas/user_data.json", mode="r", encoding="utf-8") as f:
        user_data_dict = json.load(f)

    try:
        user_data = user_data_dict[f"{user_id}"]
        if user_data["ban"]:
            await message.channel.send(f"{banned_user.name}は既にBANされています")
            return
    except KeyError:
        pass

    user_info_embed = discord.Embed(title="以下のユーザーを事前BANしますか？", description="はい(BANする): 👍\nいいえ(ミス): 👎", color=0x000000)
    user_info_embed.set_thumbnail(url=banned_user.display_avatar.url)
    user_info_embed.add_field(name=".", value=banned_user.name)
    msg = await message.channel.send(embed=user_info_embed)
    await msg.add_reaction("👍")
    await msg.add_reaction("👎")
    def check(reaction, user):
        return user == message.author and (str(reaction.emoji) == "👍" or str(reaction.emoji) == "👎")
    try:
        reply = await client1.wait_for("reaction_add", check=check, timeout=60)
    except asyncio.TimeoutError:
        await message.channel.send("タイムアウトしました。最初からやり直してください")
        return

    else:
        if str(reply[0].emoji) == "👎":
            await message.channel.send("キャンセルしました")
            return

        try:
            user_data = user_data_dict[f"{user_id}"]
        except KeyError:
            user_data_dict[f"{user_id}"] = {"ban": False, "role": [], "mcid": [], "point": 0, "speak": 0}
            user_data = user_data_dict[f"{user_id}"]

        user_data["ban"] = True

        user_data_json = json.dumps(user_data_dict, indent=4)
        with open("./datas/user_data.json", mode="w", encoding="utf-8") as f:
            f.write(user_data_json)

        await message.channel.send(f"{banned_user.name}を事前BANしました")


async def unban(message, client1, command):
    """
    第一引数のIDを持つユーザーの事前BANを解除する関数"""

    if not message.author.id == 523303776120209408:
        await message.channel.send("何様のつもり？")
        doM_role = message.guild.get_role(616212704818102275)
        await message.author.add_roles(doM_role)
        return

    try:
        user_id = int(command.split()[1])
    except ValueError:
        await message.channel.send("不正な引数です")
        return

    try:
        banned_user = await client1.fetch_user(user_id)
    except discord.errors.NotFound:
        await message.channel.send("IDが間違っています")
        return

    with open("./datas/user_data.json", mode="r", encoding="utf-8") as f:
        user_data_dict = json.load(f)

    try:
        user_data = user_data_dict[f"{user_id}"]
        if not user_data["ban"]:
            await message.channel.send(f"{banned_user.name}は事前BANされていません")
            return
    except KeyError:
        await message.channel.send("そのユーザーIDは登録されていません")
        return

    user_info_embed = discord.Embed(title="以下のユーザーの事前BANを解除しますか？", description="はい(解除): 👍\nいいえ(ミス): 👎", color=0x000000)
    user_info_embed.set_thumbnail(url=banned_user.display_avatar.url)
    user_info_embed.add_field(name=".", value=banned_user.name)
    msg = await message.channel.send(embed=user_info_embed)
    await msg.add_reaction("👍")
    await msg.add_reaction("👎")
    def check(reaction, user):
        return user == message.author and (str(reaction.emoji) == "👍" or str(reaction.emoji) == "👎")
    try:
        reply = await client1.wait_for("reaction_add", check=check, timeout=60)
    except asyncio.TimeoutError:
        await message.channel.send("タイムアウトしました。最初からやり直してください")
        return

    else:
        if str(reply[0].emoji) == "👎":
            await message.channel.send("キャンセルしました")
            return

        user_data_dict[f"{user_id}"]["ban"] = False
        user_data_json = json.dumps(user_data_dict, indent=4)
        with open("./datas/user_data.json", mode="w", encoding="utf-8") as f:
            f.write(user_data_json)

        await message.channel.send(f"{banned_user.name}の事前BANを解除しました")


async def delete_user_data(message, client1, command):
    """
    ユーザーデータのすべてを抹消する"""

    if not message.author.id == 523303776120209408:
        await message.channel.send("何様のつもり？")
        doM_role = message.guild.get_role(616212704818102275)
        await message.author.add_roles(doM_role)
        return

    try:
        user_id = int(command.split()[1])
    except ValueError:
        await message.channel.send("不正な引数です")
        return

    with open("./datas/user_data.json", mode="r", encoding="utf-8") as f:
        user_data_dict = json.load(f)

    if not str(user_id) in user_data_dict.keys():
        await message.channel.send("そのデータは登録されていません")
        return

    try:
        delete_user = await client1.fetch_user(user_id)
    except discord.errors.NotFound:
        await message.channel.send("IDが間違っていますがデータはあるので消しておきます(どうゆう状況だよおい)")
        delete_user_name = "None"
    else:
        user_info_embed = discord.Embed(title="以下のユーザーのデータをすべて抹消しますか？", description="はい(抹消): 👍\nいいえ(ミス): 👎", color=0x000000)
        user_info_embed.set_thumbnail(url=delete_user.display_avatar.url)
        user_info_embed.add_field(name=".", value=delete_user.name)
        msg = await message.channel.send(embed=user_info_embed)
        await msg.add_reaction("👍")
        await msg.add_reaction("👎")
        def check(reaction, user):
            return user == message.author and (str(reaction.emoji) == "👍" or str(reaction.emoji) == "👎")
        try:
            reply = await client1.wait_for("reaction_add", check=check, timeout=60)
        except asyncio.TimeoutError:
            await message.channel.send("タイムアウトしました。最初からやり直してください")
            return

        else:
            if str(reply[0].emoji) == "👎":
                await message.channel.send("キャンセルしました")
                return
            else:
                delete_user_name = delete_user.name

    del user_data_dict[f"{user_id}"]

    user_data_json = json.dumps(user_data_dict, indent=4)
    with open("./datas/user_data.json", mode="w", encoding="utf-8") as f:
        f.write(user_data_json)

    await message.channel.send(f"{delete_user_name}のデータを全て抹消しました")


async def ban_list(message, client1):
    """
    事前BANしている人のリスト"""

    if not message.author.id == 523303776120209408:
        await message.channel.send("何様のつもり？")
        doM_role = message.guild.get_role(616212704818102275)
        await message.author.add_roles(doM_role)
        return

    await message.channel.send("時間かかりますよ")

    with open("./datas/user_data.json", mode="r", encoding="utf-8") as f:
        user_data_dict = json.load(f)

    banned_user = ""
    i = 0
    for user_id in user_data_dict:
        if user_data_dict[user_id]["ban"]:
            user = await client1.fetch_user(int(user_id))
            banned_user += f"{user} <@{user_id}>\n"
            i +=1
    banned_user += f"\n以上{i}アカ"
    await message.channel.send(embed=discord.Embed(title="事前BAN", description=banned_user))


async def gban_list(message):
    """
    魔理沙はこのサーバには入りません"""

    if not message.author.id == 523303776120209408:
        await message.channel.send("何様のつもり？")
        doM_role = message.guild.get_role(616212704818102275)
        await message.author.add_roles(doM_role)
        return

    with open("./datas/ban_server.json", mode="r", encoding="utf-8") as f:
        ban_server_dict = json.load(f)

    text = ""
    for banned_server_id, banned_server_data in ban_server_dict.items():
        text += f"ServerID: {banned_server_id}\nServerName: {banned_server_data[0]}\nOwnerID: {banned_server_data[2]}\nOwnerName: {banned_server_data[1]}\n\n"

    await message.channel.send(text)


async def global_notice(message, client1, command):
    """
    導入サーバすべてのお知らせチャンネルにお知らせを送信"""

    if not message.author.id == 523303776120209408:
        await message.channel.send("何様のつもり？")
        doM_role = message.guild.get_role(616212704818102275)
        await message.author.add_roles(doM_role)
        return

    msg = command.replace("global_notice ", "")

    with open("./datas/marisa_notice.json", mode="r", encoding="utf-8") as f:
        marisa_notice_dict = json.load(f)

    for guild in client1.guilds:
        try:
            notice_ch_id = marisa_notice_dict[f"{guild.id}"]
        except KeyError:
            marisa_notice_dict[f"{guild.id}"] = None
            notice_ch = None
            notice_ch_id = None
        else:
            notice_ch = guild.get_channel(notice_ch_id)

        if notice_ch_id == "rejected":
            await message.channel.send(f"{guild.name}は通知を拒否しています")

        elif notice_ch is None:
            flag = False
            for ch in guild.text_channels:
                try:
                    await ch.send(msg)
                    marisa_notice_dict[f"{guild.id}"] = ch.id
                    flag = True
                    break
                except discord.errors.Forbidden:
                    pass
            if not flag:
                try:
                    await guild.owner.send(f"{guild.name}に{client1.user.name}が発言できるチャンネルがありません。以下の内容をサーバメンバーに周知してください\n\n{msg}")
                except discord.errors.Forbidden:
                    await message.channel.send(f"{guild.name}に通知できませんでした")

        else:
            try:
                await notice_ch.send(msg)
            except discord.errors.Forbidden:
                flag = False
                for ch in guild.text_channels:
                    try:
                        await ch.send(msg)
                        marisa_notice_dict[f"{guild.id}"] = ch.id
                        flag = True
                        break
                    except discord.errors.Forbidden:
                        pass
                if not flag:
                    try:
                        await guild.owner.send(f"{guild.name}に{client1.user.name}が発言できるチャンネルがありません。以下の内容をサーバメンバーに周知してください\n\n{msg}")
                    except discord.errors.Forbidden:
                        await message.channel.send(f"{guild.name}に通知できませんでした")

    marisa_notice_json = json.dumps(marisa_notice_dict, indent=4)
    with open("./datas/marisa_notice.json", mode="w", encoding="utf-8") as f:
        f.write(marisa_notice_json)

    await message.channel.send("全サーバに通知完了")


async def leave_guild(message, client1, command):
    """
    サーバから抜ける"""

    if not message.author.id == 523303776120209408:
        await message.channel.send("何様のつもり？")
        doM_role = message.guild.get_role(616212704818102275)
        await message.author.add_roles(doM_role)
        return

    try:
        guild_id = int(command.split()[1])
        reason = command.split()[2]
    except ValueError:
        await message.channel.send("intキャストできる形で入力してください")
        return
    except IndexError:
        await message.channel.send("サーバから抜ける理由を書いてください")
        return

    guild = client1.get_guild(guild_id)
    embed = discord.Embed(
        title="以下のサーバから抜け、サーバをブラックリスト登録しますか？",
        description="はい(離脱&ブラックリスト登録): 👍\nはい(離脱のみ): 👋\nいいえ(ミス): 👎",
        color=0xff0000
    )
    embed.set_author(name=guild.name, icon_url=guild.icon)
    embed.set_footer(text=guild.owner.name, icon_url=guild.owner.display_avatar.url)
    msg = await message.channel.send(embed=embed)
    await msg.add_reaction("👍")
    await msg.add_reaction("👋")
    await msg.add_reaction("👎")
    def check(reaction, user):
        return user == message.author and (str(reaction.emoji) == "👍" or str(reaction.emoji) == "👋" or str(reaction.emoji) == "👎")
    try:
        reply = await client1.wait_for("reaction_add", check=check, timeout=60)
    except asyncio.TimeoutError:
        await message.channel.send("タイムアウトしました。最初からやり直してください")
        return

    else:
        if str(reply[0].emoji) == "👎":
            await message.channel.send("キャンセルしました")
            return

        if guild.owner.id == 523303776120209408:
            await message.channel.send("あんた正気か？")
            return

        with open("./datas/marisa_notice.json", mode="r", encoding="utf-8") as f:
            marisa_notice_dict = json.load(f)

        notice_ch = client1.get_channel(marisa_notice_dict[f"{guild.id}"])
        if notice_ch is None:
            flag = False
            for ch in guild.text_channels:
                try:
                    await ch.send(f"{client1.user.name}はこのサーバを抜けます\nReason: {reason}")
                    flag = True
                    break
                except discord.errors.Forbidden:
                    pass

            if not flag:
                try:
                    await guild.owner.send(f"{client1.user.name}は{guild.name}を抜けます\nReason: {reason}")
                except discord.errors.Forbidden:
                    await message.channel.send(f"{guild.name}に通知できませんでした")

        else:
            await notice_ch.send(f"{client1.user.name}はこのサーバを抜けます\nReason: {reason}")

        await guild.leave()
        await message.channel.send(f"{guild.name}から退出しました")

        if str(reply[0].emoji) == "👋":
            return

        with open("./datas/ban_server.json", mode="r", encoding="utf-8") as f:
            ban_server_dict = json.load(f)

        ban_server_dict[f"{guild_id}"] = [guild.name, guild.owner.name, guild.owner.id]

        ban_server_json = json.dumps(ban_server_dict, indent=4, ensure_ascii=False)
        with open("./datas/ban_server.json", mode="w", encoding="utf-8") as f:
            f.write(ban_server_json)

#ーーーーここまでコマンド、以下補助関数ーーーー

def check_mcid_length(mcid):
    """
    申請されたMCIDがMCIDとして成り立つかチェックする
    boolを返す"""

    if len(mcid) >= 3 and len(mcid) <= 16:
        return True
    else:
        return False


def check_mcid_yet(mcid):
    """
    申請されたMCIDが未登録MCIDかチェックする
    boolを返す"""

    with open("./datas/user_data.json", mode="r", encoding="utf-8") as f:
        user_data_dict = json.load(f)

    for user_id in user_data_dict:
        for mcid_registered in user_data_dict[user_id]["mcid"]:
            if mcid.lower() == mcid_registered.lower():
                return False
    return True


def check_mcid_exist(mcid):
    """
    存在するかをチェックする
    boolまたはNoneを返す
    mojangAPIに問い合わせる"""

    url = f"http://api.mojang.com/users/profiles/minecraft/{mcid}"
    try:
        res = requests.get(url)
        res.raise_for_status()
        try:
            res = res.json()
        except json.decoder.JSONDecodeError:
            return False
        else:
            mcid = res["name"]
            uuid = res["id"]
            return (mcid, uuid)

    except requests.exceptions.HTTPError:
        return None


def create_pic_capcha():
    hiragana_tuple = (
        "あ", "い", "う", "え", "お",
        "か", "き", "く", "け", "こ",
        "さ", "し", "す", "せ", "そ",
        "た", "ち", "つ", "て", "と",
        "な", "に", "ぬ", "ね", "の",
        "は", "ひ", "ふ", "へ", "ほ",
        "ま", "み", "む", "め", "も",
        "や", "ゆ", "よ",
        "ら", "り", "る", "れ", "ろ",
        "わ", "を", "ん"
    )
    image = Image.new("RGB", (250, 70), color=0x000000)
    picture = ImageDraw.Draw(image)
    mojiretsu = random.sample(hiragana_tuple, k=5)
    x = 0
    for moji in mojiretsu:
        font =  ImageFont.truetype(random.choice(["cghkm_V6.ttc", "jwyz00b_V6.ttc"]), size=50)
        y = random.randint(-10, 10)
        picture.text((x, 10+y), text=moji, font=font, fill=0xffffff)
        x += 50

    picture.line((0, random.randint(10, 60), 250, random.randint(10, 60)), fill=0xffffff, width=4)
    image.save("capcha.png")
    return "".join(mojiretsu)