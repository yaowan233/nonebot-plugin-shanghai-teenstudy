import json
import os
import time
import asyncio
from httpx import AsyncClient
from nonebot import get_bot
from nonebot.adapters.onebot.v11 import MessageSegment
from .get_src import get_pic


path = os.path.dirname(__file__) + '/data'


async def auto_sh(send_id):
    with open(path + '/dxx_list.json', 'r', encoding='utf-8') as f:
        obj = json.load(f)
    headers = {
        "Host": "qcsh.h5yunban.com",
        "Connection": "keep-alive",
        "Accept": "text/javascript, application/javascript, application/ecmascript, application/x-ecmascript, */*; q=0.01",
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; PACM00 Build/QP1A.190711.020; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/86.0.4240.99 XWEB/3164 MMWEBSDK/20211001 Mobile Safari/537.36 MMWEBID/556 MicroMessenger/8.0.16.2040(0x28001056) Process/toolsmp WeChat/arm32 Weixin NetType/WIFI Language/zh_CN ABI/arm64",
        "X-Requested-With": "XMLHttpRequest",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
    }
    for item in obj:
        if int(send_id) != int(item['qq']):
            continue
        openid = item['openid']
        name = item['name']
        nid = item['nid']
        area = item['area']
        danwei1 = item['danwei1']
        danwei2 = item['danwei2']
        danwei3 = item['danwei3']
        time_stamp = str(int(time.time()))
        access_token_url = "https://qcsh.h5yunban.com/youth-learning/cgi-bin/login/we-chat/callback?callback=https%3A%2F%2Fqcsh.h5yunban.com%2Fyouth-learning%2Findex.php&scope=snsapi_userinfo&appid=wxa693f4127cc93fad&openid=" + openid + "&nickname=ZhangSan&headimg=&time=" + time_stamp + "&source=common&sign=&t=" + time_stamp
        async with AsyncClient(headers=headers) as client:
            access_token_rsp = await client.get(access_token_url)
        access_token = access_token_rsp.text[45:81]
        course_url = "https://qcsh.h5yunban.com/youth-learning/cgi-bin/common-api/course/current?accessToken=" + access_token
        async with AsyncClient(headers=headers) as client:
            course_rsp = await client.get(course_url)
        res_json = json.loads(course_rsp.text)
        title = res_json['result']['title']
        course_id = res_json['result']['id']
        data = {
            "course": course_id,
            "subOrg": None,
            "nid": nid,
            "cardNo": name
        }
        sent_url = "https://qcsh.h5yunban.com/youth-learning/cgi-bin/user-api/course/join?accessToken=" + access_token
        async with AsyncClient(headers=headers) as client:
            sent_rsp = await client.post(url=sent_url, data=json.dumps(data))
        resp = json.loads(sent_rsp.text)
        status = resp.get("status")

        try:
            bot = get_bot()
        except ValueError:
            break
        if status != 200:
            message = '提交失败！'
            await bot.send_private_msg(user_id=send_id, message=message, at_sender=True)

        img = await get_pic()
        end = img['end']

        message = f'大学习{title}提交成功!\n用户信息\n姓名：{name}\nQQ号:{send_id}\n地区：{area}\nopenid:{openid}\n' \
                  f'学校：{danwei1}\n学院：{danwei2}\n班级(团支部)：{danwei3}'
        await bot.send_private_msg(user_id=send_id, message=message, at_sender=True)
        await asyncio.sleep(1)
        c = "你也可以点击链接进行截图以获取带手机状态栏的完成截图\nhttps://qndxx.scubot.live/\n如果QQ不能直接打开请复制到微信打开！"
        message = MessageSegment.text('完成截图\n') + MessageSegment.image(end) + MessageSegment.text(c)
        await bot.send_private_msg(user_id=send_id, message=message, at_sender=True)
