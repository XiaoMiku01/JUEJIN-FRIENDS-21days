# Web端cookie
cookie = """
此行删除后填写你的cookie
"""

# 打卡内容
content = "每日打卡"

### 下面不用改
import requests
import logging, time

logging.basicConfig(
    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s', level=logging.DEBUG
)


day_n = 0


def day():
    global day_n
    api = "https://api.juejin.cn/content_api/v1/short_msg/publish"
    headers = {
        "cookie": cookie.strip(),
        "content-type": "application/json",
    }
    json = {
        "content": "[7163537723910225960#JUEJIN FRIENDS 好好生活计划#] " + content + " day" + str(day_n),
        "sync_to_org": False,
        "theme_id": "7163537723910225960",
    }
    retry_times = 5
    while True:
        try:
            r = requests.post(api, headers=headers, json=json)
            if r.status_code == 200 and r.json()['err_msg'] == 'success':
                logging.info(f"day{day_n} 打卡成功")
            else:
                logging.error(f"day{day_n} 打卡失败 {r.text}")
            break
        except Exception as e:
            logging.error(f"day{day_n} 打卡失败 {e} 重试中")
            retry_times -= 1
            if retry_times == 0:
                logging.error(f"day{day_n} 打卡失败 重试次数超限，放弃")
                break
            time.sleep(5)
    day_n += 1


if __name__ == "__main__":
    import schedule

    day()  # 启动时先打卡一次
    schedule.every().day.at("00:01").do(day, day_n)
    while True:
        schedule.run_pending()
        time.sleep(1)
