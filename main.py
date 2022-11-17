# Web端cookie
cookies = [
    """
删除此行，填入你的cookie
"""
]
# 支持多账号 格式为 ["""cookie1""", """cookie2""", """cookie3"""]

# 打卡时间(24小时制)
time_str = "00:01"

### 下面不用改
import hmac
import zlib
import requests
import logging, time, random
import hashlib

logging.basicConfig(
    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s', level=logging.INFO
)


day_n = 1


def random_str(n):
    return ''.join(random.sample('zyxwvutsrqponmlkjihgfedcba0123456789', n))


def hash256(msg):
    return hashlib.sha256(msg.encode('utf-8')).hexdigest()


def hmac_hash256(key, msg):
    if type(key) == str:
        return hmac.new(key.encode('utf-8'), msg.encode('utf-8'), hashlib.sha256)
    elif type(key) == hmac.HMAC:
        return hmac.new(key.digest(), msg.encode('utf-8'), hashlib.sha256)


def fileCRC32(file_buffer):
    return hex(zlib.crc32(file_buffer) & 0xFFFFFFFF)[2:]


def u(params):
    new_params = sorted(params.items(), key=lambda x: x[0])
    new_params = [f"{k}={v}" for k, v in new_params]
    return "&".join(new_params)


class JJRequest:
    def __init__(self, e, t, api, method="GET", params=None, data=None):
        self.t = t
        self.e = e
        self.api = api
        self.method = method
        self.params = params
        self.data = data

    def getAuthorization(self):
        return f"AWS4-HMAC-SHA256 Credential={self.e['AccessKeyId']}/{self.t[0:8]}/cn-north-1/imagex/aws4_request, SignedHeaders=x-amz-date;x-amz-security-token, Signature={self.signature()}"

    def signature(self):
        r = self.getSigningKey()
        return hmac_hash256(r, self.stringToSign()).hexdigest()

    def getSigningKey(self, r="cn-north-1", n="imagex"):
        o = hmac_hash256("AWS4" + self.e['SecretAccessKey'], str(self.t[0:8]))
        i = hmac_hash256(o, str(r))
        s = hmac_hash256(i, str(n))
        return hmac_hash256(s, "aws4_request")

    def stringToSign(self):
        t = []
        t.append("AWS4-HMAC-SHA256")
        t.append(self.t)
        t.append(self.credentialString())
        t.append(hash256(self.canonicalString()))
        return "\n".join(t)

    def credentialString(self, region="cn-north-1", serviceName="imagex"):
        return "/".join([self.t[0:8], region, serviceName, "aws4_request"])

    def canonicalString(self):
        e = []
        e.append(self.method)
        e.append("/")
        e.append(u(self.params))
        e.append(self.canonicalHeaders())
        e.append(self.signedHeaders())
        e.append(self.hexEncodedBodyHash())
        return "\n".join(e)

    def canonicalHeaders(self):
        return f"x-amz-date:{self.t}\nx-amz-security-token:{self.e['SessionToken']}\n"

    def signedHeaders(self):
        return "x-amz-date;x-amz-security-token"

    def hexEncodedBodyHash(self):
        return hash256("")


def get_token(cookie):
    api = "https://api.juejin.cn/imagex/gen_token?client=web"
    headers = {
        "cookie": cookie.strip(),
    }
    r = requests.get(api, headers=headers)
    if r.status_code == 200 and r.json()['err_msg'] == "success":
        return r.json()['data']['token']
    else:
        logging.error("获取token失败", r.text)
        return None


def get_url(uri):
    api = "https://api.juejin.cn/imagex/get_img_url"
    params = {
        "uri": uri,
    }
    resp = requests.get(api, params=params)
    if resp.status_code == 200 and resp.json()['err_msg'] == "success":
        return [resp.json()['data']['main_url']]
    else:
        logging.error("获取图片地址失败", resp.text)
        return []


