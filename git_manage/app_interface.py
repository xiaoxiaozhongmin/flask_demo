# -*- coding: utf-8 -*-
import requests

import mytool
import crawl_data
import data_storage
import time
import threading

@mytool.decorate
def get_groups(id,token):
    '''创建2个线程爬取groups和users项目'''
    urls=["https://gitlab.com/api/v4/groups",'https://gitlab.com/api/v4/users/'+str(id)+'/projects']
    tokens=[token,token]
    return mytool.threadPool_map(crawl_data.get_data,args=zip(urls, tokens),workers=2)

def get_data_isexist(id):
    connsql = data_storage.mysqlcls("gitlab" + str(id))
    sql = "select u_id, u_name from USERS"
    users = connsql.execute_sql(sql)
    sql = "select id,p_id, p_name,url,user_project from projects"
    projects = connsql.execute_sql(sql)
    sql = "select P_ID,U_ID,access from accesses"
    accesses = connsql.execute_sql(sql)
    if users and projects and accesses:
        return False
    return True
def get_data_groups(id,gname):
    connsql = data_storage.mysqlcls("gitlab" + str(id))
    sql = "select g_id from groups where g_name='%s'"%gname.strip()
    g_name = connsql.execute_sql(sql)
    if g_name:
        return g_name[0][0]
    return False

@mytool.decorate
def get_sql_data(id):
    '''获取sqllite的全部数据'''
    connsql = data_storage.mysqlcls("gitlab" + str(id))
    sql="select u_id, u_name from USERS"
    users=connsql.execute_sql(sql)
    sql = "select id,p_id, p_name,url,user_project from projects"
    projects = connsql.execute_sql(sql)
    sql = "select P_ID,U_ID,access from accesses"
    accesses = connsql.execute_sql(sql)
    accesses1={}
    for access in accesses:
        if access[0] not in accesses1:
            accesses1[access[0]]={}
        accesses1[access[0]][access[1]]=access[2]
    for p in accesses1:
        for u in users:
            if u[0] not in accesses1[p]:
                accesses1[p][u[0]]='0'

    accessdict={
        "0":'Undefined',
        "10": 'Guest',
        "20": 'Reporter',
        "30": 'Developer',
        "40": 'Master',
        "50": 'Owner',
    }
    return {
            'users':users,
            'projects':projects,
            'accesses':accesses1,
            "accessdict":accessdict
            }

def get_sql_data1(id,uid,uname):
    '''获取用户数据'''
    print(id,uid,uname)
    d=get_sql_data(id)
    def access_sort(x):
        print(x)
        return d['accesses'][x[1]][int(uid)]
    d['users']=[(int(uid),uname)]
    d['projects'].sort(key=access_sort,reverse=True)
    return d
def update_userproject(id,r):
    connsql = data_storage.mysqlcls("gitlab" + str(id))
    p=r.json()
    sql = "INSERT INTO projects (p_id, p_name,url,user_project) select '%s', '%s','%s','%s' WHERE NOT EXISTS (select 1 from projects where p_id='%s')" % (p["id"], p["name"], p["web_url"], 0, p["id"])
    connsql.execute_sql(sql)
    sql = "INSERT INTO accesses (P_ID,U_ID,access) select '%s', '%s','%s' WHERE NOT EXISTS (select 1 from accesses where P_ID='%s' and U_ID='%s')" % (p["id"], str(id), "40",p["id"], str(id))
    connsql.execute_sql(sql)




