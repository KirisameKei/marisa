import datetime
import json
import os
import time
import traceback

import requests
import schedule

avatar_url = "https://cdn.discordapp.com/attachments/644880761081561111/1038733192926085150/icon_score.png"

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
    error_notice_webhook_url = os.getenv("error_notice_webhook")
    requests.post(error_notice_webhook_url, json.dumps(error_content), headers={"Content-Type": "application/json"}) #エラーメッセをウェブフックに投稿


def login():
    """
    プログラム起動時の処理"""

    login_webhook_url = "https://discordapp.com/api/webhooks/702892881677123685/aZk-JM-eaMyPBNDZMWhEtUxVNOTFwoCueUl0d6L48tXplbsALsA1fzuyF6mi9yowa6JL"
    main_content = {
            "username": "Score記録",
            "avatar_url": avatar_url,
            "content": f"{os.path.basename(__file__)}により起動"
        }
    requests.post(login_webhook_url, main_content) #ログインメッセをウェブフックに投稿


def get_score():
    try:
        url = "https://seichi-game-data.public-gigantic-api.seichi.click/prometheus_v2_metrics"
        try:
            res = requests.get(url, timeout=(6.0, 24.0))
            res.raise_for_status()
            all_data_txt = res.text

        except requests.exceptions.Timeout:
            wh_url = "https://discord.com/api/webhooks/1018999579481473104/xXH7MPNJgfI11dhEXgyJwQ2pg03VrlgPdeVyiOTSqsMyoW_FjdeXymgjQJmbdzqMGHOR"
            now = datetime.datetime.now().strftime("%H:%M") #今何時？
            content = {
                "username": "Score記録",
                "avatar_url": avatar_url,
                "content": f"reqests.exeption.Timeout\n{now}"
            }
            requests.post(wh_url, content)
            return

        except requests.exceptions.HTTPError:
            wh_url = "https://discord.com/api/webhooks/1018999579481473104/xXH7MPNJgfI11dhEXgyJwQ2pg03VrlgPdeVyiOTSqsMyoW_FjdeXymgjQJmbdzqMGHOR"
            now = datetime.datetime.now().strftime("%H:%M") #今何時？
            content = {
                "username": "Score記録",
                "avatar_url": avatar_url,
                "content": f"整地鯖APIが落ちてたら何もできないね！\n{now}"
            }
            requests.post(wh_url, content)
            return

        all_data_list = all_data_txt.split("\n")

        date_change = False
        daily_standard_time = False
        if datetime.datetime.now().hour == 0 and datetime.datetime.now().minute == 0:
            date_change = True

        elif datetime.datetime.now().hour == 0 and datetime.datetime.now().minute == 1:
            daily_standard_time = True

        with open("./datas/player_data.json", mode="r", encoding="utf-8") as f:
            player_data_dict = json.load(f)

        #player_data_dict = {
        #    "uuid": {
        #        "total_break": 10000, #総合整地量、毎分更新
        #        "break": 1000,        #日付変更時の整地量、日間整地量ではないので注意
        #        "total_build": 100,   #総合建築量、毎分更新
        #        "build": 50           #日付変更時の整地量、日間整地量ではないので注意
        #    }                         #日間はtotal - todayで算出すること
        #}

        with open("./datas/daily_player_data.json", mode="r", encoding="utf-8") as f:
            daily_score_dict = json.load(f)

        for all_data in all_data_list:
            if not "#" in all_data and all_data != "":
                uuid = all_data.split('"')[1]

                data = int(all_data.split(" ")[1]) #この時点で整地量か建築量か接続時間か投票数かはわからない
                try:
                    player_data = player_data_dict[uuid]
                except KeyError:
                    player_data_dict[uuid] = {"total_break": 0, "break": 0, "total_build": 0, "build": 0}
                    player_data = player_data_dict[uuid]

                break_or_build = False
                if "break_count" in all_data:
                    score_type_total = "total_break"
                    score_type_daily = "break"
                    break_or_build = True
                elif "build_count" in all_data:
                    score_type_total = "total_build"
                    score_type_daily = "build"
                    break_or_build = True

                if break_or_build:
                    player_data[score_type_total] = data

                    if daily_standard_time:
                        player_data[score_type_daily] = data

                    score = player_data[score_type_total] - player_data[score_type_daily]
                    if score != 0:
                        try:
                            daily_score = daily_score_dict[uuid]
                        except KeyError:
                            try:
                                res = requests.get(f"https://sessionserver.mojang.com/session/minecraft/profile/{uuid}")
                                res.raise_for_status()
                                mcid_uuid_data = res.json()
                            except requests.exceptions.HTTPError:
                                wh_url = "https://discord.com/api/webhooks/1018999579481473104/xXH7MPNJgfI11dhEXgyJwQ2pg03VrlgPdeVyiOTSqsMyoW_FjdeXymgjQJmbdzqMGHOR"
                                now = datetime.datetime.now().strftime("%H:%M") #今何時？
                                content = {
                                    "username": "Score記録",
                                    "avatar_url": avatar_url,
                                    "content": f"mojanAPIが落ちてちゃ何もできないね！\n{now}"
                                }
                                requests.post(wh_url, content)
                                return

                            mcid = mcid_uuid_data["name"]

                            daily_score_dict[uuid] = {"mcid": mcid, "break": 0, "build": 0}
                            daily_score = daily_score_dict[uuid]
                            time.sleep(0.1)

                        daily_score[score_type_daily] = score

        player_data_json = json.dumps(player_data_dict, indent=4)
        with open("./datas/player_data.json", mode="w", encoding="utf-8") as f:
            f.write(player_data_json)

        daily_score_new_dict = {}
        for uuid, value in sorted(daily_score_dict.items(), key=lambda x: -x[1]["break"]):
            daily_score_new_dict[uuid] = value

        daily_score_json = json.dumps(daily_score_new_dict, indent=4)
        if date_change:
            yesterday = (datetime.date.today() - datetime.timedelta(days=1)).strftime(r"%Y%m%d")
            with open(f"./datas/archive/daily_player_data_{yesterday}.json", mode="w", encoding="utf-8") as f:
                f.write(daily_score_json)

            with open("./datas/daily_player_data.json", mode="w", encoding="utf-8") as f:
                f.write(r"{}")
        else:
            with open("./datas/daily_player_data.json", mode="w", encoding="utf-8") as f:
                f.write(daily_score_json)

    except:
        unexpected_error()


try:
    login()
    schedule.every(1).minutes.do(get_score)

    #ちょっとは動作軽くしたいじゃん？一秒間に何回も確認してたら重くなるやん？ってことで1秒休み
    while True:
        schedule.run_pending()
        time.sleep(1)

except:
    unexpected_error()