import datetime

import prettytable
import requests
from fake_useragent import FakeUserAgent
from station_name import station
import json


class TicketSpider(object):
    def __init__(self):
        ua = FakeUserAgent()
        self.station_name = station()
        self.from_station = input('请输入出发站: ')
        from_station = self.station_name[self.from_station]
        self.to_station = input('请输入到达站: ')
        to_station = self.station_name[self.to_station]
        self.date = input('请输入出发日期: ')
        self.url = 'https://kyfw.12306.cn/otn/leftTicket/queryZ?' \
                   'leftTicketDTO.train_date=%s&' \
                   'leftTicketDTO.from_station=%s&' \
                   'leftTicketDTO.to_station=%s&' \
                   'purpose_codes=ADULT' % (self.date, from_station, to_station)
        self.headers = {'user-agent': ua.chrome}

    def process_parse(self):
        session = requests.Session()
        url = 'https://kyfw.12306.cn/otn/leftTicket/init?linktypeid=dc&' \
              'fs=%E4%B8%8A%E6%B5%B7,SHH&' \
              'ts=%E5%A4%A9%E6%B4%A5,TJP&' \
              'date=2020-01-08&flag=N,N,Y'
        session.get(url, headers=self.headers)
        s = session.get(url=self.url, headers=self.headers)
        py_dict = json.loads(s.text)
        result_dict = dict()

        for i in py_dict['data']['result']:
            result_dict["车次"] = i.split('|')[3]
            result_dict["出发站"] = i.split('|')[4]
            result_dict["到达站"] = i.split('|')[5]
            result_dict["出发时间"] = i.split('|')[8]
            result_dict["到达时间"] = i.split('|')[9]
            result_dict["历时"] = i.split('|')[10]
            result_dict["是否有票"] = i.split('|')[11]
            result_dict["日期"] = i.split('|')[13]
            result_dict["一等座"] = i.split('|')[31]
            result_dict["二等座"] = i.split('|')[30]
            result_dict['出发站'] = self.get_key(self.station_name, result_dict['出发站'])
            result_dict['到达站'] = self.get_key(self.station_name, result_dict['到达站'])
            result_dict["是否有票"] = '有票' if result_dict["是否有票"] == 'Y' else '无票'
            yield result_dict

    def get_key(self, dict_obj, value):
        return ''.join([k for k, v in dict_obj.items() if v == value])

    def form(self, result_dict):
        # 创建表：
        tb = prettytable.PrettyTable()
        # 按行/列添加数据：
        tb.field_names = ['车次', '出发站', '到达站', '出发时间', '达到时间',
                          '历时', '是否有票', '日期', '一等座', '二等座']
        date = datetime.datetime.now()
        result_dict["日期"] = '%s-%s-%s' % (date.year, date.month, date.day)
        tb.add_row([result_dict["车次"], result_dict["出发站"],
                    result_dict["到达站"], result_dict["出发时间"],
                    result_dict["到达时间"], result_dict["历时"],
                    result_dict["是否有票"], result_dict["日期"],
                    result_dict["一等座"], result_dict["二等座"]])
        print(tb)

    def run(self):
        for result_dict in self.process_parse():
            self.form(result_dict)


if __name__ == '__main__':
    spider = TicketSpider()
    spider.run()
