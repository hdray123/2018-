from  Node import path_enemy,path_good,path_end,path_enemy_park
class Move:
    def __init__(self,we_plane,build_positions,enemy_UAVs,goods,we_positions,we_UAVs,track_dict,plane_good,No_good_enemy_positions,goods_end,price_dict,low,high,enemy_position,time,we_value):
        self.we_plane=we_plane
        self.build_positions=build_positions
        self.enemy_UAVs=enemy_UAVs
        self.goods=goods
        self.we_positions=we_positions
        self.we_UAVs=we_UAVs
        self.track_dict=track_dict
        self.plane_good=plane_good
        self.No_good_enemy_positions=No_good_enemy_positions
        self.goods_end=goods_end
        self.price_dict=price_dict
        self.low=low
        self.high=high
        self.enemy_position=enemy_position
        self.time=time
        self.we_value=we_value

    #是否有目标货物
    def Plan_in_goods(self):
        if self.we_plane["no"] in self.plane_good:
            return 1
        return 0

    #是否在追踪列表中
    def Plan_in_track(self):
        if self.we_plane["no"] in self.track_dict:
            return 1
        return 0

    #是否为小飞机
    def is_min_plane(self):
        if self.we_plane["type"]==min_plane_type:
            return 1
        return 0

    # 返回是否添加track_dict
    def add_track(self):
        we_position=[self.we_plane["x"],self.we_plane["y"],self.we_plane["z"]]

        number_enemy=0
        number_we=0
        for plane in self.enemy_UAVs:
            if plane["status"]!=1:
                number_enemy+=1
        for plane in self.we_UAVs:
            if plane["status"]!=1:
                number_we+=1
        #total包含追踪飞机和目标地点
        total_no=[]
        for k,v in self.track_dict.items():
            total_no.append(v)


        #我们飞机到人家飞机距离
        ##添加追踪无货物的飞机的
        value_enemy_to_we={}

        for k,v in self.No_good_enemy_positions.items():
            if k in total_no:
                continue
            else:
                #判断去追那架飞机的代价值=distance/value
                value_enemy_to_we[k]=(max(abs(we_position[0]-v[0]),abs(we_position[1]-v[1]))+abs(we_position[2]-v[2])+1)-(find_plane_value(k,self.price_dict,self.enemy_UAVs)+1)

        if len(value_enemy_to_we)==0:
            pass
        else:

            min=99999999
            no=-1


            for k,v in value_enemy_to_we.items():
                if v<min:
                    min=v
                    no=k
            if no==-1:
                print("error min or no enemy to track !!")
            else:
                value_plane=find_plane_value(no,self.price_dict,self.enemy_UAVs)
                min_value=find_min_value(self.price_dict)
                #我们的飞机数量三倍多余敌机才去用小飞机撞小飞机 ，可能有提升 去撞别人小飞机有点亏
                if number_enemy>number_we/3 and value_plane==min_value:
                    pass
                else:
                    self.track_dict[self.we_plane["no"]]=no
                    return self.track_dict

        for k,v in self.goods_end.items():
            good=find_good(k,self.goods)
            end_positon=[good["end_x"],good["end_y"]]
            if end_positon in total_no:
                continue
            else:
                if Distance_end_2D(end_positon,we_position,self.low)<v:
                    self.track_dict[self.we_plane["no"]]=end_positon
                    return self.track_dict
        return self.track_dict

    # 增加货物列表
    def add_plane_good(self):

        # 能拿的货物dict
        need_electricity = Delivery_elect(self.goods, self.low, self.we_plane,self.time,self.we_value)
        # 删除已经有飞机来拿的货物
        for k, v in self.plane_good.items():
            if type(v) == int:
                if v in need_electricity:
                    need_electricity.pop(v)
        number_good = -1
        max_value = -1
        for k, v in need_electricity.items():
            if max_value < v:
                max_value = v
                number_good = k
        # 没有货物可以拿
        if number_good == -1:
            pass
        else:
            self.plane_good[self.we_plane["no"]] = number_good

        return self.plane_good

    #是否在飞机场里充电
    def Plan_in_Charging(self):
        type_list=find_plane_list(self.price_dict,self.we_plane["type"])
        if self.we_plane["x"]==we_park[0] and self.we_plane["y"]==we_park[1] and self.we_plane["z"]==0:
            if self.we_plane["remain_electricity"]!= type_list["capacity"]:
                return 1
        return 0
    #充电
    def on_charging(self):
        type_list = find_plane_list(self.price_dict, self.we_plane["type"])
        if self.we_plane["remain_electricity"]+type_list["charge"]>=type_list["capacity"]:
            self.we_plane["remain_electricity"]=type_list["capacity"]
        else:
            self.we_plane["remain_electricity"]+=type_list["charge"]
        return self.we_plane

    #向追踪的飞机向他飞去
    def move_enemy(self):
        we_park_3D=[we_park[0],we_park[1],0]
        UAV_price=find_plane_list(self.price_dict,self.we_plane["type"])
        #飞向目标飞机的下一步路径或者是抢先一步到底目标飞机运送货物的终点
        position=[self.we_plane["x"],self.we_plane["y"],self.we_plane["z"]]
        enemy_no=self.track_dict[self.we_plane["no"]]
        #说明是对应飞机编号的
        if type(enemy_no)==int:
            total_position=self.enemy_position[enemy_no]
        #enemy_no为货物终点
        else:
            total_position=[enemy_no[0],enemy_no[1],0]
        x,y,z=path_enemy(self.low,position,total_position,map_x,map_y,map_z,self.build_positions,self.we_positions)

        we_position_list=[]
        for k,v in self.we_positions.items():
            we_position_list.append(v)

        if [x,y,z] in we_position_list or [x,y,z] in self.build_positions:
            if [self.we_plane["x"],self.we_plane["y"],self.we_plane["z"]+1] in we_position_list:
                #在起飞的时候发生堵塞在停机场 只能被动充电
                if [self.we_plane["x"],self.we_plane["y"],self.we_plane["z"]]==we_park_3D:
                    if self.we_plane["remain_electricity"]+UAV_price["charge"]>=UAV_price["capacity"]:
                        self.we_plane["remain_electricity"]=UAV_price["capacity"]
                    else:
                        self.we_plane["remain_electricity"]+=UAV_price["charge"]
            else:
                if self.we_plane["z"]+1>self.high:
                    pass
                else:
                    self.we_plane["z"]+=1
        else:
            self.we_plane["x"] = x
            self.we_plane["y"] = y
            self.we_plane["z"] = z

        self.we_positions[self.we_plane["no"]]=[self.we_plane["x"],self.we_plane["y"],self.we_plane["z"]]

        return self.we_plane,self.we_positions



    #飞向货物
    def move_good_start(self):
        we_park_3D = [we_park[0], we_park[1], 0]

        UAV_price = find_plane_list(self.price_dict, self.we_plane["type"])
        good_no=self.plane_good[self.we_plane["no"]]
        if type(good_no)==int :
            good=find_good(good_no,self.goods)
            if good==-1:
                print("no sucn good no!")
            else:
                total_position = [good["start_x"], good["start_y"], 0]
        else:
            total_position=[we_park[0],we_park[1],0]
        #飞机类型列表
        UAV_price=find_plane_list(self.price_dict,self.we_plane["type"])
        x,y,z,change=path_good(self.low,self.we_plane,total_position,map_x,map_y,map_z,self.build_positions,self.we_positions,we_park)

        we_position_list = []
        for k, v in self.we_positions.items():
            we_position_list.append(v)
        #飞机取货
        if change==1:
            enemy_z=999999

            for plane in self.enemy_UAVs:
                if plane["x"]==good["start_x"] and plane["y"]==good["start_y"]:
                    enemy_z=z

            if enemy_z<z and z==2 :
                pass
            else:
                self.we_plane["x"]=x
                self.we_plane["y"]=y
                self.we_plane["z"]=z
                self.we_plane["goods_no"]=self.plane_good[self.we_plane["no"]]
                good = find_good(self.we_plane["goods_no"], self.goods)
                self.we_plane["remain_electricity"] -=good["weight"]



        #飞机充电  可能不用了
        if change==2:
            self.we_plane["x"] = x
            self.we_plane["y"] = y
            self.we_plane["z"] = z
            if self.we_plane["remain_electricity"] + UAV_price["charge"] >= UAV_price["capacity"]:
                self.we_plane["remain_electricity"] = UAV_price["capacity"]
            else:
                self.we_plane["remain_electricity"] += UAV_price["charge"]
        #飞机在低空区出来
        if change==0:
            if [x, y, z] not in we_position_list:
                self.we_plane["x"] = x
                self.we_plane["y"] = y
                self.we_plane["z"] = z
            else:
                # 在起飞的时候发生堵塞在停机场 只能被动充电
                if [self.we_plane["x"], self.we_plane["y"], self.we_plane["z"]] == we_park_3D:
                    if self.we_plane["remain_electricity"] + UAV_price["charge"] >= UAV_price["capacity"]:
                        self.we_plane["remain_electricity"] = UAV_price["capacity"]
                    else:
                        self.we_plane["remain_electricity"] += UAV_price["charge"]
                else:
                    pass
        ##下去充电和上来以后再写,应该不用了
        if change==-1:
            self.we_plane["x"] = x
            self.we_plane["y"] = y
            self.we_plane["z"] = z

        #在高空区飞行
        if change==3:
            if [x,y,z] in we_position_list:
                self.we_plane["z"] +=1
            else:
                self.we_plane["x"] = x
                self.we_plane["y"] = y
                self.we_plane["z"] = z
        self.we_positions[self.we_plane["no"]] = [self.we_plane["x"], self.we_plane["y"], self.we_plane["z"]]

        return self.we_plane,self.we_positions


    #飞向对方停机场
    def move_enemy_park(self):
        we_park_3D = [we_park[0], we_park[1], 0]
        UAV_price = find_plane_list(self.price_dict, self.we_plane["type"])
        total_position=[enemy_park[0],enemy_park[1],0]
        we_position_list = []
        for k, v in self.we_positions.items():
            if k!=self.we_plane["no"]:
                we_position_list.append(v)
        #在低空区出来
        if self.we_plane["z"]<self.low:
            if [self.we_plane["x"],self.we_plane["y"]]!=enemy_park:
                x=self.we_plane["x"]
                y=self.we_plane["y"]
                z=self.we_plane["z"]+1
                if [x,y,z] in we_position_list:
                    # 在起飞的时候发生堵塞在停机场 只能被动充电
                    if [self.we_plane["x"], self.we_plane["y"], self.we_plane["z"]] == we_park_3D:
                        if self.we_plane["remain_electricity"] + UAV_price["charge"] >= UAV_price["capacity"]:
                            self.we_plane["remain_electricity"] = UAV_price["capacity"]
                        else:
                            self.we_plane["remain_electricity"] += UAV_price["charge"]
                else:
                    self.we_plane["x"] = x
                    self.we_plane["y"] = y
                    self.we_plane["z"] = z
            else:
                if self.we_plane["z"]==1:
                    pass
                else:
                    x = self.we_plane["x"]
                    y = self.we_plane["y"]
                    z = self.we_plane["z"] - 1
                    if [x, y, z] in we_position_list:
                        pass
                    else:
                        self.we_plane["x"] = x
                        self.we_plane["y"] = y
                        self.we_plane["z"] = z
        #在高空区
        else:
            distanc_x=enemy_park[0]-self.we_plane["x"]
            distanc_y=enemy_park[1]-self.we_plane["y"]
            if distanc_x==0:
                x=self.we_plane["x"]
            else:
                x=self.we_plane["x"]+distanc_x/abs(distanc_x)
            if distanc_y==0:
                y=self.we_plane["y"]
            else:
                y=self.we_plane["y"]+distanc_y/abs(distanc_y)
            if distanc_x==0 and distanc_y==0:
                z=self.we_plane["z"]-1
            else:
                z=self.we_plane["z"]
            if self.we_plane["z"]<self.high:
                if [x,y,z] in we_position_list or [x,y,z] in self.build_positions:
                    if distanc_x == 0 and distanc_y == 0:
                        pass
                    else:
                        if [self.we_plane["x"],self.we_plane["y"],self.we_plane["z"]+1] in we_position_list:
                            pass
                        else:
                            self.we_plane["z"]+=1
                else:
                    self.we_plane["x"]=x
                    self.we_plane["y"]=y
                    self.we_plane["z"]=z

        self.we_positions[self.we_plane["no"]] = [self.we_plane["x"], self.we_plane["y"], self.we_plane["z"]]

        return self.we_plane,self.we_positions

    #飞向货物终点
    def move_good_end(self):
        good=find_good(self.we_plane["goods_no"],self.goods)
        total_positon=[good["end_x"],good["end_y"],0]
        # 飞机类型列表
        UAV_price = find_plane_list(self.price_dict, self.we_plane["type"])
        x,y,z=path_end(self.low,self.we_plane,total_positon,map_x,map_y,map_z,self.build_positions,self.we_positions)
        we_position_list = []
        for k, v in self.we_positions.items():
            we_position_list.append(v)
        if [x,y,z] in we_position_list:
            self.we_plane["z"]+=1
            self.we_plane["remain_electricity"]-=good["weight"]
        else:
            self.we_plane["x"] = x
            self.we_plane["y"] = y
            self.we_plane["z"] = z
            self.we_plane["remain_electricity"] -= good["weight"]

        self.we_positions[self.we_plane["no"]] = [self.we_plane["x"], self.we_plane["y"], self.we_plane["z"]]
        return self.we_plane,self.we_positions



