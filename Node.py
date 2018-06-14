
global h_low ,open_list,close_list,map_border,start,end,build_positions,we_positions_3D
class Node:
    def __init__(this, father, x, y,z):
        if x < 0 or x >= map_border[0] or y < 0 or y >= map_border[1] or z>=map_border[2] or z<h_low:
            raise Exception("node position can't beyond the border!")

        this.father = father
        this.x = x
        this.y = y
        this.z = z
        if father != None:
            G2father = calc_G(father, this)
            if not G2father:
                raise Exception("father is not valid!")
            this.G = G2father + father.G
            this.H = calc_H(this, end)
            this.F = this.G + this.H
        else:
            this.G = 0
            this.H = 0
            this.F = 0

    def reset_father(this, father, new_G):
        if father != None:
            this.G = new_G
            this.F = this.G + this.H

        this.father = father

def calc_G(node1, node2):
    x1 = abs(node1.x-node2.x)
    y1 = abs(node1.y-node2.y)
    z1 = abs(node1.z-node2.z)
    if(x1<=1 and y1<=1 and z1<=1):
        return 1

    else:
        return 0

def calc_H(cur, end):
    return abs(end.x-cur.x) + abs(end.y-cur.y)+abs(end.z-cur.z)

# NOTE 这个地方可能成为性能瓶颈
def min_F_node():
    if len(open_list) == 0:
        raise Exception("not exist path!")

    _min = 9999999999999999
    _k = (start.x, start.y,start.z)
    for k,v in open_list.items():
        if _min > v.F:
            _min = v.F
            _k = k
    return open_list[_k]

# 把相邻节点加入open list, 如果发现终点说明找到了路径
def addAdjacentIntoOpen(node):
    # 将该节点从开放列表移到关闭列表当中。
    open_list.pop((node.x, node.y,node.z))
    close_list[(node.x, node.y,node.z)] = node

    adjacent = []
    # 相邻节点要注意边界的情况
    try:
        adjacent.append(Node(node , node.x - 1 , node.y - 1, node.z))
    except Exception as e:
        pass

    try:
        adjacent.append(Node(node , node.x     , node.y - 1, node.z))
    except Exception as e:
        pass

    try:
        adjacent.append(Node(node , node.x + 1 , node.y - 1, node.z))
    except Exception as e:
        pass

    try:
        adjacent.append(Node(node , node.x + 1 , node.y, node.z))
    except Exception as e:
        pass

    try:
        adjacent.append(Node(node , node.x + 1 , node.y + 1, node.z))
    except Exception as e:
        pass

    try:
        adjacent.append(Node(node , node.x     , node.y + 1, node.z))
    except Exception as e:
        pass

    try:
        adjacent.append(Node(node , node.x - 1 , node.y + 1, node.z))
    except Exception as e:
        pass

    try:
        adjacent.append(Node(node , node.x - 1 , node.y, node.z))
    except Exception as e:
        pass

    try:
        adjacent.append(Node(node , node.x     ,node.y ,node.z+1))
    except Exception as e:
        pass

    try:
        adjacent.append(Node(node, node.x, node.y, node.z - 1 ))
    except Exception as e:
        pass

    for a in adjacent:
        if (a.x,a.y,a.z) == (end.x, end.y,end.z):
            new_G = calc_G(a, node) + node.G
            end.reset_father(node, new_G)
            return True
        if (a.x,a.y,a.z) in close_list:
            continue

        if (a.x,a.y,a.z) not in open_list:
            open_list[(a.x,a.y,a.z)] = a
        else:
            exist_node = open_list[(a.x,a.y,a.z)]
            new_G = calc_G(a, node) + node.G
            if new_G < exist_node.G:
                exist_node.reset_father(node, new_G)

    return False

def find_the_path(start, end,build_positions,we_position_3D):
    open_list[(start.x, start.y,start.z)] = start

    for i in range(len(build_positions)):
        block_node=Node(None,build_positions[i][0],build_positions[i][1],build_positions[i][2])
        close_list[(build_positions[i][0],build_positions[i][1],build_positions[i][2])]=block_node
    for i in range(len(we_position_3D)):
        try:
            block_node=Node(None,we_position_3D[i][0],we_position_3D[i][1],we_position_3D[i][2])
        except Exception:
            continue
        close_list[(we_position_3D[i][0],we_position_3D[i][1],we_position_3D[i][2])]=block_node
    the_node = start
    while not addAdjacentIntoOpen(the_node):
        the_node = min_F_node()
    return True


def mark_path(node):
    path=[]
    while(node.father!=None):
        path.append(node)
        node=node.father
    return path[-1]


