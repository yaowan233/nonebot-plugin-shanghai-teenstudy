import asyncio
import json
import os
from nonebot import get_driver
from nonebot.permission import SUPERUSER
from nonebot.plugin import on_command
from nonebot.adapters.onebot.v11 import MessageSegment, PrivateMessageEvent, Message
from nonebot.params import CommandArg
from .dxx_sh import auto_sh
from .get_src import get_pic
from .config import Config


global_config = get_driver().config
plugin_config: Config = Config.parse_obj(global_config.dict())
openid = plugin_config.openid
if not openid:
    raise ValueError('请设置openid！')
super_id = global_config.superusers  # 超管id
path = os.path.dirname(__file__) + '/data'  # 数据存放目录

# 大学习功能，用于提交大学习，全员可用
dxx = on_command('提交大学习', aliases={'sub_dxx'}, priority=5)


@dxx.handle()
async def _(event: PrivateMessageEvent):
    send_id = event.get_user_id()
    with open(path + '/dxx_list.json', 'r', encoding='utf-8') as f:
        obj = json.load(f)
    for item in obj:
        if int(send_id) == int(item['qq']):
            content = await auto_sh(send_id)
            status = content['status']
            if status != 200:
                message = '提交失败！'
                await dxx.finish(message=message, at_sender=True)

            img = await get_pic()
            end = img['end']
            area = item['area']
            name = item['name']
            danwei1 = item['danwei1']
            danwei2 = item['danwei2']
            danwei3 = item['danwei3']
            title = content['title']
            message = f'大学习{title}提交成功!\n用户信息\n姓名：{name}\nQQ号:{send_id}\n地区：{area}\nopenid:{openid}\n' \
                      f'学校：{danwei1}\n学院：{danwei2}\n班级(团支部)：{danwei3}'
            await dxx.send(message, at_sender=True)
            await asyncio.sleep(1)
            c = "你也可以点击链接进行截图以获取带手机状态栏的完成截图\nhttps://qndxx.scubot.live/\n如果QQ不能直接打开请复制到微信打开！"
            await dxx.finish(MessageSegment.text('完成截图\n') + MessageSegment.image(end) + MessageSegment.text(c),
                             at_sender=True)
    message = '用户数据不存在，请先配置用户文件！'
    await dxx.finish(message, at_sender=True)


# 大学习功能，用于设置大学习配置，全员可用
set_dxx = on_command('设置大学习', aliases={'set_dxx'}, priority=5)


@set_dxx.handle()
async def _(event: PrivateMessageEvent, msg: Message = CommandArg()):
    send_id = event.get_user_id()
    with open(path + '/dxx_list.json', 'r', encoding='utf-8') as f:
        obj = json.load(f)
    for item in obj:
        if int(send_id) == int(item['qq']):
            message = '用户数据存在'
            await set_dxx.finish(message, at_sender=True)
    area = '上海'
    qq = int(send_id)
    uid, title = '', ''
    args = msg.extract_plain_text().strip()
    if len(args.split()) != 4:
        message = f'设置失败！您指令输入有误！\n正确指令格式：设置大学习 姓名 学校名称 团委名称 班级\nps:名称一定要输入正确'
        await set_dxx.finish(message, at_sender=True)
    name, danwei1, danwei2, danwei3 = args.split()
    with open(path + '/dxx_sh.json', 'r', encoding='utf-8') as f:
        n = json.load(f)
    nid = None
    for item1 in n:
        if item1['school'] == danwei1 and item1['college'] == danwei2 and item1['class'] == danwei3:
            nid = item1['id3']
    if not nid:
        message = '地区设置有误'
        await set_dxx.finish(message, at_sender=True)
    data = {'qq': qq, 'area': area, 'openid': openid, 'uid': uid, 'name': name, 'danwei1': danwei1,
            'danwei2': danwei2, 'danwei3': danwei3, 'nid': nid, 'title': title}
    obj.append(data)
    with open(path + '/dxx_list.json', 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=4)
    message = f'大学习用户信息设置成功!\n用户信息\n姓名：{name}\nQQ号:{send_id}\n地区：{area}\nopenid:{openid}\n' \
              f'学校：{danwei1}\n学院：{danwei2}\n班级(团支部)：{danwei3}'
    await set_dxx.finish(message, at_sender=True)


delete_dxx = on_command('删除大学习')


@delete_dxx.handle()
async def _(event: PrivateMessageEvent):
    send_id = event.get_user_id()
    delete_id = int(send_id)
    with open(path + '/dxx_list.json', 'r', encoding='utf-8') as f:
        obj = json.load(f)
    for item in obj:
        if delete_id == int(item['qq']):
            name = item['name']
            list1 = item
            obj.remove(list1)
            with open(path + '/dxx_list.json', 'w', encoding='utf-8') as f:
                json.dump(obj, f, ensure_ascii=False, indent=4)
            message = f'已将用户：{name}信息删除！'
            await delete_dxx.finish(message=message, at_sender=True)
    message = f'失败！\n用户QQ:{delete_id}不在大学习信息配置表中。'
    await delete_dxx.finish(message=message, at_sender=True)


check_dxx_list = on_command('查看大学习列表', aliases={'check_dxx_list'}, permission=SUPERUSER)


@check_dxx_list.handle()
async def _():
    message = '序号<-->QQ号<-->地区<-->姓名<-->团支部(班级)\n'
    with open(path + '/dxx_list.json', 'r', encoding='utf-8') as f:
        obj = json.load(f)
    num = 1
    for item in obj:
        qq = item['qq']
        area = item['area']
        name = item['name']
        danwei3 = item['danwei3']
        message += f'{num}<-->{qq}<-->{area}<-->{name}<-->{danwei3}\n'
        num += 1
    await check_dxx_list.finish(message)


dxx_help = on_command('大学习帮助', priority=5)


@dxx_help.handle()
async def _():
    message = '1、提交大学习\n2、大学习帮助\n3、设置大学习\n指令格式：设置大学习 姓名 学校 团委(学院) 团支部(班级)\n4、删除大学习'
    await dxx_help.finish(message)