#根据飞机类型 返回该类型飞机的详细列表

def find_plane_list(price_list,type):
    for L in price_list:
        if L["type"]==type:
            return L

#货物到达终点需要代价
def Delivery_elect(goods,low,plane,time,we_value):
    dict={}
    for good in goods:
        if good["status"]==0:
            if good["weight"]<plane["load_weight"] :
                etc=(max(abs(good["start_x"]-good["end_x"]),abs(good["start_y"]-good["end_y"]))+2*low)*1.1*good["weight"]
                if etc<plane["remain_electricity"]:
                    #暂时没考虑重量 可能以后再考虑
                    distance= max(abs(plane["x"]-good["start_x"]),abs(plane["y"]-good["start_y"]))+abs(plane["y"]-low)+low*2+max(abs(good["start_x"]-good["end_x"]),abs(good["start_y"]-good["end_y"]))
                    if time<200:
                        dict[good["no"]]=good["value"]/(distance+1)**0.5
                    else:
                        dict[good["no"]] = good["value"] / (distance + 1)
    return dict

#寻找最小的飞机类型
def find_min_type(price_dict):
    min_value=999999
    type=0
    for kind in price_dict:
        if kind["value"]<min_value:
            type=kind["type"]
            min_value=kind["value"]
    return type
#寻找最小飞机的价格
def find_min_value(price_dict):
    min_value=999999
    type=0
    for kind in price_dict:
        if kind["value"]<min_value:
            type=kind["type"]
            min_value=kind["value"]
    return min_value

