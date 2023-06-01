import asyncio
import datetime
import json

import discord

import kei_server

async def on_guild_join(client1, guild):
    """
    本botがサーバに参加した際に呼び出される
    規約違反歴がなければ自己紹介をし、お知らせchと招待を作成する"""

    with open("./datas/ban_server.json", mode="r", encoding="utf-8") as f:
        ban_server_dict = json.load(f)

    if f"{guild.id}" in ban_server_dict.keys():
        try:
            await guild.owner.send(f"{guild.name}へ招待されましたが過去に本botの規約違反が確認されているため参加は行いません")
        except discord.errors.Forbidden:
            pass
        await guild.leave()
        return

    description = (
        f"初めましての方は初めまして、そうでない方はまたお会いしましたね。KirisameKei(mcid: kei_3104)制作の{client1.user.name}です。\n"
        f"このbotを{guild.name}に導入していただきありがとうございます。\n"
        "皆様にお願いしたいことがあります。このbotに極度に負荷をかけるような行為をしないでください。\n"
        "バグ、不具合等問題がありましたら`/bug_report`コマンドで報告ができます\n"
        "追加してほしい機能がありましたら`/new_func`コマンドで追加申請ができます\n"
        "問題がなかったらお楽しみください。\n"
        "最後に[私のサーバ](https://discord.gg/nrvMKBT)を宣伝・紹介させてください。"
        "このbotについてもっと知りたい、このbotを招待したい、けいの活動に興味がある、理由は何でも構いません。ぜひ見ていってください"
    )
    self_introduction_embed = discord.Embed(
        title="よろしくお願いします!!",
        description=description,
        color=0xffff00
    )
    kei = client1.get_user(523303776120209408)
    self_introduction_embed.set_footer(text="←KirisameKei(作者)", icon_url=kei.display_avatar.url)

    marisa_notice_ch_id = None
    try:
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(send_messages=False),
            guild.me: discord.PermissionOverwrite(send_messages=True)
        }
        marisa_notice_ch = await guild.create_text_channel(
            name="魔理沙からのお知らせ",
            overwrites=overwrites,
            position=0,
            topic="魔理沙botに関するお知らせが投稿されます",
            reason="魔理沙botの機能確保のため"
        )
    except discord.errors.Forbidden: #ch作成権限がなかった場合
        for ch in guild.text_channels:
            try:
                await ch.send(embed=self_introduction_embed)
                marisa_notice_ch_id = ch.id
                break
            except discord.errors.Forbidden:
                pass
    else:
        await marisa_notice_ch.send(embed=self_introduction_embed)
        marisa_notice_ch_id = marisa_notice_ch.id

    with open("./datas/marisa_notice.json", mode="r", encoding="utf-8") as f:
        marisa_notice_ch_dict = json.load(f)

    marisa_notice_ch_dict[f"{guild.id}"] = marisa_notice_ch_id

    marisa_notice_json = json.dumps(marisa_notice_ch_dict, indent=4)
    with open("./datas/marisa_notice.json", mode="w", encoding="utf-8") as f:
        f.write(marisa_notice_json)

    for ch in guild.text_channels:
        try:
            invite_url = await ch.create_invite(reason="けいを招待するため")
            await kei.send(invite_url)
            break
        except discord.errors.Forbidden:
            pass

    guild_join_embed = discord.Embed(
        title="╋",
        description=f"{client1.user.name}が{guild.name}に参加しました",
        color=0xfffffe
    )
    guild_join_embed.set_author(name=client1.user.name,icon_url=client1.user.display_avatar.url)
    guild_join_embed.set_footer(text=guild.name, icon_url=guild.icon)
    join_leave_notice_ch = client1.get_channel(709307324170240079)
    await join_leave_notice_ch.send(embed=guild_join_embed)


async def on_guild_remove(client1, guild):
    """
    本botがサーバから退出した際に呼び出される
    けい鯖にその旨を伝える"""

    with open("./datas/marisa_notice.json", mode="r", encoding="utf-8") as f:
        marisa_notice_dict = json.load(f)

    try:
        del marisa_notice_dict[f"{guild.id}"]
    except KeyError:
        pass

    marisa_notice_json = json.dumps(marisa_notice_dict, indent=4, ensure_ascii=False)
    with open("./datas/marisa_notice.json", mode="w", encoding="utf-8") as f:
        f.write(marisa_notice_json)

    guild_remove_embed = discord.Embed(
        title="━",
        description=f"{client1.user.name}が{guild.name}から退出しました",
        color=0xff0000
    )
    guild_remove_embed.set_author(name=client1.user.name, icon_url=client1.user.display_avatar.url)
    guild_remove_embed.set_footer(text=guild.name, icon_url=guild.icon)
    join_leave_notice_ch = client1.get_channel(709307324170240079)
    await join_leave_notice_ch.send(embed=guild_remove_embed)


