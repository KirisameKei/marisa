import datetime
import json
import math
import os
import random
import re

import discord
import requests
import simplejson

async def total_break(message, command):
    uuid_mcid = await check_mcid_format(message, command)

    if uuid_mcid is None:
        return

    uuid = uuid_mcid[0]
    mcid = uuid_mcid[1]

    with open("./datas/player_data.json", mode="r", encoding="utf-8") as f:
        player_data_dict = json.load(f)

    try:
        total_break_score = player_data_dict[uuid]["total_break"]
    except KeyError:
        mcid = mcid.replace("_", "\_")
        await message.channel.send(f"{mcid}は整地鯖にいません")
        return

    rank_list = []
    for uuid_value in sorted(player_data_dict.items(), key=lambda x: -x[1]["total_break"]):
        rank_list.append(uuid_value[0])
        if uuid_value[0] == uuid:
            break

    rank = len(rank_list)
    mc_avatar_url = f"https://minotar.net/armor/body/{mcid}/130.png"

    #────────────ここからコピペ禁止────────────
    if total_break_score < 15:
        level = 1
    elif total_break_score < 49:
        level = 2
    elif total_break_score < 106:
        level = 3
    elif total_break_score < 198:
        level = 4
    elif total_break_score < 333:
        level = 5
    elif total_break_score < 705:
        level = 6
    elif total_break_score < 1265:
        level = 7
    elif total_break_score < 2105:
        level = 8
    elif total_break_score < 9557:#2105～9556までがこのelfi文内に入る
        level = 9
        n = 2015
        while True:
            n += 1242
            if total_break_score < n:
                break
            else:
                level += 1
    elif total_break_score < 11047:
        level = 15
    elif total_break_score < 12835:
        level = 16
    elif total_break_score < 14980:
        level = 17
    elif total_break_score < 17554:
        level = 18
    elif total_break_score < 20642:
        level = 19
    elif total_break_score < 24347:
        level = 20
    elif total_break_score < 28793:
        level = 21
    elif total_break_score < 34128:
        level = 22
    elif total_break_score < 40530:
        level = 23
    elif total_break_score < 48212:
        level = 24
    elif total_break_score < 57430:
        level = 25
    elif total_break_score < 68491:
        level = 26
    elif total_break_score < 81764:
        level = 27
    elif total_break_score < 97691:
        level = 28
    elif total_break_score < 212363:
        level = 29
        n = 97691
        while True:
            n += 19112
            if total_break_score < n:
                break
            else:
                level += 1
    elif total_break_score < 235297:
        level = 35
    elif total_break_score < 262817:
        level = 36
    elif total_break_score < 295891:
        level = 37
    elif total_break_score < 335469:
        level = 38
    elif total_break_score < 383022:
        level = 39
    elif total_break_score < 434379:
        level = 40
    elif total_break_score < 489844:
        level = 41
    elif total_break_score < 549746:
        level = 42
    elif total_break_score < 614440:
        level = 43
    elif total_break_score < 684309:
        level = 44
    elif total_break_score < 759767:
        level = 45
    elif total_break_score < 841261:
        level = 46
    elif total_break_score < 929274:
        level = 47
    elif total_break_score < 1024328:
        level = 48
    elif total_break_score < 1126986:
        level = 49
    elif total_break_score < 1250000:
        level = 50
    elif total_break_score < 2375000:
        level = 51
        n = 1250000
        while True:
            n += 125000
            if total_break_score < n:
                break
            else:
                level += 1
    elif total_break_score < 4125000:
        level = 60
        n = 2375000
        while True:
            n += 175000
            if total_break_score < n:
                break
            else:
                level += 1
    elif total_break_score < 6325000:
        level = 70
        n = 4215000
        while True:
            n += 220000
            if total_break_score < n:
                break
            else:
                level += 1
    elif total_break_score < 9215000:
        level = 80
        n = 6325000
        while True:
            n += 280000
            if total_break_score < n:
                break
            else:
                level += 1
    elif total_break_score < 13165000:
        level = 90
        n = 9215000
        while True:
            n += 360000
            if total_break_score < n:
                break
            else:
                level += 1
    elif total_break_score < 13615000:
        level = 100
    elif total_break_score < 17665000:
        #コピペ検出用文字列、けい制作
        level = 101
        n = 13615000
        while True:
            n += 450000
            if total_break_score < n:
                break
            else:
                level += 1
    elif total_break_score < 22565000:
        level = 110
        n = 17665000
        while True:
            n += 490000
            if total_break_score < n:
                break
            else:
                level += 1
    elif total_break_score < 27965000:
        level = 120
        n = 22565000
        while True:
            n += 540000
            if total_break_score < n:
                break
            else:
                level += 1
    elif total_break_score < 33865000:
        level = 130
        n = 27965000
        while True:
            n += 590000
            if total_break_score <n:
                break
            else:
                level += 1
    elif total_break_score < 40465000:
        level = 140
        n = 33865000
        while True:
            n += 660000
            if total_break_score < n:
                break
            else:
                level += 1
    elif total_break_score < 47865000:
        level = 150
        n = 40465000
        while True:
            n += 740000
            if total_break_score < n:
                break
            else:
                level += 1
    elif total_break_score < 56065000:
        level = 160
        n = 47865000
        while True:
            n += 820000
            if total_break_score < n:
                break
            else:
                level += 1
    elif total_break_score < 65265000:
        level = 170
        n = 56065000
        while True:
            n += 920000
            if total_break_score < n:
                break
            else:
                level += 1
    elif total_break_score < 75265000:
        level = 180
        n = 65265000
        while True:
            n += 1000000
            if total_break_score < n:
                break
            else:
                level += 1
    elif total_break_score < 85615000:
        level = 190
        n = 75265000
        while True:
            n += 1150000
            if total_break_score < n:
                break
            else:
                level += 1
    elif total_break_score < 87115000:
        level = 199
    else:
        level = 200
        star_level, amari = divmod(total_break_score, 87115000)
        persentage = round(amari * 100 / 87115000, 2)
        star_level_str = f"{star_level}、{persentage}%"
    #────────────ここまでコピペ禁止────────────

    total_break_score = "{:,}".format(total_break_score)
    mcid = mcid.replace("_", "\_")
    try:
        embed = discord.Embed(title=f"{mcid}",description=f"整地量：{total_break_score}\n順位：{rank}\nレベル：{level}☆{star_level_str}", color=0x7f7f7f)
    except UnboundLocalError:
        embed = discord.Embed(title=f"{mcid}",description=f"整地量：{total_break_score}\n順位：{rank}\nレベル：{level}", color=0x7f7f7f)

    embed.set_thumbnail(url=mc_avatar_url)
    await message.channel.send(embed=embed)