@mytool.decorate
def handle_data(userprojects1, userProjectAccess,groupsProjects, gp_access,dataname,p_g):
    '''上传数据'''
    connsql = data_storage.mysqlcls(dataname)
    t_start=time.time()
    accesses=userProjectAccess+gp_access
    projects=userprojects1+groupsProjects
    i=0
    for access in accesses:
        for used in access:
            sql="INSERT INTO USERS (u_id, u_name) select '%s', '%s' WHERE NOT EXISTS (select 1 from users where u_id='%s')"%(used["id"],used["username"],used["id"])
            connsql.execute_sql(sql)
            sql = "INSERT INTO accesses (P_ID,U_ID,access) select '%s', '%s','%s' WHERE NOT EXISTS (select 1 from accesses where P_ID='%s' and U_ID='%s')" % (projects[i]["id"],used["id"], used["access_level"],projects[i]["id"], used["id"])
            connsql.execute_sql(sql)
        i=i+1
    print("access fiash")
    for p in userprojects1:
        sql = "INSERT INTO projects (p_id, p_name,url,user_project) select '%s', '%s','%s','%s' WHERE NOT EXISTS (select 1 from projects where p_id='%s')" % (
        p["id"], p["name"], p["web_url"],0,p["id"])
        connsql.execute_sql(sql)
    for p in groupsProjects:
        sql = "INSERT INTO projects (p_id, p_name,url,user_project) select '%s', '%s','%s','%s' WHERE NOT EXISTS (select 1 from projects where p_id='%s')" % (
            p["id"], p["name"], p["web_url"],p_g[p["id"]],p["id"])
        connsql.execute_sql(sql)
        sql = "INSERT INTO groupsproject (p_id, g_id) select '%s', '%s' WHERE NOT EXISTS (select 1 from groupsproject where p_id='%s' and g_id='%s')" % (
            p["id"], p_g[p["id"]],p["id"], p_g[p["id"]])
        connsql.execute_sql(sql)
    print("handle_data用时"+str(time.time()-t_start))

def updatagroups(id,groups):
    connsql = data_storage.mysqlcls("gitlab"+str(id))
    for g in groups:
        sql = "INSERT INTO groups (g_id, g_name) select '%s', '%s' WHERE NOT EXISTS (select 1 from groups where g_id='%s')" % (
        g["id"], g["name"], g["id"])
        connsql.execute_sql(sql)

@mytool.robust
def get_data(id,token):
    '''获取git数据，使用线程池，并将数据上传sqllite'''
    t_start = time.time()
    connsql=data_storage.mysqlcls("gitlab"+str(id))
    groups_userproject=list(get_groups(id,token))
    groups=[xx['id'] for xx in groups_userproject[0]]
    updatagroups(id,groups_userproject[0])
    userprojects1=groups_userproject[1]
    userprojects=[id['id'] for id in groups_userproject[1]]
    groups_userprojects_url=["https://gitlab.com/api/v4/groups/" + str(i)+'/projects?per_page=100&page=1' for i in groups] + ['https://gitlab.com/api/v4/projects/%s/members/all' % str(id) for id in userprojects]
    tokens=[token for i in range(len(groups_userprojects_url))]
    groupsProject_userProjectAccess=list(mytool.threadPool_map(crawl_data.get_data,args=zip(groups_userprojects_url, tokens),workers=len(tokens)))
    print(time.time()-t_start)
    groupsProjects=groupsProject_userProjectAccess[:len(groups)]
    userProjectAccess=groupsProject_userProjectAccess[len(groups):]
    groupsProjects_id=[]
    h=[[x['id'] for x in p] for p in groupsProjects]
    h1 = [ p for p in groupsProjects]
    for a1 in h:
        for a2 in a1:
            groupsProjects_id.append(a2)
    groupsProjects1=[]
    p_g={}
    a = 0
    for a1 in h1:
        for a2 in a1:
            p_g[a2["id"]]=groups[a]
            groupsProjects1.append(a2)
        a=a+1
    print(p_g)
    gpurl=['https://gitlab.com/api/v4/projects/%s/members/all' % str(id) for id in groupsProjects_id]
    tokens=[token for i in range(len(gpurl))]
    gp_access=list(mytool.threadPool_map(crawl_data.get_data,args=zip(gpurl, tokens),workers=len(tokens)))
    print(time.time()-t_start)
    handle_data(userprojects1, userProjectAccess,groupsProjects1, gp_access,"gitlab"+str(id),p_g)
    return True

@mytool.robust
def changedata(id,uid,pid,access):
    """改变权限后，更新数据库"""
    connsql = data_storage.mysqlcls("gitlab" + str(id))
    sql="update accesses set access='%s' where u_id='%s' and p_id='%s'"%(access,uid,pid)
    connsql.execute_sql(sql)
    return True

@mytool.robust
def get_users(id):
    """获取所有用户信息"""
    print("get_user")
    userall=[]
    connsql = data_storage.mysqlcls("gitlab" + str(id))
    sql = "select u_id, u_name from USERS"
    users = connsql.execute_sql(sql)
    for i in range(0, len(users), 5):
        userall.append(users[i:i + 5])
    return userall

