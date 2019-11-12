# -*- coding: utf-8 -*-
from flask import Flask, request, escape, url_for, render_template, send_from_directory, make_response, jsonify
import app_interface
import mytool
import requests
from flask import current_app
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
import crawl_data


def create_token(api_user):
    s = Serializer(current_app.config["2131231231231"], expires_in=3600)
    token = s.dumps({"id": api_user}).decode("ascii")
    return token

app = Flask(__name__)
app.config["SECRET_KEY"] = "34kjja2hna32bajd12jkd"
url_gitlab="https://gitlab.com/api/v4"
tokendict={}

@mytool.robust
def getToken(id):
    if id in tokendict:
        return id,tokendict[id]
    else:
        return False

@app.route('/',methods=['GET','POST'])
def login():
    print("login")
    if request.method == 'POST':
        id=request.form["id"]
        id_token=getToken(id)
        print(id_token)
        token=request.form["Pwd"]
        brows = request.form.get("Pwd1",0)
        print(id,token,brows)
    else:
        return render_template("login.html")
    if brows==0:
        if id_token==False:
            if app_interface.get_data(id, token)==False:
                Dict = {"info": "id或者token错误"}
                response = make_response(render_template('login.html', **Dict))
                return response
    else:
        if app_interface.get_data_isexist(id):
            if app_interface.get_data(id, token)==False:
                Dict = {"info": "id或者token错误"}
                response = make_response(render_template('login.html', **Dict))
                return response
    Dict=app_interface.get_sql_data(id)
    Dict["id"]=id
    response = make_response(render_template('index1.html', **Dict))
    tokendict[id] = token
    return response

@app.route('/<id>',methods=['GET','POST'])
def login2(id):
    Dict = app_interface.get_sql_data(id)
    Dict["id"] = id
    response = make_response(render_template('index1.html', **Dict))
    return response



@app.route('/access/',methods=['GET','POST'])
def set_access():
    try:
        id,uid,pid,access=request.form.get("id",0),request.form.get("uid",0),request.form.get("pid",0),request.form.get("access",0)
        print(id,uid,pid,access)
        token=getToken(id)[1]
        if access=='0':
            url="https://gitlab.com/api/v4/projects/%s/members/%s"%(str(pid),str(uid))
            print(url)
            r = requests.delete(url, headers={"Private-Token": token})
            print(r.ok)
            print(r.text)
        else:
            url = 'https://gitlab.com/api/v4/projects/' + str(pid) + '/members/' + str(uid) + '?access_level='+str(access)
            print(url)
            r = requests.put(url, headers={"Private-Token": token})
            print(r.json())
            if "message" not in r.json():
                app_interface.changedata(id, uid, pid, access)
                return "1"
            if "Not found" in r.json().get('message',"1"):
                print(1)
                data={
                    "id":id,
                    'user_id':uid,
                    "access_level":access
                }
                headers = {"Private-Token": token}
                url='https://gitlab.com/api/v4/projects/%s/members'%(str(pid))
                r = requests.post(url,data=data, headers=headers)
            elif '403 Forbidden' in r.json().get('message',"1"):
                return "0"
        print("git_data")
        app_interface.changedata(id,uid,pid,access)
        return '1'
    except Exception as e:
        print(e)
        return "0"


@app.route('/users/<id>',methods=['GET','POST'])
def users(id):
    print("users")
    print(id)
    usersall=app_interface.get_users(id)
    Dict={
        "id":str(id),
        "allusers":usersall
    }
    Dict["label"]=["users","users"]
    response = make_response(render_template('ower.html', **Dict))
    return response

@app.route('/users/<id>/<uid>/<uname>',methods=['GET','POST'])
def user(id,uid,uname):
    Dict = app_interface.get_sql_data1(id,uid,uname)
    Dict["id"] = id
    response = make_response(render_template('index1.html', **Dict))
    return response



@app.route('/groups/<id>',methods=['GET','POST'])
def groups(id):
    groups=app_interface.get_sql_groups(id)
    Dict = {
        "id": str(id),
        "allusers": groups,
    }
    Dict["label"] = ["groups", "groups"]
    response = make_response(render_template('ower.html', **Dict))
    return response


@app.route('/groups/<id>/<gid>/<gname>',methods=['GET','POST'])
def group_page(id,gid,gname):
    print(id,gid,gname)
    token = getToken(id)[1]
    Dict=app_interface.get_sql_group(id,gid,token,gname)
    response = make_response(render_template('group.html', **Dict))
    return response


@app.route('/project/<id>/<pid>/<pname>',methods=['GET','POST'])
def project_page(id,pid,pname):
    print(pname)
    Dict = app_interface.get_project(id, pid)
    Dict["id"] = str(id)
    response = make_response(render_template('project.html', **Dict))
    return response