async def total_build(message, command):
    uuid_mcid = await check_mcid_format(message, command)

    if uuid_mcid is None:
        return

    uuid = uuid_mcid[0]
    mcid = uuid_mcid[1]

    with open("./datas/player_data.json", mode="r", encoding="utf-8") as f:
        player_data_dict = json.load(f)

    try:
        total_build_score = player_data_dict[uuid]["total_build"]
    except KeyError:
        mcid = mcid.replace("_", "\_")
        await message.channel.send(f"{mcid}は整地鯖にいません")
        return

    rank_list = []
    for uuid_value in sorted(player_data_dict.items(), key=lambda x: -x[1]["total_build"]):
        rank_list.append(uuid_value[0])
        if uuid_value[0] == uuid:
            break

    rank = len(rank_list)
    mc_avatar_url = f"https://minotar.net/armor/body/{mcid}/130.png"

    #────────────ここからコピペ禁止────────────
    if total_build_score < 50:
        level = 1
    elif total_build_score < 100:
        level = 2
    elif total_build_score < 200:
        level = 3
    elif total_build_score < 300:
        level = 4
    elif total_build_score < 450:
        level = 5
    elif total_build_score < 600:
        level = 6
    elif total_build_score < 900:
        level = 7
    elif total_build_score < 1200:
        level = 8
    elif total_build_score < 1600:
        level = 9
    elif total_build_score < 2000:
        level = 10
    elif total_build_score < 2500:
        level = 11
    elif total_build_score < 3000:
        level = 12
    elif total_build_score < 3600:
        level = 13
    elif total_build_score < 4300:
        level = 14
    elif total_build_score < 5100:
        level = 15
    elif total_build_score < 6000:
        level = 16
    elif total_build_score < 7000:
        level = 17
    elif total_build_score < 8200:
        level = 18
    elif total_build_score < 9400:
        level = 19
    elif total_build_score < 10800:
        level = 20
    elif total_build_score < 12200:
        level = 21
    elif total_build_score < 12800:
        level = 22
    elif total_build_score < 15400:
        level = 23
    elif total_build_score < 17200:
        level = 24
    elif total_build_score < 19000:
        level = 25
    elif total_build_score < 21000:
        level = 26
    elif total_build_score < 23000:
        level = 27
    elif total_build_score < 25250:
        level = 28
    elif total_build_score < 27500:
        level = 29
    elif total_build_score < 30000:
        level = 30
    elif total_build_score < 32500:
        level = 31
    elif total_build_score < 35500:
        level = 32
    elif total_build_score < 38500:
        level = 33
    elif total_build_score < 42000:
        level = 34
    elif total_build_score < 45500:
        level = 35
    elif total_build_score < 49500:
        level = 36
    elif total_build_score < 54000:
        level = 37
    elif total_build_score < 59000:
        level = 38
    elif total_build_score < 64000:
        level = 39
    elif total_build_score < 70000:
        level = 40
    elif total_build_score < 76000:
        level = 41
    elif total_build_score < 83000:
        level = 42
    elif total_build_score < 90000:
        level = 43
    elif total_build_score < 98000:
        level = 44
    elif total_build_score < 106000:
        level = 45
    elif total_build_score < 115000:
        level = 46
    elif total_build_score < 124000:
        level = 47
    elif total_build_score < 133000:
        level = 48
    elif total_build_score < 143000:
        level = 49
    elif total_build_score < 153000:
        level = 50
    elif total_build_score < 163000:
        level = 51
    elif total_build_score < 174000:
        level = 52
    elif total_build_score < 185000:
        level = 53
    elif total_build_score < 196000:
        level = 54
    elif total_build_score < 208000:
        level = 55
    elif total_build_score < 220000:
        level = 56
    elif total_build_score < 232000:
        level = 57
    elif total_build_score < 245000:
        level = 58
    elif total_build_score < 258000:
        level = 59
    elif total_build_score < 271000:
        level = 60
    elif total_build_score < 285000:
        level = 61
    elif total_build_score < 299000:
        level = 62
    elif total_build_score < 313000:
        level = 63
    elif total_build_score < 328000:
        level = 64
    elif total_build_score < 343000:
        level = 65
    elif total_build_score < 358000:
        level = 66
    elif total_build_score < 374000:
        level = 67
    elif total_build_score < 390000:
        level = 68
    elif total_build_score < 406000:
        level = 69
    elif total_build_score < 432000:
        level = 70
    elif total_build_score < 440000:
        level = 71
    elif total_build_score < 457000:
        level = 72
    elif total_build_score < 475000:
        level = 73
    elif total_build_score < 493000:
        level = 74
    elif total_build_score < 511000:
        level = 75
    elif total_build_score < 530000:
        level = 76
    elif total_build_score < 549000:
        level = 77
    elif total_build_score < 568000:
        level = 78
    elif total_build_score < 588000:
        level = 79
    elif total_build_score < 608000:
        level = 80
    elif total_build_score < 628000:
        level = 81
    elif total_build_score < 648000:
        level = 82
    elif total_build_score < 668000:
        level = 83
    elif total_build_score < 688000:
        level = 84
    elif total_build_score < 708000:
        level = 85
    elif total_build_score < 728000:
        level = 86
    elif total_build_score < 748000:
        level = 87
    elif total_build_score < 768000:
        level = 88
    elif total_build_score < 788000:
        level = 89
    elif total_build_score < 808000:
        level = 90
    elif total_build_score < 828000:
        level = 91
    elif total_build_score < 848000:
        level = 92
    elif total_build_score < 868000:
        level = 93
    elif total_build_score < 888000:
        level = 94
    elif total_build_score < 908000:
        level = 95
    elif total_build_score < 928000:
        level = 96
    elif total_build_score < 948000:
        level = 97
    elif total_build_score < 968000:
        level = 98
    elif total_build_score < 1000000:
        level = 99
    else:
        level = 100
    #────────────ここまでコピペ禁止────────────

    total_build_score = "{:,}".format(total_build_score)
    mcid = mcid.replace("_", "\_")
    embed = discord.Embed(title=f"{mcid}",description=f"建築量：{total_build_score}\n順位：{rank}\nレベル：{level}", color=0xb4905a)

    embed.set_thumbnail(url=mc_avatar_url)
    await message.channel.send(embed=embed)


