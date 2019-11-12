# -*- coding: utf-8 -*-
import requests

def get_data(url_token):
    print(url_token[0],"start crawl_data")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:70.0) Gecko/20100101 Firefox/70.0',
        "Private-Token": url_token[1]
    }
    r = requests.get(url_token[0], headers=headers, timeout=180)
    r.close()
    print(url_token[0],"success")
    return r.json()

def post_data(url_token):
    print(url_token[0],"start crawl_data")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:70.0) Gecko/20100101 Firefox/70.0',
        "Private-Token": url_token[1]
    }
    r = requests.post(url_token[0], headers=headers, timeout=180,data=url_token[2])
    print(r.json())
    r.close()
    print(url_token[0],"success")
    return r.json()


# url="https://gitlab.com/api/v4/projects"
# token="EqrQg4UPeXCX-sR6Xxnb"
# data={"name":"nginx","namespace_id":6277639}
# post_data([url,token,data])
#push_events
# POST /projects/:id/hooks'
# url="https://gitlab.com/api/v4/projects/%s/hooks"%'15296946'
# token="EqrQg4UPeXCX-sR6Xxnb"
# data={"url":"http://129.204.120.65:9898/mac/test","push_events":True}
# post_data([url,token,data])