async def on_member_join(client1, member):
    """
    サーバに参加者がいた際に呼び出される
    けい鯖にその旨を伝え、けい鯖なら専用の関数を呼ぶ"""

    when_from = (member.created_at + datetime.timedelta(hours=9)).strftime(r"%Y/%m/%d　%H:%M")
    member_embed = discord.Embed(title="╋", description=f"{member.mention}が{member.guild.name}に参加しました\n{when_from}からのdiscordユーザー", color=0xfffffe)
    member_embed.set_author(name=member.name, icon_url=member.display_avatar.url)
    member_embed.set_footer(text=member.guild.name, icon_url=member.guild.icon)
    join_leave_notice_ch = client1.get_channel(709307324170240079)
    await join_leave_notice_ch.send(embed=member_embed)

    if member.guild.id == 585998962050203672:
        await kei_server.on_member_join(client1, member)


async def on_member_remove(client1, member):
    """
    サーバに退出者がいた際に呼び出される
    けい鯖にその旨を伝え、けい鯖なら専用の関数を呼ぶ"""

    member_embed = discord.Embed(title="━", description=f"{member.mention}が{member.guild.name}から退出しました", color=0xff0000)
    member_embed.set_author(name=member.name, icon_url=member.display_avatar.url)
    member_embed.set_footer(text=member.guild.name, icon_url=member.guild.icon)
    join_leave_notice_ch = client1.get_channel(709307324170240079)
    await join_leave_notice_ch.send(embed=member_embed)

    if member.guild.id == 585998962050203672:
        await kei_server.on_member_remove(member)


async def quote_message(client1, message, url):
    """
    メッセージリンク展開用関数"""

    id_list = url.split("/")
    try:
        guild_id = int(id_list[0])
        channel_id = int(id_list[1])
        message_id = int(id_list[2].split()[0])
    except ValueError:
        await message.channel.send("メッセージリンクを魔改造しないでください")
        return

    channel = client1.get_channel(channel_id)
    if channel is None:
        guild_name = ""
        if id_list[0] == "237758724121427969":
            guild_name = "整地鯖"
        elif id_list[0] == "558125111081697300":
            guild_name = "KGx"

        faild_embed = discord.Embed(title="404", description=guild_name)
        await message.channel.send(embed=faild_embed)
        return

    try:
        msg = await channel.fetch_message(message_id)

        def quote_reaction(msg, embed):
            if msg.reactions:
                reaction_send = ""
                for reaction in msg.reactions:
                    emoji = reaction.emoji
                    count = str(reaction.count)
                    reaction_send = f"{reaction_send}{emoji}{count}"
                embed.add_field(name="reaction", value=reaction_send, inline=False)
            return embed

        if msg.content or msg.embeds or msg.attachments:
            embed = discord.Embed(description=f"{msg.content}\n\n[リンク](https://discordapp.com/channels/{guild_id}/{channel_id}/{message_id})", timestamp=msg.created_at)
            embed.set_author(name=msg.author, icon_url=msg.author.display_avatar.url)
            embed.set_footer(text=msg.channel.name, icon_url=msg.guild.icon)
            if msg.attachments:
                embed.set_image(url=msg.attachments[0].url)
            embed = quote_reaction(msg, embed)
            await message.channel.send(embed=embed)

            if len(msg.attachments) >= 2:
                for attachment in msg.attachments[1:]:
                    embed = discord.Embed().set_image(url=attachment.url)
                    await message.channel.send(embed=embed)

            for embed in msg.embeds:
                embed = quote_reaction(msg, embed)
                await message.channel.send(embed=embed)

        else:
            await message.channel.send("メッセージはありますが内容がありません")
    except discord.errors.NotFound:
        await message.channel.send("メッセージが見つかりません")


