import datetime
import json
import math
import random
import os

import discord
import MySQLdb
from PIL import Image, ImageDraw, ImageFont

async def simple_kikaku_join(message):
    """
    報告済みのMCIDを入力した場合企画参加者役職を付与"""

    if message.author.bot:
        return

    kikaku_role = message.guild.get_role(668021019700756490) #企画参加者

    if message.content == "/cancel":
        if kikaku_role in message.author.roles:
            await message.author.remove_roles(kikaku_role)
            await message.channel.send(f"{message.author.name}さんがキャンセルしました")
        else:
            await message.channel.send(f"{message.author.name}さんはまだ企画に参加していません")
        return

    now = datetime.datetime.now()
    finish_time = datetime.datetime(2023, 11, 19, 12, 0)
    if now >= finish_time:
        await message.channel.send("現在企画は行われていません")
        return

    if kikaku_role in message.author.roles:
        await message.channel.send(f"{message.author.name}さんは既に参加しています")
        return

    mcid = message.content.replace("\\", "")
    with open("./datas/user_data.json", mode="r", encoding="utf-8") as f:
        user_data_dict = json.load(f)

    try:
        mcid_list = user_data_dict[f"{message.author.id}"]["mcid"]
    except KeyError:
        user_data_dict[f"{message.author.id}"] = {"ban": False, "role": [], "mcid": [], "point": 0, "speak": 0}
        mcid_list = user_data_dict[f"{message.author.id}"]["mcid"]

    flag = False
    for registered_mcid in mcid_list:
        if mcid.lower() == registered_mcid.lower():
            flag = True
            break

    if not flag:
        mcid_list = str(mcid_list).replace("_", "\_")
        await message.channel.send(f"そのMCIDは登録されていません。\n現在登録されているMCID{mcid_list}")
        return

    await message.author.add_roles(kikaku_role)
    await message.channel.send(f"{message.author.name}さんが参加しました")


