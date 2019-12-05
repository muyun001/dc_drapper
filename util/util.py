# -*- coding: utf-8 -*-


class Util(object):
    """
    工具类
    """

    def __init__(self):
        pass

    def get_priority_num(self, level):
        """
        由文字优先级, 返回其对应的序号:
        1（最不优先）2（默认）3（最优先）
        """
        prioritys = {u'low': 1, u'normal': 2, u'high': 3}
        return prioritys[level]

    def get_city_num(self, city):
        """
        由城市名, 返回其对应的序号:
        1 北京,2 上海,3 苏州,4 深圳,5 江门
        """
        citys = {u'北京': 1, u'上海': 2, u'苏州': 3, u'深圳': 4, u'江门': 5}
        return citys.get(city, '')

    def get_redirect_num(self, flag):
        """
         由"是否跳转"的true或false,返回其对应的序号
        """
        if flag:
            return 1
        elif not flag:
            return 0

        # 避免flag写成字符串格式而出错
        redirect = {'false': 0, 'False': 0, 'true': 1, 'True': 1}
        return redirect[flag]

    def get_response_types_num(self, type):
        """
        由返回值类型,返回其对应的序号
        1(返回html， 默认)， 2(返回html和header) 4 截图(若结果含有"||||", 则返回值含有html和截图,否则只含有html)
        response_types = ["header", "body", "capture"]
        """
        if len(type) == 1 and 'body' in type:
            return 1
        elif len(type) == 2 and 'body' in type and 'capture' in type:
            return 4
        elif len(type) == 2 and 'body' in type and 'header' in type:
            return 2
        else:
            raise Exception("error, download center can not support the type.")

    def pop_dict_key(self, dictname):
        """
        移除dict中值为空的key
        """
        for key in list(dictname.keys()):
            if dictname[key] == "":
                dictname.pop(key)
        return dictname


if __name__ == '__main__':
    util = Util()
    # redirect_num = util.get_redirect_num('false')
    # print redirect_num
    # priority = util.get_priority_num('normal')
    # print priority
    # city_num = util.get_city_num(u'其他')
    # print city_num
    # response_types = ["header", "body", "capture"]
    # type_num = util.get_response_types_num(['capture'])
    # print type_num
    citys = {u'北京': 1, u'上海': 2, u'苏州': 3, u'深圳': 4, u'江门': 5}
    util.pop_dict_key(citys)