def path_enemy(low,position,total_position,map_x,map_y,map_z,building_positions,plane_position_3D):
    global h_low, open_list, close_list, map_border, start, end, build_positions, we_positions_3D
    build_positions=building_positions
    we_positions_3D=[]
    for k,v in plane_position_3D.items():
        we_positions_3D.append(v)
    h_low=low
    open_list={}
    close_list={}
    map_border=[map_x,map_y,map_z]
    #如果在目标的上面的话下降
    if position[2]<h_low :
        if position[:2]==total_position[:2] and total_position[2]<h_low:
            if position[2]==0:
                return position[0],position[1],position[2]
            return position[0],position[1],position[2]-1
        else:
            return position[0], position[1], position[2]+1
    else:

        ###$$$$如果start==end咋办？？会不会出错
        if position[:2]==total_position[:2]:
            if position[2]==0:
                return position[0],position[1],position[2]
            return position[0],position[1],position[2]-1
        else:
            start=Node(None,position[0],position[1],position[2])
            end=Node(None,total_position[0],total_position[1],h_low)
            if find_the_path(start,end,build_positions,we_positions_3D):
                next_node=mark_path(end)
                return next_node.x,next_node.y,next_node.z

#UAV_list 为该类型的飞机价格列表
def path_good(low,we_plane,total_position,map_x,map_y,map_z,building_positions,plane_position_3D,we_park):
    global h_low, open_list, close_list, map_border, start, end, build_positions, we_positions_3D
    ###change=1 时表示取到货物
    ###change=0 表示小于h_low起来
    ###change=2 表示到达飞机场充电
    ###change=3 表示飞机到飞机场，下一步也没到能充电

    change=-1
    build_positions = building_positions
    we_positions_3D = []
    for k, v in plane_position_3D.items():
        we_positions_3D.append(v)
    position=[we_plane["x"],we_plane["y"],we_plane["z"]]


    h_low = low
    open_list = {}
    close_list = {}
    map_border = [map_x, map_y, map_z]
    x=we_plane["x"]
    y=we_plane["y"]
    z=we_plane["z"]
    #飞机下去取货
    if position[:2] == total_position[:2]  and total_position[:2]!=we_park :
        #飞机到达目标货物上面
        if position[2] == 1:
            z-=1
            change=1
            #取货物的时候不用减电量

        else:
            z -= 1
        return x,y,z,change
    #飞机下去充电
    if position[:2] == total_position[:2] and total_position[:2] == we_park and position[2]<=h_low:
            if position[2]==1:
                z -= 1
                change=2
            if position[2]==0:
                change=2
            if position[2]>1:
                z -= 1
                ##这边要考虑一遍上来 一遍下去的算法要不然会撞
            return x,y,z,change
    #飞机要上来
    if position[:2]!=total_position[:2] and position[2]<h_low:
        #没考虑想撞
        z+=1
        change=0
        return x,y,z,change
    #飞向货物点在高空区
    if position[:2]!=total_position[:2] and position[2]>=h_low:
        start = Node(None, position[0], position[1], position[2])
        end = Node(None, total_position[0], total_position[1], h_low)
        if find_the_path(start, end, build_positions, we_positions_3D):
            next_node = mark_path(end)
        x=next_node.x
        y=next_node.y
        z=next_node.z
        change=3
        return x,y,z,change

def path_enemy_park(low,we_plane,total_position,map_x,map_y,map_z,building_positions,plane_position_3D):
    global h_low, open_list, close_list, map_border, start, end, build_positions, we_positions_3D
    x=we_plane["x"]
    y=we_plane["y"]
    z=we_plane["z"]
    change=0
    position = [we_plane["x"], we_plane["y"], we_plane["z"]]
    build_positions = building_positions
    we_positions_3D = []
    for k, v in plane_position_3D.items():
        we_positions_3D.append(v)
    h_low = low
    open_list = {}
    close_list = {}
    map_border = [map_x, map_y, map_z]
    if position[:2]==total_position[:2]:
        if we_plane["z"]!=1 :
            z -= 1
            change=1
        else:
            pass
    else:
        if position[2]<h_low:
            if [we_plane["x"],we_plane["y"],we_plane["z"]+1] not in we_positions_3D:
                z += 1
                change=1
            else:
                pass
        else:
            start = Node(None, position[0], position[1], position[2])
            end = Node(None, total_position[0], total_position[1], h_low)
            if find_the_path(start, end, build_positions, we_positions_3D):
                next_node = mark_path(end)
                x = next_node.x
                y = next_node.y
                z = next_node.z
                change=2
    return x,y,z,change



def path_end(low,we_plane,total_position,map_x,map_y,map_z,building_positions,plane_position_3D):
    global h_low, open_list, close_list, map_border, start, end, build_positions, we_positions_3D
    x = we_plane["x"]
    y = we_plane["y"]
    z = we_plane["z"]
    build_positions = building_positions
    we_positions_3D = []
    for k, v in plane_position_3D.items():
        we_positions_3D.append(v)
    h_low = low
    open_list = {}
    close_list = {}
    map_border = [map_x, map_y, map_z]
    position=[we_plane["x"],we_plane["y"],we_plane["z"]]
    #到达货物点
    if position[:2]==total_position[:2]:
        #服务器会自己卸货的
        z-=1
    else:
        if position[2]<h_low:
            z+=1
        else:
            start = Node(None, position[0], position[1], position[2])
            end = Node(None, total_position[0], total_position[1], h_low)
            if find_the_path(start, end, build_positions, we_positions_3D):
                next_node = mark_path(end)
            x = next_node.x
            y = next_node.y
            z = next_node.z

    return x,y,z