@app.route('/access/group/',methods=['GET','POST'])
def set_access_p():
    try:
        id,uid,gid,access=request.form.get("id",0),request.form.get("uid",0),request.form.get("gid",0),request.form.get("access",0)
        print(id,uid,gid,access)
        token = getToken(id)[1]
        if access=='0':
            url="https://gitlab.com/api/v4/groups/%s/members/%s"%(str(gid),str(uid))
            print(url)
            r = requests.delete(url, headers={"Private-Token": token})
            print(r.ok)
            print(r.text)
        else:
            url = 'https://gitlab.com/api/v4/groups/' + str(gid) + '/members/' + str(uid) + '?access_level='+str(access)
            print(url)
            r = requests.put(url, headers={"Private-Token": token})
            print(r.json())
            print(r.json().get('message',"1"))
            if "message" not in r.json():
                app_interface.changedata_g(id, uid, gid, access,token)
                return "1"
            if "Not found" in r.json().get('message',"1"):
                print(1)
                data={
                    "id":id,
                    'user_id':uid,
                    "access_level":access
                }
                headers = {"Private-Token": token}
                url='https://gitlab.com/api/v4/groups/%s/members'%(str(gid))
                print(url)
                print()
                r = requests.post(url,data=data, headers=headers)
                print(r.ok)
                print(r.text)
                print(r.json())
            elif '403 Forbidden' in r.json().get('message',"1"):
                return "0"
        print("git_data")
        app_interface.changedata_g(id,uid,gid,access,token)
        return '1'
    except Exception as e:
        print(e)
        return "0"

@app.route('/create/userProject/<id>',methods=['GET','POST'])
def create_user_project(id):
    Dict = {
        "id": str(id),
    }
    response = make_response(render_template('createusreproject.html', **Dict))
    return response

@app.route('/createGroupProject/',methods=['GET','POST'])
def createGroupProject():
    try:
        id, pname,gname, webu, description = request.form.get("id", 0), request.form.get("pname", 0),request.form.get("gname", 0), request.form.get("webu",0), request.form.get("description", 0)
        print(id, pname, webu, description)
        g_id=app_interface.get_data_groups(id, gname)
        if not(g_id):
            return "5"#gname错误，创建项目失败
        token = getToken(id)[1]
        url = "https://gitlab.com/api/v4/projects"
        data = {"name": pname, "description": description,"namespace_id":int(g_id)}
        r = crawl_data.post_data([url, token, data])
        if r.json().get("id", 0) == 0:
            return "0"
        app_interface.update_groupproject(id, r,g_id)

    except Exception as e:
        print(e)
        return "0"  # 创建项目失败
    if webu:
        try:
            id=r.json().get("id", 0)
            url = "https://gitlab.com/api/v4/projects/%s/hooks" %id
            data = {"url":webu, "push_events": True}
            r = crawl_data.post_data([url, token, data])
            if r.json().get("id", 0) == 0:
                return "2"
            return "3"# 创建项目成功，加入hookweb成功
        except Exception as e:
            print(e)
            return "2"  # 创建项目成功，加入hookweb失败

    else:
        return "1"  # 创建项目成功

@app.route('/createUserProject/',methods=['GET','POST'])
def createUserProject():
    try:
        id, pname, webu,description= request.form.get("id", 0), request.form.get("pname", 0), request.form.get("webu",0), request.form.get("description",0)
        print(id, pname, webu,description)
        token = getToken(id)[1]
        url="https://gitlab.com/api/v4/projects"
        data={"name":pname,"description":description}
        r=crawl_data.post_data([url,token,data])
        if r.json().get("id",0)==0:
            return "0"
        app_interface.update_userproject(id, r)
    except Exception as e:
        print(e)
        return "0"#创建项目失败

    if webu:
        try:
            id = r.json().get("id", 0)
            url = "https://gitlab.com/api/v4/projects/%s/hooks" % id
            data = {"url": webu, "push_events": True}
            r = crawl_data.post_data([url, token, data])
            if r.json().get("id", 0) == 0:
                return "2"
            return "3"  # 创建项目成功，加入hookweb成功
        except Exception as e:
            print(e)
            return "2"#创建项目成功，加入hookweb失败

    else:
        return "1"#创建项目成功

@app.route('/create/groupProject/<id>',methods=['GET','POST'])
def create_group_project(id):
    Dict = {
        "id": str(id),
    }
    response = make_response(render_template('creategroupproject.html', **Dict))
    return response
def main():
    app.run()

if __name__ == '__main__':
    app.run()