def uploadImage(cookie):
    e = get_token(cookie)
    if e is None:
        logging.error("获取token失败")
        return []
    t = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    params = {
        "Action": "ApplyImageUpload",
        "Version": "2018-08-01",
        "ServiceId": "k3u1fbpfcp",
        "s": random_str(11),
    }
    r = JJRequest(e, t, "https://imagex.bytedanceapi.com/", method="GET", params=params)
    headers = {
        'authorization': r.getAuthorization(),
        'x-amz-date': t,
        'x-amz-security-token': e['SessionToken'],
    }
    resp = requests.get(r.api, params=params, headers=headers).json()
    if "Result" not in resp:
        logging.error(resp)
        return []
    StoreUri = resp['Result']['UploadAddress']['StoreInfos'][0]['StoreUri']
    uploadUrl = f"https://{resp['Result']['UploadAddress']['UploadHosts'][0]}/{resp['Result']['UploadAddress']['StoreInfos'][0]['StoreUri']}"
    Authorization = resp['Result']['UploadAddress']['StoreInfos'][0]['Auth']
    # SessionKey = resp['Result']['UploadAddress']['SessionKey']
    upload_id_resp = requests.post(uploadUrl + "?uploads", headers={"Authorization": Authorization})
    if upload_id_resp.status_code != 200 and upload_id_resp.json()['error']["code"] != 200:
        logging.error(upload_id_resp.text)
        return []
    # upload_id = upload_id_resp.json()['payload']['uploadID']
    # image_path = "QQ图片20211214141318.jpg"
    # with open(image_path, "rb") as f:
    #     image = f.read()
    image = get_as_pic()
    if image is None:
        logging.error("获取图片失败")
        return []
    part_number = 1
    image_resp = requests.put(
        uploadUrl,
        # params={
        #     "partNumber": part_number,
        #     "uploadID": upload_id,
        # },
        headers={
            "authorization": Authorization,
            "content-length": str(len(image)),
            "content-Type": "application/octet-stream",
            "content-crc32": fileCRC32(image),
        },
        data=image,
    )
    # print(StoreUri)
    if image_resp.status_code != 200 and image_resp.json()['error']["code"] != 200:
        logging.error(image_resp.text)
        return []
    # logging.info(image_resp.text)

    # hash_resp = requests.post(
    #     uploadUrl, params={"uploadID": upload_id}, headers={"Authorization": Authorization}
    # )
    # if image_resp.status_code != 200 and image_resp.json()['error']["code"] != 200:
    #     logging.error(hash_resp.text)
    #     return []
    # logging.info(hash_resp.json())

    # t = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    # params = {
    #     "Action": "CommitImageUpload",
    #     "Version": "2018-08-01",
    #     "ServiceId": "k3u1fbpfcp",
    #     "SessionKey": SessionKey,
    # }
    # r = JJRequest(e, t, "https://imagex.bytedanceapi.com/", method="POST", params=params)
    # headers = {
    #     'authorization': r.getAuthorization(),
    #     'x-amz-date': t,
    #     'x-amz-security-token': e['SessionToken'],
    # }
    # resp = requests.post(r.api, params=params, headers=headers)
    # print(resp.text)
    return get_url(StoreUri)


def get_hitokoto():
    api = "https://v1.hitokoto.cn"
    r = requests.get(api)
    if r.status_code == 200:
        return f"每日一言: \n {r.json()['hitokoto']} \n ———— {r.json()['from']}"
    else:
        return "每日打卡"


def get_as_pic():
    try:
        api = f"https://api.asoulfanart.com:9000/getPic?nocache={int(time.time())}&page=1&tag_id=0&sort=3&part=0&rank=0&ctime=0&type=1"
        r = requests.get(api, verify=False)
        if r.status_code == 200:
            url = random.choice(r.json())['pic_url'][0]
            imgBytes = requests.get(url['img_src']).content
            return imgBytes
        else:
            print(r.status_code)
            # print("获取图片失败")
            return None
    except Exception as e:
        logging.error(e)
        return None


def day():
    global day_n
    for cookie in cookies:
        api = "https://api.juejin.cn/content_api/v1/short_msg/publish"
        headers = {
            "cookie": cookie.strip(),
            "content-type": "application/json",
        }
        json = {
            "content": "[7163537723910225960#JUEJIN FRIENDS 好好生活计划#] " + get_hitokoto() + " day" + str(day_n),
            "pic_list": uploadImage(cookie),
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
        time.sleep(5)
    day_n += 1


if __name__ == "__main__":
    import schedule
    import datetime

    day()  # 启动时先打卡一次
    schedule.every().day.at(time_str).do(day)
    while True:
        schedule.run_pending()
        time.sleep(1)
        if datetime.datetime.now().year == 2023:
            logging.info("2023年了，活动结束")
            break