async def new_function(client1, message):
    """
    新機能追加申請用関数"""

    start_msg = (
        "```\n機能追加の申請をします。\n各項目は全て1回の送信で書いてください。\n"
        "各項目は10分でタイムアウトします。\n備考などがない場合はなしと入力してください。\n"
        "複雑な場合はけいに直接言っていただいても構いません。```"
    )

    msg_tuple = (
        "この依頼内容を公開してよろしいですか？\n良い場合はyes、悪い場合はnoと入力してください\n__**特殊な理由がない限りyesにしてください。**__(noの場合けいのDMに送られるためログが埋もれて忘れ去られる可能性があります。)",
        "何をしたら？\n例：/seichiと入力したら、16時になったら等",
        "何をする？\n例：整地鯖役職を付与する、チャンネルにあるメッセージをすべて消去する等",
        "チャンネル、役職の指定は？\n例：Hypixl役職持ちが実行すると怒られる、<#603832801036468244>を消す等",
        "その他備考は？\n他に要求がある場合ここに書いてください。",
    )
    reply_list = []

    def check1(m):#公開設定
        return m.author == message.author and m.channel == message.channel and m.content == "yes" or m.content == "no"
    def check2(m):#何をしたら？
        return m.author == message.author and m.channel == message.channel
    def check3(m):#何をする？
        return m.author == message.author and m.channel == message.channel
    def check4(m):#チャンネルや役職の指定は？
        return m.author == message.author and m.channel == message.channel
    def check5(m):#備考は？
        return m.author == message.author and m.channel == message.channel
    def check6(m):#これでいいですか？
        return m.author == message.author and m.channel == message.channel and m.content == "yes" or m.content == "no"

    check_tuple = (
        check1,
        check2,
        check3,
        check4,
        check5,
    )

    await message.channel.send(start_msg)
    for i in range(5): #msg_tupleをすべて送信する、msg_tupleの項目数が5
        await message.channel.send(msg_tuple[i])
        try:
            reply = await client1.wait_for("message", check=check_tuple[i], timeout=600)
            reply_list.append(reply)
        except asyncio.TimeoutError:
            await message.channel.send("タイムアウトしました。最初からやり直してください。")
            try:
                await message.channel.purge(after=message)
            except discord.errors.NotFound:
                pass
            return

    embed = discord.Embed(title="これで申請してよろしいですか？", description="良ければyes、やり直すならnoと入力してください", color=0xfffffe)
    embed.add_field(name="やりたいこと", value=f"{reply_list[1].content}{reply_list[2].content}", inline=False)
    embed.add_field(name="条件の指定", value=reply_list[3].content)
    embed.add_field(name="備考", value=reply_list[4].content)
    if reply_list[0].content == "yes":
        koukai_hikoukai = "公開"
    else:
        koukai_hikoukai = "非公開"
    embed.add_field(name="公開設定", value=koukai_hikoukai, inline=False)
    kakunin = await message.channel.send(embed=embed)

    try:
        reply = await client1.wait_for("message", check=check6, timeout=600)
    except asyncio.TimeoutError:
        await message.channel.send("タイムアウトしました。最初からやり直してください。")
        try:
            await message.channel.purge(after=message)
        except discord.errors.NotFound:
            pass
        return

    if reply.content == "yes":
        try:
            await message.channel.purge(before=kakunin, after=message)
        except discord.errors.NotFound:
            pass

        embed = discord.Embed(title="依頼が届きました", color=0x00ff00)
        embed.add_field(name="やりたいこと", value=f"{reply_list[1].content}{reply_list[2].content}", inline=False)
        embed.add_field(name="条件の指定", value=reply_list[3].content)
        embed.add_field(name="備考", value=reply_list[4].content)
        embed.set_author(name=message.author.name, icon_url=message.author.display_avatar.url)
        embed.set_footer(text=message.guild.name, icon_url=message.guild.icon)
        if reply_list[0].content == "no":#非公開なら
            send_place = "けいのDM"
            kei = client1.get_user(523303776120209408)
            await kei.send(embed=embed)
        else:
            send_place = "けいの実験サーバ「isueses」"
            notice_ch = client1.get_channel(636359382359080961)
            await notice_ch.send(content="<@523303776120209408>", embed=embed)

        await message.channel.send(f"依頼内容を{send_place}に送信しました。回答をお待ちください。\n疑問点がある、情報が不十分等の理由でDMを送らせていただく場合があります。")


    else:    
        try:
            await message.channel.purge(after=message)
        except discord.errors.NotFound:
            pass
        await message.channel.send("最初からやり直してください。")


