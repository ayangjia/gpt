from flask import Flask,make_response
from flask import request
import xml.etree.ElementTree as ET
import hashlib
import requests
import json
import time
import re


REQUEST_ID_HEADER = 'x-fc-request-id'

app = Flask(__name__)
# openai的key
openaikey = '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'
# 微信公众号的appid
appid= "wx33c33825e95e29b3",
# 微信公众号的secret
secret= "989ac03d826d304523a0fcab534abf75"

@app.route('/robot', methods=['GET','POST'])

def wechat_tuling():
    if request.method == 'GET':
        print(request)
        my_signature = request.args.get(
            'signature', '')  # 获取携带 signature微信加密签名的参数
        my_timestamp = request.args.get('timestamp', '')  # 获取携带随机数timestamp的参
        my_nonce = request.args.get('nonce', '')   # 获取携带时间戳nonce的参数
        my_echostr = request.args.get('echostr', '')  # 获取携带随机字符串echostr的参数
        token = 'xytx'
        # 这里输入你要在微信公众号里面填的token，保持一致
        data = [token, my_timestamp, my_nonce]
        data.sort()
        # 进行字典排序
        temp = ''.join(data)
        # 拼接成字符串
        mysignature = hashlib.sha1(temp.encode('utf-8')).hexdigest()
        # # 判断请求来源，将三个参数字符串拼接成一个字符串进行sha1加密,记得转换为utf-8格式
        if my_signature == mysignature:
            # 开发者获得加密后的字符串可与signature对比，标识该请求来源于微信
            return make_response(my_echostr)
        else:
            return ''

    if request.method == 'POST':
        print(request)
        print(request.data)
        try:
            return ''
        finally:

            xml = ET.fromstring(request.data)
            print('XML',xml)
            # 获取用户发送的原始数据
            # fromstring()就是解析xml的函数，然后通过标签进行find()，即可得到标记内的内容。
            fromUser = xml.find('FromUserName').text
            toUser = xml.find('ToUserName').text
            msgType = xml.find("MsgType").text
            # 获取向服务器发送的消息
            createTime = xml.find("CreateTime")
            content = xml.find('Content').text
            print(content)
            xml_sta = '<xml><ToUserName><![CDATA[%s]]></ToUserName><FromUserName><![CDATA[%s]]></FromUserName><CreateTime>%s</CreateTime><MsgType><![CDATA[text]]></MsgType><Content><![CDATA[%s]]></Content></xml>'
            # 定义返回的xml数据结构，这里指的是文本消息，更多请参考微信公众号开发者文档
            print(xml_sta)
            if msgType == 'text':
                    # 判断消息类型，如果返回的字段是text，则是文字
                    print('接收到的text')
                    tuling_reply = reply(fromUser,content)
                    print('openai begin')
            # 调用api回复赋值给xml里面的content，这里定义为tuling_reply
                    res = make_response(xml_sta % (fromUser, toUser, str(int(time.time())), tuling_reply))
                    # 微信公众号做出响应，自动回复的格式如上
                    print(res)
                    res.content_type = 'application/xml'
                    # 定义回复的类型为xml
                    print('res',res)
                    return res
                    # 输出自动回复
            else:
                    # 如果输入非文字的则会提示下面这句话
                    return '我还只会文字，请等我慢慢成长，谢谢！'



    


def reply(user,info):
    print('进入接口')
    # 调用api
    api = 'https://api.openai.com/v1/completions'
    # 请求api接口的网址
    data = {
        "prompt": info, "max_tokens": 2048, "model": "text-davinci-003"
    }
    headers = {
        'content-type': 'application/json', 'Authorization': 'Bearer '+openaikey}
    # 请求的数据（这里只有对话的，可以添加url或者其他，有问题查看官方文档）
    print('合成数据',headers)
    jsondata = json.dumps(data)
    print('json化字典data',jsondata)
    # 根据官方文档，需要把利用json.dumps()方法把字典转化成json格式字符串
    try:

        response = requests.post(api, data=jsondata, headers=headers,timeout=None)
        print('开始请求')
    
        # 发起post请求
        robot_res = json.loads(response.content)
        print('返回结果',robot_res)
        # 把json格式的数据再转化成Python数据输出，注意编码为utf-8 格式
        robot_reply = robot_res['choices'][0]['text']
        print(robot_reply)
        postsend(user,robot_reply)

        return robot_reply
    except:
        return '服务接口缓慢请稍后重试'

def get_token():
        """
        获取微信的access_token
        :return:返回access_token
        """
        url = "https://api.weixin.qq.com/cgi-bin/token"

        params = {"grant_type": "client_credential",
                  "appid":appid,
                  "secret":secret}

        a =  requests.get(url=url, params=params).json().get("access_token")
        print('aaaaaaaaaaaaaa',a)
        return a 

def postsend(fromUser,cont):
    token=get_token()
    params = {
        "access_token": token
    }
    data = {
          "touser": fromUser,
            "msgtype": "text",
            "text": {
                 "content": cont
            }
    }
    print(data)
    kf = requests.post("https://api.weixin.qq.com/cgi-bin/message/custom/send", params=params,data=bytes(json.dumps(data, ensure_ascii=False), encoding='utf-8'),  headers = {"Content-type": "application/json", "charset": "UTF-8"})
    print(kf.text)
    return kf

if __name__ == '__main__':
        app.run(host='0.0.0.0',port=9000)