async def daily_score(message, command):
    uuid_mcid = await check_mcid_format(message, command)

    if uuid_mcid is None:
        return

    uuid = uuid_mcid[0]

    with open("./datas/daily_player_data.json", mode="r", encoding="utf-8") as f:
        daily_score_dict = json.load(f)

    try:
        mcid = daily_score_dict[uuid]["mcid"]
    except KeyError:
        mcid = uuid_mcid[1]
        break_score = 0
        build_score = 0
        break_rank = "-"
        build_rank = "-"
    else:
        break_score = daily_score_dict[uuid]["break"]
        build_score = daily_score_dict[uuid]["build"]
        if break_score == 0:
            break_rank = "-"
        else:
            rank_list = []
            for logged_uuid in daily_score_dict.keys():
                rank_list.append(logged_uuid)
                if logged_uuid == uuid:
                    break
            break_rank = len(rank_list)
        if build_score == 0:
            build_rank = "-"
        else:
            rank_list = []
            for uuid_value in sorted(daily_score_dict.items(), key=lambda x: -x[1]["build"]):
                rank_list.append(uuid_value[0])
                if uuid_value[0] == uuid:
                    break
            build_rank = len(rank_list)

    mc_avatar_url = f"https://minotar.net/armor/body/{mcid}/130.png"
    embed = discord.Embed(title=f"{mcid}", color=random.randint(0x000000, 0xffffff))
    embed.set_thumbnail(url=mc_avatar_url)
    break_score = "{:,}".format(break_score)
    build_score = "{:,}".format(build_score)
    embed.add_field(name="整地量", value=f"{break_score}\n{break_rank}位", inline=True)
    embed.add_field(name="建築量", value=f"{build_score}\n{build_rank}位", inline=True)
    await message.channel.send(embed=embed)


async def last_login(message, command):
    mcid = command.split()[1].replace("\\", "")
    p = re.compile(r"^[a-zA-Z0-9_]+$")
    if not p.fullmatch(mcid):
        await message.channel.send("MCIDに使用できない文字が含まれています")
        return

    if not (len(mcid) >= 3 and len(mcid) <= 16):
        await message.channel.send("MCIDの文字数として不適です")
        return

    url = f"https://ranking-gigantic.seichi.click/player/{mcid.lower()}"
    await message.channel.send(f"現在この機能はご利用いただけません。お手数ですがこちらのリンクでご確認ください\n{url}")


async def mcavatar(message, command):
    """
    第一引数のMCIDのマイクラスキンを取得"""

    mcid = command.split()[1]
    mcid = mcid.replace("\\", "")
    url = f"https://api.mojang.com/users/profiles/minecraft/{mcid}"
    try:
        res = requests.get(url)
        res.raise_for_status()
        try:
            res.json()
        except json.decoder.JSONDecodeError:
            await message.channel.send("そのMCIDは存在しません")
            return
    except requests.exceptions.HTTPError:
        await message.channel.send("現在データ参照元が使用できない状態です。しばらく待ってからもう一度お試しください。")
        return

    url = f"https://minotar.net/armor/body/{mcid}/130.png"
    avatar_pic_embed = discord.Embed()
    avatar_pic_embed.set_image(url=url)
    await message.channel.send(embed=avatar_pic_embed)


