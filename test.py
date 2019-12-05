import base64
import json
import requests
import traceback

IP_HOST = '182.254.155.218:9090'  # 上線地址
DOWNLOADER_SENDTASK = "http://{}/download/setTask"  # sendTask
DOWNLOADER_GETRESULT = "http://{}/download/getResult"  # getResult
TASK_SCHEDULER_IP = "http://{}/adslGetIp"

reqs = requests.session()
response = reqs.post(TASK_SCHEDULER_IP.format(IP_HOST), data={"type": 2}, timeout=30)
downloader_ip = str(response.text).strip()
data = {'user_id': 25,
        'headers': '{"User-Agent": "", "Cookie": ""}',
        'config': '{"redirect": 0, "priority": 2}',
        'urls': '[{"url": "", "type": 1, "unique_key": ""}]'
        }


def send_request(data, downloader_ip):
    rdata = reqs.post(DOWNLOADER_SENDTASK.format(downloader_ip), data=data, timeout=30)
    r = json.loads(rdata.text)
    if r["status"] == 1:  # 发送成功
        rdata = json.loads(r["rdata"])
        for i, k in enumerate(rdata):
            unique_md5 = k
            print(unique_md5)
    else:  # 发送失败
        print("set msg: {}".format(r["msg"]))
    return r["status"]


def get_result():
    try:
        data = {"user_id": 25,
                "config": '{"redirect": 0, "priority": 2}',
                "urls": '[{"url": "https://www.baidu.com/s?wd=%E9%B9%B0%E6%BD%AD%E7%B2%89%E5%88%B7%E7%9F%B3%E8%86%8F%E6%96%BD%E5%B7%A5", "type": 1, "unique_key": "c429da390659656e4676e7de7a5b20ac"}]'
                }
        rdata = reqs.post(DOWNLOADER_GETRESULT.format(downloader_ip), data=data, timeout=30)
        r = json.loads(rdata.text)
        if r["status"] == 1:
            unique_md5_results = json.loads(r["rdata"])
            for unique_md5 in unique_md5_results:
                if 'result' in unique_md5_results[unique_md5] and unique_md5_results[unique_md5]['result']:
                    html = base64.b64decode(unique_md5_results[unique_md5]['result'])
                    if html and isinstance(html, bytes):
                        try:
                            html = html.decode(encoding="utf-8", errors='ignore')  # bytes to str
                        except:
                            pass
                    unique_md5_results[unique_md5]['result'] = html
            return unique_md5_results
        else:
            print(r["status"])
    except:
        traceback.print_exc()


# status = send_request(data, downloader_ip)
unique_md5_results = get_result()