@mytool.robust
def get_sql_groups(id):
    print("get_user")
    groupall=[]
    connsql = data_storage.mysqlcls("gitlab" + str(id))
    sql = "select g_id, g_name from groups"
    groups = connsql.execute_sql(sql)
    for i in range(0, len(groups), 5):
        groupall.append(groups[i:i + 5])
    return groupall

def get_project(id,pid):
    connsql = data_storage.mysqlcls("gitlab" + str(id))
    sql = "select id, p_id, p_name,url,user_project from projects where p_id='%s'"%pid
    project = connsql.execute_sql(sql)
    print(project)
    data_git=get_sql_data(id)
    usersall=[]

    def sort_key(x):
        return data_git["accesses"][int(pid)][int(x[0])]
    data_git['users'].sort(key=sort_key,reverse=True)
    for i in range(0, len(data_git['users']), 5):
        usersall.append(data_git['users'][i:i + 5])
    return {
        "project":project[0],
        'usersall':usersall,
        'accesses':  data_git['accesses'],
        "accessdict": data_git['accessdict']
    }

def get_sql_group(id,gid,token,gname):
    connsql = data_storage.mysqlcls("gitlab" + str(id))
    url = "https://gitlab.com/api/v4/groups/%s/members/all" % gid
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0',
        "Private-Token": token
    }
    r = requests.get(url, headers=headers, timeout=20)
    user_groups=list(r.json())
    data_git = get_sql_data(id)
    access_id=[i['id'] for i in r.json()]
    groupaccess="0"
    for u in data_git['users']:
        d={}
        if u[0] not in access_id:
            d["id"]=u[0]
            d["username"]=u[1]
            d['access_level']='0'
            user_groups.append(d)
    for i in r.json():
        if int(i["id"])==int(id):
            groupaccess=i['access_level']
    print(groupaccess)
    groupsall=[]
    for i in range(0, len(user_groups), 5):
        groupsall.append(user_groups[i:i + 5])
    return {
        "usersall":groupsall,
        "groupid":gid,
        "id":id,
        "groupname":gname,
        "accessdict": data_git['accessdict'],
        "groupaccess":groupaccess
    }

def changedata_g(id,uid,gid,access,token):
    connsql = data_storage.mysqlcls("gitlab" + str(id))
    data_git = get_sql_data(id)
    sql = "select p_id from groupsproject where g_id='%s'"%gid
    p = connsql.execute_sql(sql)
    sql = "select p_id, user_project from projects where p_id in (select p_id from groupsproject where g_id='%s') and user_project=0"%gid
    p1 = connsql.execute_sql(sql)
    print(p1)
    u_d=[i[0] for i in p1]
    gp=[i[0] for i in p]
    print(p)
    for p_id in gp:
        if p_id not in u_d or int(access)>data_git['accesses'][int(p_id)][int(uid)]:
            sql="update accesses set access='%s' where u_id='%s' and p_id='%s'" % (access, uid, p_id)
            connsql.execute_sql(sql)
    url =  ['https://gitlab.com/api/v4/projects/%s/members/all' % str(id) for id in gp]
    tokens = [token for i in range(len(gp))]
    def p_update(url_token,pid):
        r = crawl_data.get_data(url_token)
        print(r)
        a="0"
        for access in r:
            if int(uid)==int(access['id']):
                a=access["access_level"]
                break
        sql = "update accesses set access='%s' where u_id='%s' and p_id='%s'" % (a, uid, pid)
        connsql.execute_sql(sql)
    for i in range(len(gp)):
        t=threading.Thread(target=p_update,args=((url[i],tokens[i]),gp[i]))
        t.start()



def update_groupproject(id, r,g_id,token):
    connsql = data_storage.mysqlcls("gitlab" + str(id))
    p = r.json()
    sql = "INSERT INTO projects (p_id, p_name,url,user_project) select '%s', '%s','%s','%s' WHERE NOT EXISTS (select 1 from projects where p_id='%s')" % (p["id"], p["name"], p["web_url"], g_id, p["id"])
    connsql.execute_sql(sql)
    url="https://gitlab.com/api/v4/projects/%s/members/all"%p['id']
    access=crawl_data.get_data([url,token])
    for used in access:
        sql = "INSERT INTO accesses (P_ID,U_ID,access) select '%s', '%s','%s' WHERE NOT EXISTS (select 1 from accesses where P_ID='%s' and U_ID='%s')" % (
            p["id"], used["id"], used["access_level"], p["id"], used["id"])
        connsql.execute_sql(sql)