async def stack_eval64(message, command):
    """
    スタック数の計算をする"""

    msg = command.replace("/stack_eval64 ", "").replace("/stack_eval ", "")
    msg = msg.lower()
    msg = msg.replace("lc", "*3456").replace("sb", "*1728").replace("c", "*1728").replace("st", "*64").replace("個", "")
    p = re.compile(r"^[0-9 +\-*/%().]+$")
    if not p.fullmatch(msg):
        await message.channel.send("不正な入力です")
        return
    try:
        result = eval(msg)
    except (SyntaxError, NameError, OverflowError, TypeError):
        await message.channel.send("不正な入力です")
    except ZeroDivisionError:
        await message.channel.send("変な入力するんじゃねぇ！")
    else:
        try:
            LC, st = divmod(result, 3456)
            st, ko = divmod(st, 64)
        except (TypeError):
            await message.channel.send("変な入力するんじゃねぇ！")
            return
        result_list = []
        if LC != 0:
            result_list.append(f"{LC}LC")
        if st != 0:
            result_list.append(f"{st}st")
        if ko != 0:
            result_list.append(f"{ko}個")
        result_str = " + ".join(result_list)
        if result_str == "":
            result_str = "0"
        await message.channel.send(f"{result_str}\n{result}")


async def stack_eval16(message, command):
    """
    スタック数の計算をする"""

    msg = command.replace("/stack_eval16 ", "")
    msg = msg.lower()
    msg = msg.replace("lc", "*864").replace("sb", "*432").replace("c", "*432").replace("st", "*16").replace("個", "")
    p = re.compile(r"^[0-9 +\-*/%().]+$")
    if not p.fullmatch(msg):
        await message.channel.send("不正な入力です")
        return
    try:
        result = eval(msg)
    except (SyntaxError, NameError, OverflowError, TypeError):
        await message.channel.send("不正な入力です")
    except ZeroDivisionError:
        await message.channel.send("変な入力するんじゃねぇ！")
    else:
        try:
            LC, st = divmod(result, 864)
            st, ko = divmod(st, 432)
        except (TypeError):
            await message.channel.send("変な入力するんじゃねぇ！")
            return
        result_list = []
        if LC != 0:
            result_list.append(f"{LC}LC")
        if st != 0:
            result_list.append(f"{st}st")
        if ko != 0:
            result_list.append(f"{ko}個")
        result_str = " + ".join(result_list)
        if result_str == "":
            result_str = "0"
        await message.channel.send(f"{result_str}\n{result}")


async def stack_eval1(message, command):
    """
    スタック数の計算をする"""

    msg = command.replace("/stack_eval1 ", "")
    msg = msg.lower()
    msg = msg.replace("lc", "*54").replace("sb", "*27").replace("c", "*27").replace("st", "*1").replace("個", "")
    p = re.compile(r"^[0-9 +\-*/%().]+$")
    if not p.fullmatch(msg):
        await message.channel.send("不正な入力です")
        return
    try:
        result = eval(msg)
    except (SyntaxError, NameError, OverflowError, TypeError):
        await message.channel.send("不正な入力です")
    except ZeroDivisionError:
        await message.channel.send("変な入力するんじゃねぇ！")
    else:
        try:
            LC, ko = divmod(result, 54)
        except (TypeError):
            await message.channel.send("変な入力するんじゃねぇ！")
            return
        result_list = []
        if LC != 0:
            result_list.append(f"{LC}LC")
        if ko != 0:
            result_list.append(f"{ko}個")
        result_str = " + ".join(result_list)
        if result_str == "":
            result_str = "0"
        await message.channel.send(f"{result_str}\n{result}")


async def info(client1, message, command):
    """
    role, guild, user, ch, emojiの情報を表示する関数"""

    check_list = command.split()
    if not len(check_list) == 3:
        await message.channel.send("引数の数が正しくありません\nヒント: `/info␣[role, guild, user, ch, emoji]␣ID`")
        return

    check_element = check_list[1]
    check_id = check_list[2]

    try:
        check_id = int(check_id)
    except ValueError:
        await message.channel.send("IDとして成り立ちません\nヒント: `/info␣[role, guild, user, ch, emoji]␣ID`")
        return

    if check_element == "role":
        info_embed = role_info(message, check_id)
    elif check_element == "guild":
        info_embed = guild_info(client1, check_id)
    elif check_element == "user":
        info_embed = await user_info(client1, check_id)
    elif check_element in ("ch", "channel"):
        info_embed = await ch_info(client1, check_id)
    elif check_element == "emoji":
        info_embed = await emoji_info(client1, check_id)
    else:
        await message.channel.send("第二引数の指定が正しくありません\nヒント: `/info␣[role, guild, user, ch, emoji]␣ID`")
        return

    await message.channel.send(embed=info_embed)