async def bug_report(client1, message):
    """
    不具合報告用関数"""

    start_msg = (
        "```\n不具合の報告をします。\n各項目は全て1回の送信で書いてください。\n虚偽の報告はけいが不快になります。\n"
        "各項目は10分でタイムアウトします。\n複雑な場合はけいに直接言っていただいても構いません。```"
    )

    await message.channel.send(start_msg)
    await message.channel.send("いつ、どこで、誰が、何をしたら、どうなったかを詳しく書いてください。")

    def check1(m):
        return m.author == message.author and m.channel == message.channel

    try:
        reply = await client1.wait_for("message", check=check1, timeout=600)
    except asyncio.TimeoutError:
        await message.channel.send("タイムアウトしました。最初からやり直してください。")
        try:
            await message.channel.purge(after=message)
        except discord.errors.NotFound:
            pass
        return

    confirmation_embed = discord.Embed(title="この内容で報告してよろしいですか？", description="良ければyes、やり直すならnoと入力してください", color=0xfffffe)
    confirmation_embed.add_field(name="不具合の内容", value=reply.content)
    confirmation = await message.channel.send(embed=confirmation_embed)
    
    def check2(m):
        return m.author == message.author and m.channel == message.channel and (m.content == "yes" or m.content == "no")

    try:
        y_or_n = await client1.wait_for("message", check=check2, timeout=600)
    except asyncio.TimeoutError:
        await message.channel.send("タイムアウトしました。最初からやり直してください。")
        await confirmation.delete()
    else:
        if y_or_n.content == "yes":
            notice_ch = client1.get_channel(636359382359080961)
            now = datetime.datetime.now().strftime(r"%Y/%m/%d　%H:%M")
            notice_embed = discord.Embed(title="バグです！", description=reply.content, color=0xff0000)
            notice_embed.set_author(name=message.author.name, icon_url=message.author.display_avatar.url)
            notice_embed.set_footer(text=f"{message.guild.name}　{now}", icon_url=message.guild.icon)
            await notice_ch.send(content="<@523303776120209408>", embed=notice_embed)
            await message.channel.send(
                "不具合の報告ありがとうございます。内容をけいの実験サーバ「python開発やることリスト」に送信しました。\n"
                "疑問点がある、情報が不十分等の理由でメンションやDMをさせていただく場合があります。"
            )
        else:
            await message.channel.send("最初からやり直してください。")

        await y_or_n.delete()


async def form_link(message, command):
    """
    各フォームへのリンク"""

    if command == "report":
        await message.channel.send("https://docs.google.com/forms/d/e/1FAIpQLSfK9DQkUCD2qs8zATUuYIC3JuV3MyXRVCYjMb5g4g_hBUusSA/viewform")
    if command == "failure":
        await message.channel.send("https://docs.google.com/forms/d/e/1FAIpQLSdn9fTTs55c-oGLT3c68KVTGvfUjTK-W_cdataU7_XyzqcBRg/viewform")
    if command == "idea":
        #await message.channel.send("http://w4.minecraftserver.jp/ideaForm")
        await message.channel.send("https://docs.google.com/forms/d/e/1FAIpQLScB-XAHWnYePUpljd6swUfJTn6NJJNn74HgkqifxM7I3oxIMA/viewform")
    if command == "opinion":
        await message.channel.send("https://docs.google.com/forms/d/e/1FAIpQLSctLrByNvAiQop2lha9Mxn-D5p1OUaOf8JKQJCyAdggGBbzpg/viewform?c=0&w=1")
    if command == "donation":
        await message.channel.send("https://docs.google.com/forms/d/e/1FAIpQLSezwur20tx0JCQ0KMY0JiThYy7oEQDykFRiic96KxK17WOBwA/viewform?c=0&w=1")
    if command == "inquiry":
        #await message.channel.send("https://w4.minecraftserver.jp/inquiryForm")
        await message.channel.send("https://docs.google.com/forms/d/e/1FAIpQLSfqQLbeUQo1DxlL0Wy3A0129PerNrQHJB3Ner3ZEv62WGJywg/viewform")
    if command == "formal":
        await message.channel.send("https://www.seichi.network/gigantic")
    if command == "informal":
        await message.channel.send("https://seichi-click-network.sokuhou.wiki/")

    if command == "form":
        embed = discord.Embed(title="各フォームへのリンク一覧", color=0xff0000)
        embed.add_field(name="通報フォーム", value="https://docs.google.com/forms/d/e/1FAIpQLSfK9DQkUCD2qs8zATUuYIC3JuV3MyXRVCYjMb5g4g_hBUusSA/viewform", inline=False)
        embed.add_field(name="不具合フォーム", value="https://docs.google.com/forms/d/e/1FAIpQLSdn9fTTs55c-oGLT3c68KVTGvfUjTK-W_cdataU7_XyzqcBRg/viewform", inline=False)
        #embed.add_field(name="アイデアフォーム", value="http://w4.minecraftserver.jp/ideaForm", inline=False)
        embed.add_field(name="アイデアフォーム", value="https://docs.google.com/forms/d/e/1FAIpQLScB-XAHWnYePUpljd6swUfJTn6NJJNn74HgkqifxM7I3oxIMA/viewform", inline=False)
        embed.add_field(name="意見・感想フォーム", value="https://docs.google.com/forms/d/e/1FAIpQLSctLrByNvAiQop2lha9Mxn-D5p1OUaOf8JKQJCyAdggGBbzpg/viewform?c=0&w=1", inline=False)
        embed.add_field(name="寄付フォーム", value="https://docs.google.com/forms/d/e/1FAIpQLSezwur20tx0JCQ0KMY0JiThYy7oEQDykFRiic96KxK17WOBwA/viewform?c=0&w=1", inline=False)
        #embed.add_field(name="お問い合わせフォーム", value="https://w4.minecraftserver.jp/inquiryForm", inline=False)
        embed.add_field(name="お問い合わせフォーム", value="https://docs.google.com/forms/d/e/1FAIpQLSfqQLbeUQo1DxlL0Wy3A0129PerNrQHJB3Ner3ZEv62WGJywg/viewform", inline=False)
        await message.channel.send(embed=embed)