async def seichi_taikai_join(message):
    """
    MCIDごとに参加申請を行う
    1アカ以上参加登録されている場合企画参加者を付与
    整地大会用"""

    if message.author.bot:
        return

    kikaku_role = message.guild.get_role(668021019700756490)

    if message.content.startswith("/cancel"):
        with open("./datas/seichi_taikai.json", mode="r", encoding="utf-8") as f:
            kikaku_data_dict = json.load(f)

        simple = False
        try:
            cancel_mcid = message.content.split()[1].replace("\\", "")
        except IndexError:
            cancel_mcid = None
            simple = True

        mcid_list = []
        counter = 0
        uuid = None
        uuid_only = None
        for key, value in kikaku_data_dict.items():
            if value["user_id"] == message.author.id:
                mcid_list.append(value["mcid"])
                mcid = value["mcid"].replace("_", "\_")
                uuid = key
                counter += 1

                if not simple and cancel_mcid == value["mcid"]:
                    uuid_only = key

        if simple and counter == 1:
            del kikaku_data_dict[uuid]
        elif simple and counter != 1:
            await message.channel.send(f"あなたは複数アカウントで参加登録をしています。`/cancel MCID`で1アカウントずつ辞退申請をしてください\n現在あなたが参加申請しているアカウント: {mcid_list}")
            return
        elif not simple:
            try:
                del kikaku_data_dict[uuid_only]
            except KeyError:
                await message.channel.send(f"そのMCIDは参加申請されていません。\n現在あなたが参加申請しているアカウント: {mcid_list}")
                return

        kikaku_data_json = json.dumps(kikaku_data_dict, indent=4)
        with open("./datas/seichi_taikai.json", mode="w", encoding="utf-8") as f:
            f.write(kikaku_data_json)

        if counter == 1:
            await message.author.remove_roles(kikaku_role)
        if cancel_mcid is None:
            await message.channel.send(f"{mcid}の参加登録を取り消しました")
        else:
            await message.channel.send(f"{cancel_mcid}の参加登録を取り消しました")
        return

    now = datetime.datetime.now()
    finish_time = datetime.datetime(2023, 7, 29, 23, 55)
    if now >= finish_time:
        await message.channel.send("参加締め切り時刻を過ぎています")
        return

    mcid = message.content.replace("\\", "")
    with open("./datas/user_data.json", mode="r", encoding="utf-8") as f:
        user_data_dict = json.load(f)

    try:
        mcid_list = user_data_dict[f"{message.author.id}"]["mcid"]
    except KeyError:
        user_data_dict[f"{message.author.id}"] = {"ban": False, "role": [], "mcid": [], "point": 0, "speak": 0}
        mcid_list = user_data_dict[f"{message.author.id}"]["mcid"]

    flag = False
    for registered_mcid in mcid_list:
        if mcid.lower() == registered_mcid.lower():
            flag = True
            break

    if not flag:
        mcid_list = str(mcid_list).replace("_", "\_")
        await message.channel.send(f"そのMCIDは登録されていません。\n現在登録されているMCID{mcid_list}")
        return

    connection = MySQLdb.connect(
        host=os.getenv("mysql_host"),
        user=os.getenv("mysql_user"),
        passwd=os.getenv("mysql_passwd"),
        db=os.getenv("mysql_db_name")
    )
    cursor = connection.cursor()
    cursor.execute(f"select uuid from uuids where mcid='{mcid}'")
    result = cursor.fetchall()
    uuid = result[0][0]
    cursor.close()
    connection.close()

    uuid_1 = uuid[:8]
    uuid_2 = uuid[8:12]
    uuid_3 = uuid[12:16]
    uuid_4 = uuid[16:20]
    uuid_5 = uuid[20:]
    uuid = f"{uuid_1}-{uuid_2}-{uuid_3}-{uuid_4}-{uuid_5}"

    with open("./datas/seichi_taikai.json", mode="r", encoding="utf-8") as f:
        kikaku_data_dict = json.load(f)

    #ゴミ構造だが後でscore順にソートすることを考えるとこの方が良い
    #kikaku_data_dict = {
    #    uuid: {
    #        "user_id": user_id,
    #        "mcid": mcid,
    #        "score": 0
    #    }
    #}

    try:
        mcid = kikaku_data_dict[uuid]["mcid"]
    except KeyError:
        kikaku_data_dict[uuid] = {
            "user_id": message.author.id,
            "mcid": mcid,
            "score": 0
        }
    else:
        mcid = mcid.replace("_", "\_")
        await message.channel.send(f"{mcid}は既に参加登録されています")
        return

    kikaku_data_json = json.dumps(kikaku_data_dict, indent=4)
    with open("./datas/seichi_taikai.json", mode="w", encoding="utf-8") as f:
        f.write(kikaku_data_json)

    await message.author.add_roles(kikaku_role)
    mcid = mcid.replace("_", "\_")
    await message.channel.send(f"{mcid}の参加登録が完了しました")


async def simple_kikaku_result(client1):
    """
    企画参加者役職持ちから
    任意の人数選出するだけのシンプルな結果発表"""

    guild = client1.get_guild(585998962050203672)
    kikaku_role = guild.get_role(668021019700756490)
    try:
        tousen = random.sample(kikaku_role.members, k=5) #kは当選人数
    except ValueError:
        tousen = kikaku_role.members

    tousen_role = guild.get_role(669720120314167307)

#    description = ""
#    for mem in tousen:
#        await mem.add_roles(tousen_role)
#        description += f"{mem.mention}\n"

#    description = (
#        f"1等: {tousen[0].mention}\n"
#        f"2等: {tousen[1].mention}, {tousen[2].mention}"
#    )

    description = f"当選者: {tousen[0].mention}"
    await tousen[0].add_roles(tousen_role)

    embed = discord.Embed(title=":tada:おめでとう:tada:", description=description, color=0xffff00)
    ch = client1.get_channel(586420858512343050)
    await ch.send(content="<@&668021019700756490>", embed=embed)
    await ch.send(
        "**受け取り期日は2023/12/31までとします\n"
        "**当選者で事情により期限内に受け取れない場合は期限内に言っていただければ対応します。\n"
#        "kirisamekei都合で受け渡しができない可能性があります。その際は受け取り期限を延長/廃止します。"
        "参加賞は期限内に受け取ってください。\n参加賞受け取り希望の方でmineでの受け取りを希望する場合は"
        "s3にてmineでの受け渡しも可能とします。\n受け取り辞退をする場合<#665487669953953804>にて`/cancel`をしてください。"
    )