async def random_command(message, command):
    """
    pythonのランダムをdis上で再現する"""

    arg = command.split()[1]

    if arg == "choice":
        try:
            args = command.split()[2:]
        except IndexError:
            await message.channel.send("候補がありません")
            return
        if args == []:
            await message.channel.send("候補がありません")
            return
        await message.channel.send(random.choice(args))

    elif arg == "sample":
        try:
            sample = int(command.split()[2])
        except IndexError:
            await message.channel.send("引数が足りません。ヒント:/random␣sample␣n(n≧1)␣候補")
            return
        except ValueError:
            await message.channel.send("数の指定は正の整数です")
            return
        if sample <= 0:
            await message.channel.send("数の指定は正の整数です")
        try:
            args = command.split()[3:]
        except IndexError:
            await message.channel.send("候補がありません")
            return
        if len(args) < sample:
            await message.channel.send("候補数よりサンプル数のほうが多いです")
            return
        await message.channel.send(random.sample(args, sample))

    elif arg == "choices":
        try:
            sample = int(command.split()[2])
        except IndexError:
            await message.channel.send("引数が足りません。ヒント:/random␣choices␣n(n≧1)␣候補")
            return
        except ValueError:
            await message.channel.send("数の指定は正の整数です")
            return
        try:
            args = command.split()[3:]
        except IndexError:
            await message.channel.send("候補がありません")
            return
        if args == []:
            await message.channel.send("候補がありません")
            return
        if sample <= 0:
            await message.channel.send("サンプル数は正の整数です")
            return
        await message.channel.send(random.choices(args, k=sample))

    elif arg == "randint":
        try:
            start = int(command.split()[2])
            end = int(command.split()[3])
        except IndexError:
            await message.channel.send("引数が足りません。ヒント:/random␣randint␣min␣max")
            return
        except ValueError:
            await message.channel.send("max, minは整数です")
            return
        if start >= end:
            await message.channel.send("minがmaxと同じか大きいです")
            return
        await message.channel.send(f"{random.randint(start, end)}")

    else:
        await message.channel.send("不正な引数です。ヒント:/random␣[choice, sample, choices, randint]")


async def weather(message, command):
    """
    weatherコマンド対応用関数"""

    if command.split()[1] == "map":

        now = datetime.datetime.now()
        y_m_d = datetime.datetime.strftime(now, r"%Y/%m/%d") #本日の日付をyyyy/mm/ddにする
        if now.hour >= 0 and now.hour < 6: #前日21時
            y_m_d = datetime.datetime.strftime(now - datetime.timedelta(days=1), r"%Y/%m/%d") #前日の日付をyyyy/mm/ddにする
            hour = "21"
        elif now.hour >= 6 and now.hour < 9:
            hour = "03"
        elif now.hour >= 9 and now.hour < 12:
            hour = "06"
        elif now.hour >= 12 and now.hour < 15 :
            hour = "09"
        elif now.hour >= 15 and now.hour < 18:
            hour = "12"
        elif now.hour >= 18 and now.hour < 21:
            hour = "15"
        elif now.hour >= 21 and now.hour < 24:
            hour = "18"

        url = f"https://imageflux.tenki.jp/large/static-images/chart/{y_m_d}/{hour}/00/00/large.jpg"
        weather_embed = discord.Embed()
        weather_embed.set_image(url=url)
        await message.channel.send(embed=weather_embed)

    else:
        with open("./datas/citycodes.json", mode="r", encoding="utf-8") as f:
            citycode = json.load(f)

        try:
            lon_lat_list = citycode[command.split()[1]]
        except KeyError:
            cities = ""
            for city in citycode.keys():
                cities += f"{city}、"
            await message.channel.send(f"その地点は登録されていません\n現在登録されている地点:```\n{cities}```")
            return
        key = os.getenv("weather_API_key")

        lon = lon_lat_list[0]
        lat = lon_lat_list[1]

        api = f"http://api.openweathermap.org/data/2.5/onecall?units=metric&lat={lat}&lon={lon}&exclude=minutely,hourly&lang=ja&units=metric&APPID={key}"

        try:
            res = requests.get(api)
            res.raise_for_status()
            weather_data_dict = res.json()
        except requests.exceptions.HTTPError:
            await message.channel.send("現在データ参照元が使用できない状態です。しばらく待ってからもう一度お試しください。")
            return
        else:
            now = (datetime.datetime.fromtimestamp(weather_data_dict["current"]["dt"])).strftime(r"%Y/%m/%d-%H:%M")
            #────現在の天気によってembedの色を決める────
            if weather_data_dict["current"]["weather"][0]["main"] == "Thunderstorm":
                color = 0xffff00
            elif weather_data_dict["current"]["weather"][0]["main"] == "Drizzle" or weather_data_dict["current"]["weather"][0]["main"] == "Rain":
                color = 0x0000ff
            elif weather_data_dict["current"]["weather"][0]["main"] == "Snow":
                color = 0xfffffe
            elif weather_data_dict["current"]["weather"][0]["main"] == "Clear":
                color = 0xff7700
            elif weather_data_dict["current"]["weather"][0]["main"] == "Atmosphere" or weather_data_dict["current"]["weather"][0]["main"] == "Clouds":
                color = 0x888888
            else:
                color = 0x000000
            #────ここまで色決め────
            weather_embed = discord.Embed(title=f"{command.split()[1]}の天気概況&予報", description=f"{now}発表", color=color)
            icon = weather_data_dict["current"]["weather"][0]["icon"]
            weather_embed.set_thumbnail(url=f"http://openweathermap.org/img/wn/{icon}@2x.png")
            weather = weather_data_dict["current"]["weather"][0]["description"]
            temp = weather_data_dict["current"]["temp"]
            pressure = weather_data_dict["current"]["pressure"]
            wind_speed = weather_data_dict["current"]["wind_speed"]
            humidity = weather_data_dict["current"]["humidity"]
            text = f"現在の{command.split()[1]}の天気は{weather}。\n気温は{temp}℃で気圧は{pressure}hPa、風速は{wind_speed}m/sで湿度は{humidity}%です。"
            try:
                rain = weather_data_dict["current"]["rain"]["1h"]
            except KeyError:
                pass
            else:
                if rain >= 80:
                    strong = "猛烈な"
                elif rain >= 50:
                    strong = "非常に激しい"
                elif rain >= 30:
                    strong = "激しい"
                elif rain >= 20:
                    strong = "強い"
                elif rain >= 10:
                    strong = "やや強い"
                else:
                    strong = ""
                text += f"\n1時間に振った雨の量は{rain}mmで{strong}雨になっています。"
            try:
                snow = weather_data_dict["current"]["snow"]["1h"]
            except KeyError:
                pass
            else:
                text += f"\n積雪量は{snow*10}cmです。"

            sunrise = (datetime.datetime.fromtimestamp(weather_data_dict["current"]["sunrise"])).strftime(r"%H:%M")
            sunset = (datetime.datetime.fromtimestamp(weather_data_dict["current"]["sunset"])).strftime(r"%H:%M")
            text += f"\n\n本日の日の出時刻は{sunrise}、日の入り時刻は{sunset}となっています。"
            weather_embed.add_field(name="現在の天気概況", value=text, inline=False)

            when_list = ["明日", "明後日", "明々後日"]
            for i in range(4):
                if i == 0:
                    pass
                else:
                    weather = ""
                    for wt in weather_data_dict["daily"][i]["weather"]:
                        weather += wt["description"] + ", "
                    max_temp = weather_data_dict["daily"][i]["temp"]["max"]
                    min_temp = weather_data_dict["daily"][i]["temp"]["min"]
                    pressure = weather_data_dict["daily"][i]["pressure"]
                    wind_speed = weather_data_dict["daily"][i]["wind_speed"]
                    humidity = weather_data_dict["daily"][i]["humidity"]
                    pop = math.floor(weather_data_dict["daily"][i]["pop"] * 100)

                    date = (datetime.datetime.fromtimestamp(weather_data_dict["daily"][i]["dt"])).strftime(r"%Y/%m/%d-%H:%M")
                    text = (
                        f"{date}\n"
                        f"天気　　　　: {weather}\n予想最高気温: {max_temp}℃\n予想最低気温: {min_temp}℃\n"
                        f"予想気圧　　: {pressure}hPa\n予想風速　　: {wind_speed}m/s\n予想湿度　　: {humidity}%\n降水確率　　: {pop}%"
                    )
                    try:
                        rain = weather_data_dict["daily"][i]["rain"]
                    except KeyError:
                        pass
                    else:
                        text += f"\n予想降雨量　: {rain}mm"

                    try:
                        snow = weather_data_dict["daily"][i]["snow"]
                    except KeyError:
                        pass
                    else:
                        text += f"\n予想降雪量　: {snow*10}cm"

                    sunrise = (datetime.datetime.fromtimestamp(weather_data_dict["daily"][i]["sunrise"])).strftime(r"%d日%H:%M")
                    sunset = (datetime.datetime.fromtimestamp(weather_data_dict["daily"][i]["sunset"])).strftime(r"%d日%H:%M")
                    text += f"\n\n{when_list[i-1]}の日の出時刻は{sunrise}、日の入り時刻は{sunset}です"

                    weather_embed.add_field(name=f"{when_list[i-1]}の天気予報", value=text, inline=False)
            await message.channel.send(embed=weather_embed)


