# 一般系统中，将数据库中的时间统一使用UTC时间，然后在展示之类处理时，转成当地时区
import pytz
import time
import math
import datetime

loc_tz = pytz.timezone('Asia/Shanghai')
utc_tz = pytz.timezone('UTC')

def now_dt(tzinfo=loc_tz):
    # datetime.now(tz)
    # tz.localize(datetime.now())
    # tz.localize(datetime.fromtimestamp(time.time()))
    # 这里先取当前utc时间，然后加上UTC时区，之后转成当前时区
    return datetime.datetime.utcnow().replace(tzinfo=utc_tz).astimezone(loc_tz)


def str_2_datetime_by_format(dt_str, dt_format='%Y-%m-%d %H:%M:%S'):
    return loc_tz.localize(datetime.datetime.strptime(dt_str, dt_format))


def datetime_2_str_by_format(dt, dt_format='%Y-%m-%d %H:%M:%S'):
    return dt.astimezone(loc_tz).strftime(dt_format)

str2tsp = lambda s: int(time.mktime(time.strptime(s, "%Y-%m-%d %H:%M:%S")))
tsp2str = lambda s: time.strptime("%Y-%m-%d %H:%M:%S", time.localtime(s))
tsp2dt = lambda s: datetime.datetime.fromtimestamp(s)


# 获取当前时间是第几年的第几个月
def get_month_sequence_by_date(dt=None):
    """
    :params dt: 日期时间对象
    :return 第几年的第几个月(字符串表示)
    """
    if not dt:
        dt = datetime.datetime.now()
    year = str(dt.year)
    year_month = "%02d" % dt.month
    return year + year_month


def delta_day(delta=0):
    """
    :param delta:   偏移量
    :return:        0今天, 1昨天, 2前天, -1明天 ...
    """
    dt = (datetime.datetime.now() + datetime.timedelta(days=delta)).strftime('%Y-%m-%d')
    return dt


def delta_month(delta=0):
    """
    :param delta:  0本月, -1上月, 1下月, 下下个月...
    :return:    时间区间
    """

    def _delta_month(__year, __month, __delta):
        _month = __month + __delta
        if _month < 1:
            delta_year = math.ceil(abs(_month) / 12)
            delta_year = delta_year if delta_year else 1
            __year -= delta_year
            _month = delta_year * 12 + __month + __delta
        elif _month > 12:
            delta_year = math.floor(_month / 12)
            __year += delta_year
            _month %= 12
        return __year, _month

    now = datetime.datetime.now()
    _from = datetime.datetime(*_delta_month(now.year, now.month, delta), 1)

    _to = datetime.datetime(*_delta_month(_from.year, _from.month, 1), 1) - datetime.timedelta(days=1)
    return _from.strftime('%Y-%m-%d'), _to.strftime('%Y-%m-%d')


def delta_week(delta=0):
    """
    :param delta:   0本周, -1上周, 1下周 ...
    :return:        时间区间
    """
    now = datetime.datetime.now()
    week = now.weekday()
    _from = (now - datetime.timedelta(days=week - 7 * delta)).strftime('%Y-%m-%d')
    _to = (now + datetime.timedelta(days=6 - week + 7 * delta)).strftime('%Y-%m-%d')
    return _from, _to


last_week = lambda s=-1: delta_week(s)
next_week = lambda s=1: delta_week(s)
this_week = lambda s=0: delta_week(s)
last_month = lambda s=-1: delta_month(s)
next_month = lambda s=1: delta_month(s)
this_month = lambda s=0: delta_month(s)