async def greeting(message):
    """
    おはよう、こんにちは、こんばんは、おやすみ、ありがとう
    が入ったメッセが送られたとき用の関数"""

    if message.author.bot:
        return

    now = datetime.datetime.now()
    if "おはよう" in message.content:
        if now.hour >= 5 and now.hour <= 9:
            await message.channel.send(f"おはようございます、{message.author.name}さん！")
        else:
            await message.channel.send("今おはよう！？")
    if "こんにちは" in message.content:
        if now.hour >= 9 and now.hour <= 17:
            await message.channel.send(f"こんにちは、{message.author.name}さん！")
        else:
            await message.channel.send("今こんにちは！？")
    if "こんばんは" in message.content:
        if (now.hour >= 17 and now.hour <= 23) or (now.hour >= 0 and now.hour <= 5):
            await message.channel.send(f"こんばんは、{message.author.name}さん！")
        else:
            await message.channel.send("今こんばんは！？")
    if "おやすみ" in message.content:
        if now.hour >= 18 and now.hour <= 20:
            await message.channel.send(f"{message.author.name}さんは早寝だね～。おやすみなさ～い")
        elif (now.hour >= 21 and now.hour <= 23) or now.hour == 0:
            await message.channel.send(f"おやすみなさい、{message.author.name}さん:zzz:")
        elif now.hour >= 1 and now.hour <= 3:
            await message.channel.send(f"夜更かしのしすぎには気を付けてね？おやすみなさい、{message.author.name}さん")
        elif now.hour >= 4 and now.hour <= 5:
            await message.channel.send("・・・")
        elif now.hour >= 6 and now.hour <= 10:
            await message.channel.send("二度寝っていいよね:+1:")
        else:
            await message.channel.send("お昼寝？おやすみ～")
    if "ありがとう" in message.content:
        await message.add_reaction("🍆")


async def end_reaction(message):
    """
    「少し放置」と「学校終わって三条」にendを付ける"""

    try:
        await message.add_reaction("🔚")
    except discord.errors.Forbidden:
        pass


async def change_prefix(message):
    """
    カスタムプレフィックスの変更"""

    if message.author.bot:
        return

    if not message.author.guild_permissions.administrator:
        await message.channel.send("このコマンドは管理者のみが使用できます")
        return

    prefix = message.content.split()[1]
    if prefix.startswith("//"):
        await message.channel.send("本botの別機能と競合するため「//」で始まるプレフィックスは使用できません")
        return
    elif "\\" in prefix:
        await message.channel.send("表示がややこしくなるためバックスラッシュを含むプレフィックスは使用できません")
        return
    elif message.mentions:
        await message.channel.send("メンションをプレフィックスに含むことはできません")
        return

    with open("./datas/custom_prefix.json", mode="r", encoding="utf-8") as f:
        custom_prefix_dict = json.load(f)

    custom_prefix_dict[f"{message.guild.id}"] = prefix

    custom_prefix_json = json.dumps(custom_prefix_dict, indent=4, ensure_ascii=False)
    with open("./datas/custom_prefix.json", mode="w", encoding="utf-8") as f:
        f.write(custom_prefix_json)

    await message.channel.send(f"{message.guild.name}でのプレフィックスを「{prefix}」に設定しました")


async def set_notice_ch(message, client1, command):
    """
    導入サーバすべてのお知らせチャンネルにお知らせを送信"""

    print("発火")

    if message.author.bot:
        return

    if not message.author.guild_permissions.administrator:
        await message.channel.send("このコマンドは管理者のみが使用できます")
        return

    with open("./datas/marisa_notice.json", mode="r", encoding="utf-8") as f:
        notice_ch_dict = json.load(f)

    if command == "set_notice_ch":
        notice_ch_dict[f"{message.guild.id}"] = message.channel.id
        try:
            await message.channel.send("このチャンネルに全体通知を送信します")
        except discord.errors.Forbidden:
            await message.author.send(f"{message.channel.mention}で{client1.user.name}が喋ることはできません。権限を与えるかチェンネルを変更してください")

    elif command.lower() == "set_notice_ch none":
        notice_ch_dict[f"{message.guild.id}"] = "rejected"
        await message.channel.send("全体通知受信を拒否しました")

    else:
        await message.channel.send("`/set_notice_ch`で実行チャンネルを通知チャンネルに、`/set_notice_ch None`で通知拒否")

    with open("./datas/marisa_notice.json", mode="w", encoding="utf-8") as f:
        notice_ch_json = json.dumps(notice_ch_dict, indent=4)
        f.write(notice_ch_json)