async def vote(message, command):
    """
    投票機能"""

    if message.author.bot:
        return

    vote_list = command.split()
    if len(vote_list) == 1:
        await message.channel.send("/vote␣投票の題名\nor\n/vote␣投票の題名␣候補1␣候補2␣・・・␣候補n(n≦20)")
        return

    if len(vote_list) > 22:
        await message.channel.send("候補が多すぎます。20個以下にしてください。")
        return

    if len(vote_list) == 2:
        vote_embed = discord.Embed(title=vote_list[1], color=0xfffffe)
        vote_msg = await message.channel.send(embed=vote_embed)
        await vote_msg.add_reaction("⭕")
        await vote_msg.add_reaction("❌")

    else:
        reaction_list = [
            "🇦", "🇧", "🇨", "🇩", "🇪",
            "🇫", "🇬", "🇭", "🇮", "🇯",
            "🇰", "🇱", "🇲", "🇳", "🇴",
            "🇵", "🇶", "🇷", "🇸", "🇹"
        ]

        vote_content = ""

        counter = 0
        for msg in vote_list[2:]:
            vote_content += f"{reaction_list[counter]}:{msg}\n"
            counter += 1

        vote_embed = discord.Embed(title=vote_list[1], description=vote_content, color=0xfffffe)
        vote_msg = await message.channel.send(embed=vote_embed)

        for i in range(len(vote_list[2:])):
            await vote_msg.add_reaction(reaction_list[i])


async def name(message, command):
    """
    nameコマンド対応用関数"""

    try:
        name_length = int(command.split()[1])
    except ValueError:
        await message.channel.send("不正な引数です")
        return

    if not (name_length >= 1 and name_length <= 10):
        await message.channel.send("引数の値は1～10の範囲にしてください")
        return

    name_kouho = [
        "あ", "い", "う", "え", "お", "か", "き", "く", "け", "こ", "さ", "し", "す", "せ", "そ",
        "た", "ち", "つ", "て", "と", "な", "に", "ぬ", "ね", "の", "は", "ひ", "ふ", "へ", "ほ",
        "ま", "み", "む", "め", "も", "や", "ゆ", "よ", "ら", "り", "る", "れ", "ろ", "わ", "ゐ", "ゑ", "を", "ん",
        "が", "ぎ", "ぐ", "げ", "ご", "ざ", "じ", "ず", "ぜ", "ぞ", "だ", "ぢ", "づ", "で", "ど",
        "ば", "び", "ぶ", "べ", "ぼ", "ぱ", "ぴ", "ぷ", "ぺ", "ぽ", "ぱ", "ぴ", "ぷ", "ぺ", "ぽ"
    ]

    name_letter_list = random.choices(name_kouho, k=name_length)
    name = "".join(name_letter_list)
    await message.channel.send(name)

