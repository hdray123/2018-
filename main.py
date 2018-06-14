# -*- coding:utf-8 -*-
import sys
import socket
import json
from Plane_move import planes_move,Delivery_elect,find_plane,find_plane_list
import time
#从服务器接收一段字符串, 转化成字典的形式
def RecvJuderData(hSocket):
    nRet = -1
    Message = hSocket.recv(1024 * 1024 * 4)
    len_json = int(Message[:8])
    str_json = Message[8:].decode()
    while len(str_json) != len_json:
        Message = hSocket.recv(1024 * 1024 * 4)
        str_json = str_json + Message.decode()
    nRet = 0
    Dict = json.loads(str_json)
    print(Dict)
    return nRet, Dict

#根据货物编号寻找货物
def find_good(no,goods):
    for good in goods:
        if good["no"]==no:
            return good
    return -1

# 接收一个字典,将其转换成json文件,并计算大小,发送至服务器
def SendJuderData(hSocket, dict_send):
    str_json = json.dumps(dict_send)
    len_json = str(len(str_json)).zfill(8)
    str_all = len_json + str_json
    print(str_all)
    ret = hSocket.sendall(str_all.encode())
    if ret == None:
        ret = 0
    print('sendall', ret)
    return ret

#清理track_dict
def check_track_dict(track_dict,UAV_we,UAV_enemy,goods):
    track_dict_T={}
    we_no=[]
    enemy_no=[]
    for plane in UAV_we:
        if plane["status"]!=1:
            we_no.append(plane["no"])
    good_end_position=[]
    for plane in UAV_enemy:
        if plane["status"]!=1:
            enemy_no.append(plane["no"])
            if plane["goods_no"]==-1:
                pass
            else:
                good=find_good(plane["goods_no"],goods)
                good_end_position.append([good["end_x"],good["end_y"]])

    for k,v in track_dict.items():
        if k in we_no:
            if type(v)==int:
                if v in enemy_no:
                    track_dict_T[k]=v
            else:
                if v in good_end_position:
                    track_dict_T[k]=v
    return track_dict_T
#清理good_plane
def check_plane_good(plane_good,goods,UAV_we,UAV_price,time,we_value):
    we_no = []
    plane_good_T={}
    for plane in UAV_we:
        if plane["status"]!=1 and plane["goods_no"]==-1:
            we_no.append(plane["no"])
    for k,v in plane_good.items():
        if k in we_no:
            plane = find_plane(k, UAV_we)
            type_list=find_plane_list(UAV_price,plane["type"])
            #如果飞机在停车场 先充满电再出来
            if plane["x"]==park_x and plane["y"]==park_y and plane["z"]==0 and plane["remain_electricity"]!= type_list["capacity"]:
                pass
            else:

                #如果是追踪目标货物
                need_electricity=Delivery_elect(goods,h_low,plane,time,we_value)
                for k_T, v_T in plane_good_T.items():
                    if v_T in need_electricity.items():
                        need_electricity.pop(v_T)
                number_good = -1
                max_value = -1
                for k_T, v_T in need_electricity.items():
                    if max_value < v_T:
                        max_value = v_T
                        number_good = k_T
                good=find_good(v,goods)


                if good!=-1 and good["status"]==1 and plane["x"]==good["start_x"] and plane["y"]==good["start_y"] and plane["z"]>1:
                    plane_good_T[k]=v
                if number_good==v:
                    plane_good_T[k]=v

    return plane_good_T



#购买飞机算法
def Buy_Plane(UAV_we,UAV_enemy,we_value,UAV_price,goods):

    list=[]
    dict={}
    min_value = 999999
    type = 0
    min_weight=99999999
    for kind in UAV_price:
        if kind["value"] < min_value:
            type = kind["type"]
            min_value = kind["value"]
            min_weight=kind["load_weight"]

    dict["purchase"]=type
    while we_value>min_value:
        list.append(dict)
        we_value-= min_value
    return list

#用户自定义函数, 返回字典FlyPlane, 需要包括 "UAV_info", "purchase_UAV" 两个key.
#track_dict 是我方飞机追踪的敌方飞机。
def AlgorithmCalculationFun(pstMapInfo, pstMatchStatus, pstFlayPlane,build_positions,enemy_park,track_dict,plane_good,enemy_position):
    FlyPlane = {}
    FlyPlane["purchase_UAV"] = []
    if (pstMatchStatus["time"] <= 0):
        FlyPlane["UAV_info"] = pstFlayPlane["astUav"]
        return FlyPlane,track_dict,plane_good,enemy_position
    global h_low,h_high ,map_x,map_y,map_z,park_x,park_y,UAV_price

    map_x = pstMapInfo["map"]["x"]
    map_y = pstMapInfo["map"]["y"]
    map_z = pstMapInfo["map"]["z"]
    h_low = pstMapInfo["h_low"]
    h_high = pstMapInfo["h_high"]
    park_x = pstMapInfo["parking"]["x"]
    park_y = pstMapInfo["parking"]["y"]
    UAV_price = pstMapInfo["UAV_price"]



    # 我方飞机状态
    UAV_we = pstMatchStatus["UAV_we"]
    # 敌方飞机状态
    UAV_enemy = pstMatchStatus["UAV_enemy"]
    # 货物信息
    goods = pstMatchStatus["goods"]
    # 我方含有价值
    we_value = pstMatchStatus["we_value"]
    # 敌方含有价值
    enemy_value = pstMatchStatus["enemy_value"]
    time = pstMatchStatus["time"]
    map=[map_x,map_y,map_z]


    #购买算法
    FlyPlane["purchase_UAV"] = Buy_Plane(UAV_we,UAV_enemy,we_value,UAV_price,goods)
    #清理track_dict
    track_dict=check_track_dict(track_dict,UAV_we,UAV_enemy,goods)
    #清理plane_good
    plane_good=check_plane_good(plane_good,goods,UAV_we,UAV_price,time,we_value)

    FlyPlane["UAV_info"],track_dict,plane_good,enemy_position=\
        planes_move(build_positions=build_positions,enemy_UAVs=UAV_enemy,goods=goods,we_UAVs=UAV_we,track_dict=track_dict,plane_good=plane_good,price_dict=UAV_price,h_low=h_low,h_high=h_high,map=map,park_we=[park_x,park_y],park_enemy=enemy_park,Enemy_position=enemy_position,time=time,we_value=we_value)

    return  FlyPlane,track_dict,plane_good,enemy_position