async def check_notice_ch(message):
    """
    全体通知チャンネルを確認する"""

    with open("./datas/marisa_notice.json", mode="r", encoding="utf-8") as f:
        notice_ch_dict = json.load(f)

    try:
        notice_ch_id = notice_ch_dict[f"{message.guild.id}"]
    except KeyError:
        notice_ch_id = 0
        notice_ch_dict[f"{message.guild.id}"] = 0 #これで記録すれば全体通知使用時にchannelがNoneになる

    if notice_ch_id == "rejected":
        await message.channel.send("通知を拒否しています。`/set_notice_ch`を実行すると実行チャンネルで本botに関する通知を受け取れます")
    elif notice_ch_id == 0:
        with open("./datas/marisa_notice.json", mode="w", encoding="utf-8") as f:
            notice_ch_json = json.dumps(notice_ch_dict, indent=4)
            f.write(notice_ch_json)
        await message.channel.send("未設定、発言権のある一番上のチャンネルで通知を行います")
    else:
        await message.channel.send(f"<#{notice_ch_id}>")


async def help(message, command, client1):
    """
    ヘルプ表示用関数"""

    try:
        need_help_command = command.split()[1]
    except IndexError:
        with open("./datas/custom_prefix.json", mode="r", encoding="utf-8") as f:
            custom_prefix_dict = json.load(f)

        try:
            custom_prefix = custom_prefix_dict[f"{message.guild.id}"]
        except KeyError:
            custom_prefix = "/"

        help_embed = discord.Embed(
            title=f"{client1.user.name}のヘルプ",
            description=f"「/」は{message.guild.name}のプレフィックス( {custom_prefix} )に変換してください",
            color=0xffcc00
        )

        common_help = "**/help**"
        common_help += "\n**/new_func**"
        common_help += "\n**/bug_report**"
        common_help += "\n**/set_notice_ch**"
        common_help += "\n**/set_notice_ch None**"
        common_help += "\n**/check_notice_ch**"
        common_help += "\n**/report**"
        common_help += "\n**/failure**"
        common_help += "\n**/idea**"
        common_help += "\n**/opinion**"
        common_help += "\n**/donation**"
        common_help += "\n**/inquiry**"
        common_help += "\n**/formal**"
        common_help += "\n**/informal**"
        common_help += "\n**/form**"
        help_embed.add_field(name="全サーバ共通のコマンド", value=common_help, inline=False)

        common_help = "・メッセージリンクを貼ると展開します"
        common_help += "\n・MEE6の発言に:middle_finger:をつけます"
        common_help += "\n・挨拶やお礼に反応します"
        common_help += "\n・「少し放置」と「学校終わって三条」にendリアクションを付けます"
        help_embed.add_field(name="全サーバ共通の機能", value=common_help, inline=False)

        local_command_help = None
        if message.guild.id == 585998962050203672: #けい鯖
            local_command_help = "**/break␣MCID**"
            local_command_help += "\n**/build␣MCID**"
            local_command_help += "\n**/daily␣MCID**"
            local_command_help += "\n**/last_login␣MCID**"
            local_command_help += "\n**/mcavatar MCID**"
            local_command_help += "\n**/stack_eval␣args**"
            local_command_help += "\n**/stack_eval64␣args**"
            local_command_help += "\n**/stack_eval16␣args**"
            local_command_help += "\n**/stack_eval1␣args**"
            local_command_help += "\n**/info␣[role, guild, user, ch, emoji]␣ID**"
            local_command_help += "\n**/random␣[choice, sample, choices, randint]␣args**"
            local_command_help += "\n**/weather␣[map, 地点名]**"
            local_command_help += "\n**/vote␣args**"
            local_command_help += "\n**/name␣n**"
            local_command_help += "\n**/user_data␣ID** or **/user_data**"
            local_command_help += "\n**/mypt**"
            local_command_help += "\n**/ranking␣[point(pt), speak]␣n(n≧1)**"
            local_command_help += "\n/**glist**"
            local_command_help += "\n/**accept**"
            local_command_help += "\n以下KirisameKei専用(部外者が使用するとドM役職を付与されます)"
            local_command_help += "\n**/delmsg** or **/delmsg␣n(n≧0)** or **/delmsg␣area␣msgID␣msgID**"
            local_command_help += "\n**/mcid␣[add, del]␣ID␣MCID**"
            local_command_help += "\n**/point(/pt)␣[sum, add, use set, crd]␣ID␣n(n≧0)**"
            local_command_help += "\n**/remove_role␣ID**"
            local_command_help += "\n**/datas**"
            local_command_help += "\n**/before_ban␣ID**"
            local_command_help += "\n**/unban␣ID**"
            local_command_help += "\n**/delete_user_data␣ID**"
            local_command_help += "\n**/ban_list**"
            local_command_help += "\n**/gban_list**"
            local_command_help += "\n**/global_notice␣content**"
            local_command_help += "\n**/leave_guild␣ID␣reason**"

            local_help = "・<#664286990677573680>のメッセージにリアクションを付けると役職が着脱されます"
            local_help += "\n・発言のログが取られています"
            local_help += "\n・<#634602609017225225>で発言すると確率でポイントが貰えます"
            local_help += "\n・毎週日曜日にしりとりチャンネルをリセットします"
            local_help += "\n・<#762546731417731073>や<#762546959138816070>で作られた物語を記録します"
            local_help += "\n・しりとりチャンネルで「ん」か「ン」で終わるメッセージを投稿すると続けてくれます"
            local_help += "\n・毎日9:10に投票通知役職持ちにメンションを飛ばします"
            local_help += "\n・毎日日付変更をお知らせし、本鯖のステータスを表示します"

        elif message.guild.id == 587909823665012757: #無法地帯
            local_command_help = "**/break␣MCID**"
            local_command_help += "\n**/build␣MCID**"
            local_command_help += "\n**/daily␣MCID**"
            local_command_help += "\n**/last_login␣MCID**"
            local_command_help += "\n**/mcavatar MCID**"
            local_command_help += "\n**/stack_eval␣args**"
            local_command_help += "\n**/stack_eval64␣args**"
            local_command_help += "\n**/stack_eval16␣args**"
            local_command_help += "\n**/stack_eval1␣args**"
            local_command_help += "\n**/info␣[role, guild, user, ch, emoji]␣ID**"
            local_command_help += "\n**/random␣[choice, sample, choices, randint]␣args**"
            local_command_help += "\n**/weather␣[map, 地点名]**"
            local_command_help += "\n**/vote␣args**"
            local_command_help += "\n**/name␣n**"

            local_help = "・MEE6の発言に悪態をつきます"
            local_help += "\n・毎日正午にサーバアイコンを変更します"

        elif message.guild.id == 735632039050477649: #絵文字鯖
            local_command_help = "**/break␣MCID**"
            local_command_help += "\n**/build␣MCID**"
            local_command_help += "\n**/daily␣MCID**"
            local_command_help += "\n**/last_login␣MCID**"
            local_command_help += "\n**/mcavatar MCID**"
            local_command_help += "\n**/stack_eval␣args**"
            local_command_help += "\n**/stack_eval64␣args**"
            local_command_help += "\n**/stack_eval16␣args**"
            local_command_help += "\n**/stack_eval1␣args**"
            local_command_help += "\n**/info␣[role, guild, user, ch, emoji]␣ID**"
            local_command_help += "\n**/random␣[choice, sample, choices, randint]␣args**"
            local_command_help += "\n**/weather␣[map, 地点名]**"
            local_command_help += "\n**/vote␣args**"

            local_help = "・絵文字の作成、変更、削除を記録します"
            local_help += "\n・絵文字作成時にバックアップを取ります"

        elif message.guild.id in (863367920612802610, 659375053707673600): #あんず鯖
            local_command_help = "**/break␣MCID**"
            local_command_help += "\n**/build␣MCID**"
            local_command_help += "\n**/daily␣MCID**"
            local_command_help += "\n**/last_login␣MCID**"
            local_command_help += "\n**/mcavatar MCID**"
            local_command_help += "\n**/stack_eval␣args**"
            local_command_help += "\n**/stack_eval64␣args**"
            local_command_help += "\n**/stack_eval16␣args**"
            local_command_help += "\n**/stack_eval1␣args**"
            local_command_help += "\n**/info␣[role, guild, user, ch, emoji]␣ID**"
            local_command_help += "\n**/random␣[choice, sample, choices, randint]␣args**"
            local_command_help += "\n**/weather␣[map, 地点名]**"
            local_command_help += "\n**/vote␣args**"
            local_command_help += "\n**/name␣n**"

        elif message.guild.id in (876143248471621652, 660445544296218650): #いろは鯖
            local_command_help = "**/break␣MCID**"
            local_command_help += "\n**/build␣MCID**"
            local_command_help += "\n**/daily␣MCID**"
            local_command_help += "\n**/last_login␣MCID**"
            local_command_help += "\n**/mcavatar MCID**"
            local_command_help += "\n**/stack_eval␣args**"
            local_command_help += "\n**/stack_eval64␣args**"
            local_command_help += "\n**/stack_eval16␣args**"
            local_command_help += "\n**/stack_eval1␣args**"
            local_command_help += "\n**/info␣[role, guild, user, ch, emoji]␣ID**"
            local_command_help += "\n**/random␣[choice, sample, choices, randint]␣args**"
            local_command_help += "\n**/weather␣[map, 地点名]**"
            local_command_help += "\n**/vote␣args**"
            local_command_help += "\n**/name␣n**"

        elif message.guild.id == 812096632714690601: #起きてー
            local_command_help = "**/break␣MCID**"
            local_command_help += "\n**/build␣MCID**"
            local_command_help += "\n**/daily␣MCID**"
            local_command_help += "\n**/last_login␣MCID**"
            local_command_help += "\n**/mcavatar MCID**"
            local_command_help += "\n**/stack_eval␣args**"
            local_command_help += "\n**/stack_eval64␣args**"
            local_command_help += "\n**/stack_eval16␣args**"
            local_command_help += "\n**/stack_eval1␣args**"
            local_command_help += "\n**/info␣[role, guild, user, ch, emoji]␣ID**"
            local_command_help += "\n**/random␣[choice, sample, choices, randint]␣args**"
            local_command_help += "\n**/weather␣[map, 地点名]**"
            local_command_help += "\n**/vote␣args**"
            local_command_help += "\n**/name␣n**"

        elif message.guild.id == 985092628594978867: #ぴかちゅう鯖
            local_command_help = "**/break␣MCID**"
            local_command_help += "\n**/build␣MCID**"
            local_command_help += "\n**/daily␣MCID**"
            local_command_help += "\n**/last_login␣MCID**"
            local_command_help += "\n**/mcavatar MCID**"
            local_command_help += "\n**/stack_eval␣args**"
            local_command_help += "\n**/stack_eval64␣args**"
            local_command_help += "\n**/stack_eval16␣args**"
            local_command_help += "\n**/stack_eval1␣args**"
            local_command_help += "\n**/info␣[role, guild, user, ch, emoji]␣ID**"


        elif message.guild.id == 731437075622133861: #徹夜鯖
            local_command_help = "\n**/daily␣MCID**"


        if local_command_help is not None:
            help_embed.add_field(name=f"{message.guild.name}でのコマンド", value=local_command_help, inline=False)
        if local_help is not None:
            help_embed.add_field(name=f"{message.guild.name}での機能", value=local_help, inline=False)

        await message.channel.send(embed=help_embed)

    else:
        command_tuple_key = (
            "break",
            "build",
            "daily",
            "last_login",
            "mcavatar",
            "stack_eval",
            "stack_eval64",
            "stack_eval16",
            "stack_eval1",
            "info",
            "random",
            "weather",
            "vote",
            "name",
            "user_data",
            "mypt",
            "ranking",
            "glist",
            "accept"
        )
        command_tuple_value = (
            "MCIDの総合整地量と順位、レベルを表示します",
            "MCIDの総合建築量と順位、レベルを表示します",
            "MCIDの日間整地・建築量と順位を表示します",
            "MCIDの整地鯖への最終ログイン日時を表示します(現在リンク貼り付け)",
            "MCIDの正面からのスキンを表示します",
            "マイクラのアイテム数計算をします 1st=64のアイテムが対象",
            "マイクラのアイテム数計算をします 1st=64のアイテムが対象",
            "マイクラのアイテム数計算をします 1st=16のアイテムが対象",
            "マイクラのアイテム数計算をします 1st=1のアイテムが対象",
            "役職、サーバ、ユーザ、チャンネル、絵文字の情報を表示します",
            "引数からランダムに選出します pythonが分かる方向け",
            "引数の地域の天気予報を表示します mapで天気図を表示します",
            "投票をします 第一引数が投票名、第二引数以降が候補 第二引数以下がない場合○×投票",
            "引数文字の名前をランダムで作成します",
            "引数のIDを持つユーザーのけいの実験サーバでの情報を表示します 引数がない場合実行者の情報",
            "実行者の保有ptを表示します",
            "発言数・ポイントランキングを表示します 第二引数に数字を入れると21位以下が表示されます",
            f"{client1.user.name}が導入されているサーバの一覧を表示します",
            "けいの実験サーバの規約に同意し発言権を得ます"
        )

        try:
            index = command_tuple_key.index(need_help_command)
        except ValueError:
            description = ", ".join(command_tuple_key)
            await message.channel.send(f"そのコマンドはhelpにありません```\n{description}```")
            return

        await message.channel.send(command_tuple_value[index])