#ーーーーここまでコマンド、以下コマンド補助ーーーー

async def check_mcid_format(message, command):
    """
    正しいMCIDのフォーマットかを確かめる"""

    mcid = command.split()[1].replace("\\", "")

    p = re.compile(r"^[a-zA-Z0-9_]+$")
    if not p.fullmatch(mcid):
        await message.channel.send("MCIDに使用できない文字が含まれています")
        return None

    if not (len(mcid) >= 3 and len(mcid) <= 16):
        await message.channel.send("MCIDの文字数として不適です")
        return None

    with open("./datas/mcid_uuid_cache.json", mode="r", encoding="utf-8") as f:
        mcid_uuid_dict = json.load(f)

    mcid = mcid.lower() #keyにするために小文字化する

    try:
        uuid = mcid_uuid_dict[mcid]
    except KeyError:
        url = f"https://api.mojang.com/users/profiles/minecraft/{mcid}"
        try:
            res = requests.get(url)
            res.raise_for_status()

        except requests.exceptions.HTTPError:
            await message.channel.send("現在mojangAPIが落ちています、こりゃダメだぁ・・・")
            return None

        try:
            mcid_uuid = res.json()
        except json.decoder.JSONDecodeError:
            mcid = mcid.replace("_", "\_")
            await message.channel.send(f"{mcid}は存在しません1←この数字は仕様です")
            return None

        except simplejson.errors.JSONDecodeError:
            mcid = mcid.replace("_", "\_")
            await message.channel.send(f"{mcid}は存在しません2←この数字は仕様です")
            return None

        uuid = mcid_uuid["id"]
        uuid_1 = uuid[:8]
        uuid_2 = uuid[8:12]
        uuid_3 = uuid[12:16]
        uuid_4 = uuid[16:20]
        uuid_5 = uuid[20:]
        uuid = f"{uuid_1}-{uuid_2}-{uuid_3}-{uuid_4}-{uuid_5}"

        mcid_uuid_dict[mcid] = uuid
        mcid_uuid_json = json.dumps(mcid_uuid_dict, indent=4)
        with open("./datas/mcid_uuid_cache.json", mode="w", encoding="utf-8") as f:
            f.write(mcid_uuid_json)

    return uuid, mcid


def role_info(message, role_id):
    """
    実行サーバの役職の情報を取得する関数
    discord.Embedを返す"""

    role = message.guild.get_role(role_id)
    try:
        role_info_embed = discord.Embed(title=role.name, color=role.color)
        if len(role.members) <= 10:
            member = ""
            for mem in role.members:
                member += f"{mem.mention}\n"
            role_info_embed = discord.Embed(title=role.name, description=member, color=role.color)
        else:
            role_info_embed = discord.Embed(title=role.name, description="11人以上いるため省略", color=role.color)
        role_info_embed.add_field(name="人数", value=f"{len(role.members)}", inline=False)
        role_info_embed.add_field(name="色", value=f"{role.color}", inline=False)
        role_made_time = (role.created_at + datetime.timedelta(hours=9)).strftime(r"%Y/%m/%d %H:%M")
        role_info_embed.add_field(name="作成日時", value=f"{role_made_time}　(JST)", inline=False)
        if role.mentionable:
            mention_able = "可"
        else:
            mention_able = "否"
        role_info_embed.add_field(name="メンションの可否", value=mention_able, inline=False)
        role_info_embed.set_footer(text=message.guild.name, icon_url=message.guild.icon_url_as(format="png"))
        return role_info_embed

    except AttributeError:
        error_embed = discord.Embed(title="ERROR", description="ID指定が間違っているかこのサーバにない役職です", color=0xff0000)
        return error_embed


def guild_info(client1, guild_id):
    """
    サーバの情報を取得する関数
    discord.Embedを返す"""
    
    guild = client1.get_guild(guild_id)
    try:
        guild_info_embed = discord.Embed(title=guild.name, color=0xffffff)
        guild_info_embed.set_thumbnail(url=guild.icon_url_as(format="png"))
        guild_info_embed.add_field(name="参加人数", value=f"{len(guild.members)}", inline=True)
        guild_made_time = (guild.created_at + datetime.timedelta(hours=9)).strftime(r"%Y/%m/%d %H:%M")
        guild_info_embed.add_field(name="作成日時", value=f"{guild_made_time}　(JST)", inline=True)
        with open("./datas/custom_prefix.json", mode="r", encoding="utf-8") as f:
            custom_prefix_dict = json.load(f)
        try:
            custom_prefix = custom_prefix_dict[f"{guild_id}"]
        except KeyError:
            custom_prefix = "/"
        guild_info_embed.add_field(name="魔理沙botのプレフィックス", value=custom_prefix, inline=False)
        return guild_info_embed

    except AttributeError:
        error_embed = discord.Embed(title="ERROR", description="ID指定が間違っているか本botの監視下にないサーバです", color=0xff0000)
        return error_embed