#障碍物位置
def Build_position(build,h_low,h_high):
    position = []
    for i in range(len(build)):
        if (build[i]["h"] > h_low):
            for z in range(h_low, min(build[i]["h"],h_high+1)):
                for y in range(build[i]["y"], (build[i]["y"] + build[i]["w"])):
                    for x in range(build[i]["x"], (build[i]["x"] + build[i]["l"])):
                        position.append([x, y, z])
    return position

def main(szIp, nPort, szToken):
    print("server ip %s, prot %d, token %s\n", szIp, nPort, szToken)

    #Need Test // 开始连接服务器
    hSocket = socket.socket()

    hSocket.connect((szIp, nPort))

    #接受数据  连接成功后，Judger会返回一条消息：
    nRet, _ = RecvJuderData(hSocket)
    if (nRet != 0):
        return nRet
    

    # // 生成表明身份的json
    token = {}
    token['token'] = szToken        
    token['action'] = "sendtoken"   

    
    #// 选手向裁判服务器表明身份(Player -> Judger)
    nRet = SendJuderData(hSocket, token)
    if nRet != 0:
        return nRet

    #//身份验证结果(Judger -> Player), 返回字典Message
    nRet, Message = RecvJuderData(hSocket)
    if nRet != 0:
        return nRet
    
    if Message["result"] != 0:
        print("token check error\n")
        return -1

    # // 选手向裁判服务器表明自己已准备就绪(Player -> Judger)
    stReady = {}
    stReady['token'] = szToken
    stReady['action'] = "ready"

    nRet = SendJuderData(hSocket, stReady)
    if nRet != 0:
        return nRet

    # //对战开始通知(Judger -> Player)
    nRet, Message = RecvJuderData(hSocket)
    if nRet != 0:
        return nRet
    
    #初始化地图信息
    pstMapInfo = Message["map"]  
    
    #初始化比赛状态信息
    pstMatchStatus = {}
    pstMatchStatus["time"] = 0

    #初始化飞机状态信息
    pstFlayPlane = {}
    pstFlayPlane["nUavNum"] = len(pstMapInfo["init_UAV"])
    pstFlayPlane["astUav"] = []

    #每一步的飞行计划
    FlyPlane_send = {}
    FlyPlane_send["token"] = szToken
    FlyPlane_send["action"] = "flyPlane"

    for i in range(pstFlayPlane["nUavNum"]):
        pstFlayPlane["astUav"].append(pstMapInfo["init_UAV"][i])

    # // 根据服务器指令，不停的接受发送数据
    build_positions = Build_position(pstMapInfo["building"], pstMapInfo["h_low"],pstMapInfo["h_high"])
    #敌人飞机场
    enemy_park = []
    #追踪字典
    track_dict={}
    #目标货物的字典
    plane_good={}
    #敌机以前的位置
    enemy_position={}


    while True:
        a=time.time()
        # // 进行当前时刻的数据计算, 填充飞行计划，注意：1时刻不能进行移动，即第一次进入该循环时
        FlyPlane,track_dict,plane_good,enemy_position = AlgorithmCalculationFun(pstMapInfo, pstMatchStatus, pstFlayPlane,build_positions,enemy_park,track_dict,plane_good,enemy_position)
        FlyPlane_send['UAV_info'] = FlyPlane["UAV_info"]
        FlyPlane_send["purchase_UAV"] = FlyPlane["purchase_UAV"]


        # print(track_dict)
        # print(plane_good)
        # print("ssss")
        # //发送飞行计划
        nRet = SendJuderData(hSocket, FlyPlane_send)
        if nRet != 0:
            return nRet
        
        # // 接受当前比赛状态
        nRet, pstMatchStatus = RecvJuderData(hSocket)
        if nRet != 0:
            return nRet
        print(pstMatchStatus["time"])
        if pstMatchStatus["time"] == 1:
            enemy_park = [pstMatchStatus["UAV_enemy"][0]["x"], pstMatchStatus["UAV_enemy"][0]["y"]]
        print(time.time()-a)
        if pstMatchStatus["match_status"] == 1:
            print("game over, we value %d, enemy value %d\n", pstMatchStatus["we_value"], pstMatchStatus["enemy_value"])
            hSocket.close()
            return 0

if __name__ == "__main__":
    if len(sys.argv) == 4:
        print("Server Host: " + sys.argv[1])
        print("Server Port: " + sys.argv[2])
        print("Auth Token: " + sys.argv[3])
        main(sys.argv[1], int(sys.argv[2]), sys.argv[3])
    else:
        print("need 3 arguments")