async def complex_kikaku_result(client1):
    """
    総額いくらを当選人数人でランダムに分配するときに使う"""

    guild = client1.get_guild(585998962050203672)
    kikaku_role = guild.get_role(668021019700756490)
    tousen_ninzuu = 10 #当選人数をここに入力
    try:
        tousen = random.sample(kikaku_role.members, k=tousen_ninzuu)
    except ValueError:
        tousen = kikaku_role.members

    tousen_role = guild.get_role(669720120314167307)

    tousen_ninzuu = len(tousen)
    if tousen_ninzuu == 0: #ほとんど想定する必要はない
        ch = client1.get_channel(586420858512343050)
        await ch.send(content="企画参加者は誰一人いませんでした・・・")
        return

    price_list = [0] #起点、触るな
    for i in range(tousen_ninzuu-1): #range内は当選人数-1 (ex: 10人が当選のとき9)
        n = random.randint(0, 2560) #randintの第2引数は総額の個数
        price_list.append(n)
    price_list.append(2560) #randintの第2引数と同じ値を入れること
    price_list.sort()

    give_list = []
    keihin_sum = 0
    description = ""
    for i in range(tousen_ninzuu):
        give = price_list[tousen_ninzuu-i] - price_list[tousen_ninzuu-1-i]
        st, ko = divmod(give, 64)
        give_list.append(f"{st}st+{ko}")
        keihin_sum += give

        tousen[i].add_roles(tousen_role)
        description += f"{tousen[i].mention}: {give_list[i]}\n" 

    embed = discord.Embed(title=":tada:おめでとう:tada:(これはデバッグです)", description=description, color=0xffff00)
    ch = client1.get_channel(586420858512343050) #企画お知らせ
    #ch = client1.get_channel(595072269483638785) #1組
    await ch.send(content="<@&668021019700756490>", embed=embed)
    await ch.send(
        "**受け取り期日は2023/10/17までとします\n"
        "**当選者で事情により期限内に受け取れない場合は期限内に言っていただければ対応します。\n"
        "受け取り辞退をする場合<#665487669953953804>にて`/cancel`をしてください。"
    )


