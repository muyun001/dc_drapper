# -*- coding: utf-8 -*-
from util.util import Util
from util.store import Store
from download_center.new_spider.downloader.downloader import SpiderRequest
from download_center.new_spider.spider.basespider import BaseSpider

import os
import time
import traceback
import sys

PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.append(PROJECT_PATH)


class DCWrapper(BaseSpider):
    """
    打包下载中心
    读取保存的下发接口的数据，组成下载中心的Request对象，下发到下载中心。
    保留下载中心的逻辑，并把抓取结果存储下来以备"获取接口"来拿(Redis)。
    """

    def __init__(self):
        super(DCWrapper, self).__init__()
        self.util = Util()
        self.store = Store()
        self.sleep_time = 5  # 没有任务休眠时间
        self.sending_queue_max = 8000  # sending_queue 最大值
        self.send_url_to_sended_queue()

    def send_url_to_sended_queue(self):
        """
        每次初始运行时,将status为1的url重新发送至sended_queue.
        为了防止死循环,url发送之后先将status置为临时状态5,
        所有url发送完后再将status重新置为1.
        """
        temp_status = 5  # 设置一个临时状态
        unique_keys = list()
        try:
            while True:
                condition = {'status': 1}  # 查询status=1的数据
                request_datas = self.store.read_request_datas(condition)
                if request_datas is not None:
                    unique_keys.append(request_datas['unique_key'])
                    try:
                        headers, configs, urls = self.parameter_format(request_datas)
                        spider_request = SpiderRequest(headers=headers, urls=urls, config=configs)
                        self.sending_queue.put(spider_request)
                        self.store.update_status(request_datas['unique_key'], temp_status)  # 将状态改为临时状态
                    except:
                        self.store.update_status(request_datas['unique_key'], -1)  # 请求发送失败,则将mongo中原数据的status置为-1
                        traceback.print_exc()
                else:
                    break

            # 将临时状态的status改为1
            for unique_key in unique_keys:
                self.store.update_status(unique_key, 1)
            del unique_keys  # 从内存中删除变量
        except:
            print("send_uncomplished_url_to_dc error")
            traceback.print_exc()

    def get_user_password(self):
        return 'fxt', 'fxt_spider'

    def get_stores(self):
        stores = list()
        return stores

    def parameter_format(self, request):
        """
        参数格式转变:将mongo数据库中的数据格式,转变为下载中心需要的request样式
        """
        headers = {
            'User-Agent': request['request']['user_agent'],
            'Cookie': request['request']['cookie']
        }
        configs = {
            "conf_district_id": self.util.get_city_num(request['config']['district']),
            "redirect": self.util.get_redirect_num(request['config']['follow_redirect']),
            "priority": self.util.get_priority_num(request['config'].get('priority', 'normal')),
            "post_data": request['request']['body']
        }
        urls = [{
            "url": request['request']['url'],
            "type": self.util.get_response_types_num(
                request['config'].get('response_types', ['body'])),
            "unique_key": request['unique_key']
        }]
        headers = self.util.pop_dict_key(headers)
        configs = self.util.pop_dict_key(configs)
        urls[0] = self.util.pop_dict_key(urls[0])
        return headers, configs, urls

    def control_tasks(self):
        """
        控制sended_queue队列长度
        """
        if self.sending_queue.qsize() < self.sending_queue_max:
            return True
        else:
            return False

    def is_finish(self):
        """
        不再有完成一说，永远返回False
        """
        return False

    def start_requests(self):
        try:
            while True:
                if self.control_tasks():
                    condition = {"$or": [{'status': 0}, {'status': -1}]}  # 查询status为0或-1的数据
                    request_datas = self.store.read_request_datas(condition)
                    if request_datas is not None:
                        try:
                            print(request_datas['unique_key'])
                            headers, configs, urls = self.parameter_format(request_datas)
                            spider_request = SpiderRequest(headers=headers, urls=urls, config=configs)
                            self.sending_queue.put(spider_request)
                            self.store.update_status(request_datas['unique_key'], 1)  # 请求发送成功,则将mongo中原数据的status置为1
                        except:
                            if request_datas['status'] == 0:
                                # 请求发送失败,则将mongo中原数据的status置为-1
                                self.store.update_status(request_datas['unique_key'], -1)
                            else:
                                # 请求发送失败,则将mongo中原数据的status置为-2
                                self.store.update_status(request_datas['unique_key'], -2)
                            print("start_requests error, 1.")
                            traceback.print_exc()
                            time.sleep(1)
                    else:
                        time.sleep(self.sleep_time)
                else:
                    time.sleep(self.sleep_time)
        except:
            print("start_requests error, 2.")
            traceback.print_exc()

    def deal_response_results_status(self, task_status, url, result, request):
        """
        处理返回结果
        """
        if task_status == '2':
            print(url['unique_key'])
            r_html = ''
            r_capture = ''
            r_l = result["result"].split("||||")
            if len(r_l) == 1:  # 非截图
                r_html = r_l[0]
                r_capture = ""
            elif len(r_l) == 2:  # 截图
                r_capture = r_l[0]
                r_html = r_l[1]

            save_data = {
                "unique_key": url['unique_key'],
                "response": {
                    "ip": result['inter_pro'],
                    "header": result['header'],
                    "body": r_html,
                    "capture": r_capture
                }
            }
            self.store.store_data(save_data)
            # 返回结果保存成功之后将status置为2
            self.store.update_status(save_data['unique_key'], 2)


if __name__ == '__main__':
    spider = DCWrapper()
    spider.run(1, 1, 1, 1)