async def user_info(client1, user_id):
    """
    ユーザー情報を取得する関数
    discord.Embedを返す"""

    user = client1.get_user(user_id)
    if user is None:
        bot_know = False
    else:
        bot_know = True

    try:
        user = await client1.fetch_user(user_id)
    except discord.errors.NotFound:
        error_embed = discord.Embed(title="ERROR", description="ID指定が間違っています", color=0xff0000)
        return error_embed

    user_info_embed = discord.Embed(title=user.name, color=0x000000)
    user_info_embed.set_thumbnail(url=user.avatar_url_as(format="png"))
    user_info_embed.add_field(name="botかどうか", value=f"{user.bot}", inline=False)
    user_made_time = (user.created_at + datetime.timedelta(hours=9)).strftime(r"%Y/%m/%d %H:%M")
    user_info_embed.add_field(name="アカウント作成日時", value=f"{user_made_time}　(JST)", inline=False)
    user_info_embed.add_field(name=f"{client1.user.name}の監視下にあるか", value=f"{bot_know}", inline=False)
    return user_info_embed


async def ch_info(client1, ch_id):
    """
    チャンネル情報を取得する関数
    discord.Embedを返す"""

    ch = client1.get_channel(ch_id)
    if not hasattr(ch, "name"): #chにnameという属性が無ければ
        error_embed = discord.Embed(title="ERROR", description="・ID指定が間違っている\n・DMである\n・本botの監視下にないチャンネル\nのいずれかです。", color=0xff0000)
        return error_embed

    ch_info_embed = discord.Embed(title=ch.name, color=0x000000)
    ch_made_time = (ch.created_at + datetime.timedelta(hours=9)).strftime(r"%Y/%m/%d %H:%M")
    ch_info_embed.add_field(name="チャンネル作成日時", value=f"{ch_made_time}　(JST)", inline=False)
    ch_info_embed.set_footer(text=ch.guild.name, icon_url=ch.guild.icon_url_as(format="png"))
    if isinstance(ch, discord.TextChannel):
        category = ch.category
        if category is None:
            category = "None"
        else:
            category = category.name
        pins = await ch.pins()
        if len(pins) <= 1:
            pinned_message = f"{len(pins)} message"
        else:
            pinned_message = f"{len(pins)} messages"
        topic = ch.topic
        if topic is None:
            topic = "None"
        ch_info_embed.add_field(name="ChannelType", value="テキストチャンネル", inline=False)
        ch_info_embed.add_field(name="所属カテゴリ", value=category, inline=False)
        ch_info_embed.add_field(name="トピック", value=topic, inline=False)
        ch_info_embed.add_field(name="ピン留め", value=pinned_message, inline=False)
        ch_info_embed.add_field(name="NSFW", value=f"{ch.is_nsfw()}", inline=True)
        ch_info_embed.add_field(name="NEWS", value=f"{ch.is_news()}", inline=True)
    elif isinstance(ch, discord.VoiceChannel):
        category = ch.category
        if category is None:
            category = "None"
        else:
            category = category.name
        if ch.user_limit == 0:
            user_limit = "上限なし"
        else:
            user_limit = ch.user_limit
        ch_info_embed.add_field(name="ChannelType", value="ボイスチャンネル", inline=False)
        ch_info_embed.add_field(name="所属カテゴリ", value=category, inline=False)
        ch_info_embed.add_field(name="音声ビットレート", value=f"{ch.bitrate}bit/s", inline=True)
        ch_info_embed.add_field(name="ユーザーリミット", value=user_limit, inline=True)
        #ch_info_embed.add_field(name="NSFW", value=f"{ch.is_nsfw()}", inline=True) 2.0の機能のため封印
    elif isinstance(ch, discord.CategoryChannel):
        texts = len(ch.text_channels)
        voices = len(ch.voice_channels)
        ch_info_embed.add_field(name="ChannelType", value="カテゴリチャンネル", inline=False)
        ch_info_embed.add_field(name="NSFW", value=ch.is_nsfw(), inline=False)
        ch_info_embed.add_field(name="保有チャンネル数", value=f"テキストチャンネル: {texts}\nボイスチャンネル: {voices}", inline=False)  
    else:
        ch_info_embed.add_field(name="ChannelType", value="不明", inline=False)

    return ch_info_embed


async def emoji_info(client1, emoji_id):
    """
    絵文字情報を取得する関数
    discord.Embedを返す"""

    emoji = client1.get_emoji(emoji_id)

    try:
        guild = client1.get_guild(emoji.guild_id)
    except AttributeError:
        error_embed = discord.Embed(title="ERROR", description="ID指定が間違っているか本botの監視下にない絵文字です", color=0xff0000)
        return error_embed
    emoji = await guild.fetch_emoji(emoji_id)

    if not emoji.animated:
        emoji_info_embed = discord.Embed(title=emoji.name, color=0x000000)
    else:
        emoji_info_embed = discord.Embed(color=0x000000)

    emoji_info_embed.set_thumbnail(url=emoji.url)
    emoji_info_embed.add_field(name="名前", value=emoji.name.replace("_", "\_"), inline=False)
    user = emoji.user
    if user is None:
        user = "不明"
    emoji_info_embed.add_field(name="作者", value=user, inline=False)
    emoji_info_embed.add_field(name="所属サーバ", value=guild.name, inline=False)
    emoji_info_embed.add_field(name="アニメーション", value=f"{emoji.animated}", inline=False)
    emoji_made_time = (emoji.created_at + datetime.timedelta(hours=9)).strftime(r"%Y/%m/%d %H:%M")
    emoji_info_embed.add_field(name="絵文字作成日時", value=emoji_made_time, inline=False)
    return emoji_info_embed