#根据飞机编号得到它的价值
def  find_plane_value(no,price_dict,UVAs):
    type=-1
    for plane in UVAs:
        if plane["no"]==no:
            type=plane["type"]
            break
    if type==-1:
        print("error plane no!")
    else:
        for plane in price_dict:
            if plane["type"]==type:
                return plane["value"]
    print("errror  price_dict! ")

#根据飞机编号找到飞机
def find_plane(no,UAV):
    for plane in UAV:
        if plane["no"]==no:
            return plane

#根据货物编号寻找货物
def find_good(no,goods):
    for good in goods:
        if good["no"]==no:
            return good
    return -1

#根据货物终点和飞机的距离
def Distance_end_2D(end,position,low):
    return abs(position[2]-low)+max(abs(end[0]-position[0]),abs(end[1]-position[1]))+low




def planes_move(build_positions,enemy_UAVs,goods,we_UAVs,track_dict,plane_good,price_dict,h_low,h_high,map,park_we,park_enemy,Enemy_position,time,we_value):

    #$#goods_end==good_end_postion->distance
    #No_good_enemy_positions==enemy_no->enmey_postion

    global min_plane_type,No_good_enemy_positions,goods_end,we_positions,map_x,map_y,map_z,we_park,enemy_park
    map_x=map[0]
    map_y=map[1]
    map_z=map[2]
    we_positions = {}
    No_good_enemy_positions={}
    goods_end={}
    we_park=park_we
    enemy_park=park_enemy

    min_plane_type=find_min_type(price_dict)
    #获取我自己的位置

    for plane in we_UAVs:
        if plane["status"]!=1:
            we_positions[plane["no"]]=[plane["x"],plane["y"],plane["z"]]

    for plane in enemy_UAVs:
        #比赛规则说我们看不到status==1
        if plane["status"]==0:
            Enemy_position[plane["no"]]=[plane["x"],plane["y"],plane["z"]]
            if plane["goods_no"]==-1:
                No_good_enemy_positions[plane["no"]]=[plane["x"],plane["y"],plane["z"]]
            else:
                good=find_good(plane["goods_no"],goods)
                if good==-1:
                    print("has no such goood !")
                else:
                    good_end_position=[good["end_x"],good["end_y"]]
                    enemy_position=[plane["x"],plane["y"],plane["z"]]
                    distance=Distance_end_2D(good_end_position,enemy_position,h_low)
                    goods_end[good["no"]]=distance


    for i in range(len(we_UAVs)):
        if we_UAVs[i]["status"]!=1:
            Plane=Move(we_UAVs[i],build_positions,enemy_UAVs,goods,we_positions,we_UAVs,track_dict,plane_good,No_good_enemy_positions,goods_end,price_dict,h_low,h_high,Enemy_position,time,we_value)
            #如果小飞机不在追踪列表也不在货物dict看是否能加入不能加入不改变track_dict,能加入改变track_dict

            if we_UAVs[i]["goods_no"]==-1:
                #如果飞机而且不在追踪列表中 ，看是否能加入追踪列表
                if Plane.is_min_plane()==1 and Plane.Plan_in_track()==0:
                    track_dict=Plane.add_track()
                # 飞机在追踪列表里在track_dict中的飞机
                if Plane.Plan_in_track():

                    we_UAVs[i],we_positions = Plane.move_enemy()
                    continue
                #除去追踪的飞机外 那些在飞机场里的飞机是否充满电了 没充满继续冲
                if Plane.Plan_in_Charging():
                    we_UAVs[i]=Plane.on_charging()
                    continue

                if Plane.Plan_in_goods()==0:

                    plane_good=Plane.add_plane_good()

                if Plane.Plan_in_goods():
                    #飞机飞向货物

                    we_UAVs[i],we_positions = Plane.move_good_start()
                    continue
                if Plane.is_min_plane()==1:
                    we_UAVs[i],we_positions=Plane.move_enemy_park()
                    continue
            else:
                we_UAVs[i],we_positions=Plane.move_good_end()
                continue
    #妈的  status==1不用返回 看了我半天
    we_UAVs_T=[]
    for plane in we_UAVs:
        if plane["status"]!=1:
            we_UAVs_T.append(plane)
    return we_UAVs_T,track_dict,plane_good,Enemy_position

