async def seichi_taikai_result(client1):
    """
    整地大会の結果発表用
    順位報酬: 1位～3位、
    大量採掘報酬: 3104万以上、
    調整報酬: 3104の倍数に調整、
    人数報酬: 日間1000万以上が20人以上"""

    with open("./datas/seichi_taikai.json", mode="r", encoding="utf-8") as f:
        kikaku_data_dict = json.load(f)

    yesterday = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y%m%d")
    with open(f"../graph_v4/player_data_break_{yesterday}.json", mode="r", encoding="utf-8") as f:
        player_data_dict = json.load(f)

    rank = 1
    for player_data in sorted(player_data_dict.values(), key=lambda x: -x["23_58"]):
        if rank == 20:
            daily_20th_score = player_data["23_58"]
            break
        else:
            rank += 1

    if daily_20th_score >= 10000000:
        ninzuu_housyu = 16
    else:
        ninzuu_housyu = 0

    for uuid in kikaku_data_dict.keys():
        kikaku_data = kikaku_data_dict[uuid]
        try:
            kikaku_data["score"] = player_data_dict[uuid]["23_58"]
        except KeyError:
            kikaku_data["score"] = 0

    sankasya_data_dict = {}
    for uuid, value in sorted(kikaku_data_dict.items(), key=lambda x: -x[1]["score"]):
        sankasya_data_dict[uuid] = value

    rank = 0
    loop = 0
    page = math.ceil(len(sankasya_data_dict) / 10)
    for value in sankasya_data_dict.values():
        if (rank % 10) == 0:
            loop += 1
            description = ""

        user_id = value["user_id"]
        mcid = value["mcid"]
        score = value["score"]
        if rank == 0:
            jyunni_housyu = 192
        elif rank == 1:
            jyunni_housyu = 128
        elif rank == 2:
            jyunni_housyu = 64
        else:
            jyunni_housyu = 0

        if score >= 31040000:
            tairyo_saikutsu_housyu = 64
        else:
            tairyo_saikutsu_housyu = 0

        if score % 3104 == 0:
            tyousei_housyu = math.floor((score * 0.01) / 3104)
        else:
            tyousei_housyu = 0

        for i in range(16-len(mcid)):
            mcid += " "
        mcid = mcid.replace("_", "\_")

        score = "{:,}".format(score)

        description += (
            f"<@{user_id}>\n"
            f"{mcid}: {rank+1}位: {score}\n"
            f"    順位報酬　　: {int(jyunni_housyu/64)}st\n"
            f"    大量採掘報酬: {int(tairyo_saikutsu_housyu/64)}st\n"
        )
        st, ko = divmod(tyousei_housyu, 64)
        description += (
            f"    調整報酬　　: {st}st + {ko}個\n"
            f"    人数報酬　　: {ninzuu_housyu}個\n"
        )
        st, ko = divmod(jyunni_housyu+tairyo_saikutsu_housyu+tyousei_housyu+ninzuu_housyu, 64)
        description += f"    　**合計　: {st}st + {ko}個**\n"

        if not (st == 0 and ko == 0):
            guild = client1.get_guild(585998962050203672)
            tousen_role = guild.get_role(669720120314167307)
            member = guild.get_member(user_id)
            await member.add_roles(tousen_role)

        if (rank % 10) == 9:
            embed = discord.Embed(
                title=f"結果発表({loop}/{page})",
                description=description,
                color=0xffff00
            )
            notice_ch = client1.get_channel(586420858512343050) #企画についてのお知らせ(本番用)
            #notice_ch = client1.get_channel(595072269483638785) #1組
            if loop == 1:
                mention = "<@&668021019700756490>" #下にもあるよ、要修正
            else:
                mention=""
            await notice_ch.send(content=mention, embed=embed)

        rank += 1

    if len(sankasya_data_dict) % 10 != 0:
        embed = discord.Embed(
            title=f"結果発表({loop}/{page})",
            description=description,
            color=0xffff00
        )
        notice_ch = client1.get_channel(586420858512343050) #企画についてのお知らせ(本番用)
        #notice_ch = client1.get_channel(595072269483638785) #1組
        if loop == 1:
            mention = "<@&668021019700756490>" #上にもあるよ、要修正
        else:
            mention=""
        await notice_ch.send(content=mention, embed=embed)


async def tanzaku(message, command):
    negai = command.replace("tanzaku ", "")
    bg_color = random.randint(0x000000, 0xffffff)
    letter_color = 0xffffff - bg_color
    image = Image.new("RGB", (130, 500), bg_color)
    moji = ImageDraw.Draw(image)
    font = ImageFont.truetype(r"./UDDigiKyokashoN-R.ttc", size=50)
    negai = list(negai)
    i = 0
    for x in range(2):
        for y in range(10):
            try:
                moji.text((80-x*50, y*50), text=negai[i], font=font, fill=letter_color)
            except IndexError:
                break
            i += 1
    username = list(message.author.display_name)
    font = ImageFont.truetype(r"./UDDigiKyokashoN-R.ttc", size=30)
    for y in range(10):
        try:
            moji.text((0, 100+y*30), text=username[y], font=font, fill=letter_color)
        except IndexError:
            break
    bg = Image.open("./pictures/banboo.png")
    x = random.randint(0, 650)
    y = random.randint(0, 280)
    bg.paste(image, (x, y))
    bg.save("tanzaku.png")
    await message.channel.send(file=discord.File("tanzaku.png"))