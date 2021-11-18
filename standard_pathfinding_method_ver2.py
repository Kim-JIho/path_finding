from neo4j import GraphDatabase
import csv
import math
from haversine import haversine

import sys

"""
2021.04.08
경로탐색함수
경로탐색 알고리즘
"""


class Neo4jHelper:
    def __init__(self, uri, user, password):
        self.start_flag = False
        self._driver = GraphDatabase.driver(uri, auth=(user, password), encrypted=False)
        self.rd_map = {}
        self.crs_map = {}
        self.xy_map = {}
        self.load_property()
        self.open_list = []
        self.close_list = []
        self.path = []

    def load_property(self):
        with open('C:/Users/m/Desktop/kisti재난대피/1차년도/QGIS 개발/neo4j 핵심자료/Resource/TL_SPRD_CRS_WGS84_v1.csv', 'r',
                  encoding='utf-8') as crs_id:
            csvf = csv.DictReader(crs_id)
            for row in csvf:
                crs = dict(row)
                self.crs_map[crs['CRS_ID']] = crs

        with open('C:/Users/m/Desktop/kisti재난대피/1차년도/QGIS 개발/neo4j 핵심자료/Resource/TL_SPRD_CRS_WGS84_v1.csv', 'r',
                  encoding='utf-8') as xy:
            csvf = csv.DictReader(xy)
            for row in csvf:
                xy = dict(row)
                self.xy_map[xy['xcoord'], xy['ycoord']] = xy

        with open('C:/Users/m/Desktop/kisti재난대피/1차년도/QGIS 개발/neo4j 핵심자료/Resource/TL_SPRD_RD_v1.csv', 'r',
                  encoding='utf-8') as rd_id:
            csvf = csv.DictReader(rd_id)
            for row in csvf:
                rd = dict(row)
                self.rd_map[rd['ID']] = rd

        print('Property Load Done')
        # file = open('C:/Users/m/Desktop/kisti재난대피/2차년도/test.txt', 'a')
        # file.write('Property Load Done')
        # file.write('\n')

    def close(self):
        self._driver.close()

    def retrieve_shelter_adj(self, _id):
        pass

    def retrieve_adj_node_from_cross(self, _id):
        query = 'match (c:Cross) where c.ID="' + str(_id) + '" return (c)-[:Connection]-(:Road)-[:Connection]-(:Cross)'
        with self._driver.session() as session:
            result = session.write_transaction(self.execute_query, query)
            adj_list = []
            edge_map = {}
            for path in result:
                for rel in path.relationships:
                    snode = rel.nodes[0]
                    enode = rel.nodes[1]
                    st_set = set(snode.labels)
                    ed_set = set(enode.labels)

                    if ed_set.issubset({'Road'}) and snode['ID'] == _id:
                        eid = enode['ID']
                        if edge_map.get(eid) is None:
                            edge_map[eid] = [None, None, None, None,None,None] #2021.05.22 None 2개 추가


                        edge_map[eid][1] = float(self.get_length_of(eid))
                        edge_map[eid][2] = float(self.get_x_of(_id))
                        edge_map[eid][3] = float(self.get_y_of(_id))

                        #2021.05.22
                        if self.get_rk1_of(eid) != '':
                            edge_map[eid][4] = str(self.get_rk1_of(eid))


                        if self.get_rk2_of(eid) != '':
                            edge_map[eid][5] = str(self.get_rk2_of(eid))


                    # from connected road to other crs
                    if ed_set.issubset({'Cross'}) and st_set.issubset({'Road'}) and enode['ID'] != _id:
                        nid = snode['ID']
                        if edge_map.get(nid) is None:
                            edge_map[nid] = [None, None, None, None,None,None]
                        edge_map[nid][0] = enode['ID']

            for edge_id in edge_map.keys():
                adj_list.append(edge_map[edge_id])
            #print("adj_list",adj_list)
            return sorted(adj_list, key=lambda x: x[1])

    @staticmethod
    def execute_query(tx, query):
        result = tx.run(query)
        record = result.single()
        if record is not None:
            return record[0]
        else:
            return None

    @staticmethod
    def execute_query_multi_result(tx, query):
        result = tx.run(query)
        record = result.records()
        if record is not None:
            return record

    def get_x_of(self, _crs_id):
        return float(self.crs_map[_crs_id]['xcoord'])

    def get_y_of(self, _crs_id):
        return float(self.crs_map[_crs_id]['ycoord'])

    def get_ID_of(self, _x, _y):
        return self.xy_map[(_x, _y)]['CRS_ID']

    def get_length_of(self, _rd_id):
        return self.rd_map[_rd_id]['length']

    def get_rn_of(self, _rn_id):
        return self.rd_map[_rn_id]['RN']

    #21.05.22
    def get_rk1_of(self, _rn_id):
        return self.rd_map[_rn_id]['RISK_TYPE_1']

    def get_rk2_of(self, _rn_id):
        return self.rd_map[_rn_id]['RISK_TYPE_2']


    def search(self, id):
        start_node = self.retrieve_adj_node_from_cross(id)
        #node_list = [{"main_node_name": id, "main_node_x": start_node[0][2], "main_node_y": start_node[0][3]}]
        node_list = [{"main_node_name": id, "main_node_x": start_node[0][2], "main_node_y": start_node[0][3], "main_node_risk1": start_node[0][4], "main_node_risk2": start_node[0][5]}]

        for i in start_node:
            dict = {"adj_ID_node": None, "road_length": None, "adj_node_x": None, "adj_node_y": None}
            dict["adj_ID_node"] = i[0]
            dict["road_length"] = i[1]
            node_list.append(dict)

        for i in node_list[1:]:
            try:
                i["adj_node_x"] = float(self.get_x_of(i["adj_ID_node"]))
                i["adj_node_y"] = float(self.get_y_of(i["adj_ID_node"]))
            except:
                pass
        #print("node_list_fi",node_list)
        return node_list

    @classmethod
    def euclidean_distance(cls, sx, sy, ex, ey):
        return math.sqrt(math.pow(ex - sx, 2) + math.pow(ey - sy, 2))

    def haversine_euclidean_distance(cls, sx, sy, ex, ey):
        start = (sx, sy)  # (위도,가로, 경도,세로)
        end = (ex, ey)  # (위도,가로, 경도,세로)
        result = haversine(start, end) * 1000
        return result

    def node_l2_distance(self, node_info_start, node_info_end):
        # start_x = node_info_start[0]["main_node_x"]
        # start_y = node_info_start[0]["main_node_y"]
        #  = node_info_end[0]["main_node_x"]
        #  = node_info_end[0]["main_node_y"]

        # 2021.05.07 x,y값이 잘못 들어가서 거리가 이상하게 나타남
        start_y = node_info_start[0]["main_node_x"]
        start_x = node_info_start[0]["main_node_y"]
        end_y = node_info_end[0]["main_node_x"]
        end_x = node_info_end[0]["main_node_y"]


        return self.haversine_euclidean_distance(start_x, start_y, end_x, end_y)

    def adj_euclidean_distance(self, node_info_start, node_info_end,risk_cd_1,risk_cd_2):
        each_node_distance = []
        dis_dict = {"adj_ID_node": None, "destination_node_ID": None, "adj_distance": None}
        dis_dict["destination_node_ID"] = node_info_end[0]["main_node_name"]

        for i in node_info_start[1:]:
            temp_dict = {"adj_ID_node": None, "adj_distance": None}
            start_node_ID = i["adj_ID_node"]
            temp_dict["adj_ID_node"] = start_node_ID
            end_node_ID = node_info_end[0]["main_node_name"]

            start_x = i["adj_node_x"]
            start_y = i["adj_node_y"]
            end_x = node_info_end[0]["main_node_x"]
            end_y = node_info_end[0]["main_node_y"]

            print("risk_cd_1,2",risk_cd_1,risk_cd_2)

            if (start_x != None) and (end_x != None) and (start_y != None) and (end_y != None):
                #2021.05.22 여기다 가중치 업데이트 하면 됨
                #if (risk_cd_1 == '2') or (risk_cd_2 == '2'): #여기서 가중치 조절
                if (risk_cd_1 == '5') or (risk_cd_2 == '5'): #여기서 가중치 조절
                    print("오오오오오오오오오오")
                    # 알파
                    temp_dict["adj_distance"] = self.haversine_euclidean_distance(start_y, start_x, end_y, end_x) * 1.8
                    each_node_distance.append(temp_dict)
                else:
                    temp_dict["adj_distance"] = self.haversine_euclidean_distance(start_y, start_x, end_y, end_x) * 1
                    each_node_distance.append(temp_dict)
            else:
                pass

        return each_node_distance

    def get_all_shelter(self):
        query = 'match (s:Shelter) return (s);'
        with self._driver.session() as session:
            result = session.write_transaction(self.execute_query_multi_result, query)
            return result

    def get_all_shelter_json(self):
        import json
        with open('C:/Users/m/Desktop/kisti재난대피/1차년도/QGIS 개발/neo4j 핵심자료/Resource/shelter_rn_id.json', 'r',
                  encoding='utf-8') as shelters:
            return json.loads(shelters.read(), encoding='utf-8')

    def retrieve_adj_shelter(self, crs_id, k):
        current_x = self.get_x_of(crs_id)
        current_y = self.get_y_of(crs_id)
        shelters = self.get_all_shelter_json()
        shelters_list = []
        for shelter in shelters:

            # 수용인원 변수 추가
            # shelters_list.append([shelter['ID'],self.haversine_euclidean_distance(current_x, current_y, shelter['xcord'],shelter['ycord']),shelter['fclty_ar']])
            # 2021.05.07 거리 값 수정
            shelters_list.append([shelter['ID'],
                                  self.haversine_euclidean_distance(current_y, current_x, shelter['ycord'],
                                                                    shelter['xcord']), shelter['fclty_ar']])

        return sorted(shelters_list, key=lambda sh: sh[1])[:k]

    def value_update(self, pre_open_list, pre_close_list): #flag_update
        update_open_list = pre_open_list
        update_close_list = pre_close_list

        for i in update_open_list:
            for j in update_close_list:
                if self.start_flag == False: #처음에만 실행되는것 초기값으로 넣는거 이후에는 실행안되는 if
                    self.start_flag = True
                    break
                elif (i["parent_node"] == j["adj_ID_node"]) and (i["flag_var"] == False):
                    i["g_value"] = i["g_value"] + j["g_value"]
                    i["f_value"] = i["g_value"] + i["h_value"]
                    i["flag_var"] = True

        return update_open_list

    def path_finding(self, node_info_start, node_info_end):
        start_point_node = node_info_start[0]["main_node_name"]
        destination_node = node_info_end[0]["main_node_name"]
        risk_cd_1 = 0
        risk_cd_2 = 0

        #print("start_point_node", start_point_node)
        #print(start_point_node)
        print("destination_node", destination_node)

        # file = open('C:/Users/m/Desktop/kisti재난대피/2차년도/test.txt', 'a')
        #
        # file.write("start_point_node \n")
        # file.write(start_point_node)
        # file.write('\n')
        #
        # file.write("destination_node \n")
        # file.write(destination_node)
        # file.write('\n')
        #
        # file.close()



        adj_search = self.search(start_point_node)

        print("adj_search_path",adj_search) #21.05.22 기준
        risk_cd_1=adj_search[0]['main_node_risk1']
        risk_cd_2=adj_search[0]['main_node_risk2']
        print("risk_cd_1,risk_cd_2",risk_cd_1,risk_cd_2)

        # 인접노드 거리 계산
        each_node_distance = self.adj_euclidean_distance(node_info_start, node_info_end,risk_cd_1,risk_cd_2)

        #print("each_node_distance", each_node_distance)
        #print("adj_search", adj_search)
        # file = open('C:/Users/m/Desktop/kisti재난대피/2차년도/test.txt', 'a')
        #
        # file.write("each_node_distance \n")
        # file.writelines(each_node_distance)
        # file.write('\n')
        #
        # file.write("adj_search \n")
        # file.write(adj_search)
        # file.write('\n')
        #
        # file.close()

        for i in each_node_distance:
            for j in adj_search[1:]:
                if i["adj_ID_node"] == j["adj_ID_node"]:
                    i["road_length"] = j["road_length"]
                    i["parent_node"] = start_point_node

        each_node_value = each_node_distance
        for i in each_node_value:
            i["g_value"] = 0
            i["h_value"] = i["adj_distance"]
            i["f_value"] = i["g_value"] + i["h_value"]
            i["parent_node"] = node_info_start[0]["main_node_name"]
            del i["adj_distance"]
            i["flag_var"] = False

            flag_var = True
            for close_list_node in self.close_list:
                if close_list_node["adj_ID_node"] == i["adj_ID_node"] and close_list_node["parent_node"] == i[
                    "parent_node"]:

                    flag_var = False
                    break
                elif self.close_list[-1]["parent_node"] == i["adj_ID_node"]:
                    flag_var = False

            if flag_var == True:
                self.open_list.append(i)

        #self.open_list = sorted(self.open_list, key=lambda adj_dist: (adj_dist["h_value"]), reverse=True)
        self.open_list = sorted(self.open_list, key=lambda adj_dist: (adj_dist["f_value"]), reverse=True) #2021.05.12
        #i = temp_list가 문제를 일으켜서 다시 해봄
        print("self.open_list0",self.open_list)


        #print("self.open_list", self.open_list) #여기서 방금 발견된 노드에 대해서 load_lengh의 형태로 붙으면서 g값은 0으로 나옴
        # file = open('C:/Users/m/Desktop/kisti재난대피/2차년도/test.txt', 'a')
        # file.write("open_list 1\n")
        # file.write(self.open_list)
        # file.write('\n')
        #
        # file.close()

        """
        2021.05.04
        여기서 뭔가 이상하게 다른게 closed list에 붙음 

        오픈
        {'adj_ID_node': '3b1baa3e30', 'road_length': 15.35313022951852, 'parent_node': '1a2994f783', 'g_value': 0, 'h_value': 38.55644170707723, 'f_value': 38.55644170707723, 'flag_var': False}
        {'adj_ID_node': 'c2604e43c2', 'road_length': 58.139464590539895, 'parent_node': '1a2994f783', 'g_value': 0, 'h_value': 0.0, 'f_value': 0.0, 'flag_var': False}
        클로즈 
        {'adj_ID_node': '1a2994f783', 'parent_node': '111b000b6e', 'g_value': 1030.274340557873, 'h_value': 43.44912420887195, 'f_value': 1073.723464766745, 'flag_var': True}
        {'adj_ID_node': '27a28f37d3', 'parent_node': '581cd6fbee', 'g_value': 349.0811594452879, 'h_value': 728.1688888724525, 'f_value': 1077.2500483177405, 'flag_var': True}]
        """
        # open_list에서 목적지까지 거리가 가장 짧을것으로 추측되는 노드(h가 가장 낮은 노드)를 정렬(오름차순)해서 가져옴
        for i in self.open_list[-1:]:
            for k in self.open_list:
                if 'road_length' in k.keys():
                    k["g_value"] = k["road_length"]
                    del k["road_length"]
                    k["f_value"] = k["g_value"] + k["h_value"]

            #print("ii 11: ",i)

            self.open_list = sorted(self.open_list, key=lambda adj_dist: (adj_dist["f_value"]), reverse=True)
            #print("pre_update self.open_list", self.open_list)
            # file = open('C:/Users/m/Desktop/kisti재난대피/2차년도/test.txt', 'a')
            #
            # file.write("self.open_list 2\n")
            # file.write(self.open_list)
            # file.write('\n')
            #
            # file.close()

            """
            2021.05.10
            업데이트하면서 오픈리스트에 기존의 값을 지우지 않고 붙여넣기만 해서 문제인듯
            """
            self.value_update(self.open_list, self.close_list)

            self.open_list = sorted(self.open_list, key=lambda adj_dist: (adj_dist["f_value"]), reverse=True)

            up_ip_list = self.update_de_duplicate() #2021.05.10 수정
            self.open_list = up_ip_list

            #self.update_de_duplicate()
            self.open_list = sorted(self.open_list, key=lambda adj_dist: (adj_dist["f_value"]), reverse=True)
            #print("after_update self.open_list", self.open_list)
            # file = open('C:/Users/m/Desktop/kisti재난대피/2차년도/test.txt', 'a')
            #
            # file.write("self.open_list 3\n")
            # file.write(self.open_list)
            # file.write('\n')
            #
            # file.close()
            # 2021.05.04 f값으로 정렬했지만 이상한게 튀어나옴 --> f값으로 정렬해서 f가 가장 낮은걸 가져오는건 맞아
            # 그 노드가 정답이 아닐지라도

            temp_list = self.open_list[-1:].pop()
            #i = temp_list  # --> 이것때문에 갑자기 close list가 비어버리네?? 왜지?
            #print("close list222222222",self.close_list)
            #print("temp_list", temp_list) #ec6ecd9108

            # file = open('C:/Users/m/Desktop/kisti재난대피/2차년도/test.txt', 'a')
            # file.write("temp_list 2\n")
            # file.write(temp_list)
            # file.write('\n')
            #
            # file.close()

            close_node_name = temp_list["adj_ID_node"]
            del self.open_list[-1]  # pop으로 꺼내온 마지막 f가 가장 낮은 노드를 삭제

            # self.close_list.append(temp_list) #방문노드(close)에 가장 낮은 f값을 가진 노드를 넣는다

            print("after_update self.open_list222222222", self.open_list)

            #print("iii", i)
            # file = open('C:/Users/m/Desktop/kisti재난대피/2차년도/test.txt', 'a')
            # file.write("self.close_list \n")
            # file.write(self.close_list)
            # file.write('\n')
            #
            # file.write("iii \n")
            # file.write(i)
            # file.write('\n')
            #
            # file.close()

            """
            2021.05.04.
            f값이 틀렸어도 다시 찾으면 돼
            그러니까 조건이 잘못된거임 

            꺼내온 것과 지금 조회하고 있는 것이 괴리가 있는거같은데?
            """
            # 2021.05.06 여기다가 마지막 노드를 붙이자
            if i["adj_ID_node"] == destination_node:
                for j in node_info_start:
                    #print("jjj", j)
                    # file = open('C:/Users/m/Desktop/kisti재난대피/2차년도/test.txt', 'a')
                    #
                    # file.write("jjj \n")
                    # file.write(j)
                    # file.write('\n')
                    #
                    # file.close()
                    try:
                        if j["adj_ID_node"] == destination_node:
                            # if j["main_node_name"] == destination_node:
                            self.close_list.append(i)  # 2021.05.06
                            self.path.append(self.close_list)
                    except:
                        pass
            else:
                self.close_list.append(temp_list)
                restart_node = self.search(close_node_name)
                self.path_finding(restart_node, node_info_end)

        #print("리턴을 못했어요~")
        return self.path

    def to_cross_from_shelter(self, _id):
        query = 'match(s: Shelter) where s.ID = "' + str(
            _id) + '" return (s) - [:Connection]-(:Road) - [: Connection]-(:Cross)'
        with self._driver.session() as session:
            result = session.write_transaction(self.execute_query, query)
            adj_list = []
            for path in result:
                for rel in path.relationships:
                    snode = rel.nodes[0]
                    enode = rel.nodes[1]
                    st_set = set(snode.labels)
                    ed_set = set(enode.labels)

                    if ed_set.issubset({'Cross'}):
                        adj_list.append(enode['ID'])

                    elif st_set.issubset({'Cross'}):
                        adj_list.append(snode['ID'])

            temp_list = set(adj_list)
            adj_list = []
            for cross in temp_list:
                adj_list.append(cross)

            return adj_list

    def disaster_A_star(self, x, y, disaster_code):
        start_ID = self.get_ID_of(x, y)
        start_node_info = {'adj_ID_node': start_ID, 'parent_node': None, 'g_value': 0, 'h_value': 0, 'f_value': 0,
                           'flag_var': False}

        self.close_list.append(start_node_info)

        if disaster_code == 1:
            shelter_list = []
            for sh in self.retrieve_adj_shelter(start_ID, 5):
                shelter_list.append(sh)

            first_shelter = shelter_list[0][0]
            shelter_adj_cross = self.to_cross_from_shelter(first_shelter)

        start_node = self.search(start_ID)
        temp_adj_cross = []
        for i in shelter_adj_cross:
            ii = self.search(i)
            temp = self.node_l2_distance(start_node, ii)
            temp_tupple = {"nodeID": i, "distance": temp}
            temp_adj_cross.append(temp_tupple)
        temp_adj_cross = sorted(temp_adj_cross, key=lambda temp_adj_cross: (temp_adj_cross["distance"]), reverse=False)
        print("shelter_candidate:  ", temp_adj_cross)
        # file = open('C:/Users/m/Desktop/kisti재난대피/2차년도/test.txt', 'a')
        # file.write("shelter_candidate \n")
        # file.write(temp_adj_cross)
        # file.write('\n')
        #
        # file.close()

        end_node = self.search(temp_adj_cross[0]['nodeID'])

        # 2021.04.14 20시 주석
        print("start_node: ", start_node_info['adj_ID_node'], "end_node: ", end_node[0]["main_node_name"])
        # file = open('C:/Users/m/Desktop/kisti재난대피/2차년도/test.txt', 'a')
        # file.write("start_node: \n")
        # file.write(start_node_info['adj_ID_node'])
        # file.write('\n')
        # file.write("end_node: \n")

        # file.write(end_node[0]["main_node_name"])
        # file.write('\n')
        #
        # file.close()

        close_list_final = self.path_finding(start_node, end_node)
        path = self.result_parsing(close_list_final)
        # print("path",path)
        final_path = self.from_id_to_xy(path)

        # return path
        return final_path

    #2021.05.10 메인쪽(pathfinding)에서 새로운 발견 노드를 오픈리스트에 그냥 붙인다.
    #
    def update_de_duplicate(self):
        temp_openlist = self.open_list.copy()

        temp_id = 0
        temp_parent = 0
        temp_value = 0
        temp_id_list = []
        temp_parent_list = []
        temp_value_list = []
        # 2021.05.10
        # 중복을 먼저 제거하자
        # 완벽하게 같은것들은 제거하고
        # 여기서 이제 f값이 큰걸 날려버려
        new_list = []
        for i in temp_openlist:
            if i not in new_list:
                new_list.append(i)

        for node in new_list:
            for others in new_list:
                #2021.05.10
                #오픈리스트에서 현재 노드(adj_ID_node)가 이름은 같고 부모가 다르고 뒤쪽에 나온 다른 노드의 f가 크면
                #others(비교노드)의 값을 임시저장
                #그렇지 않으면(node-기준노드)의 값을 임시저장 --> 잘못된거같음. 반대로 해야 하는거 같은데
                #아니다 그 값을 찾으면 그것을 실제 self.open_list에서 삭제해버림
                if node["adj_ID_node"] == others["adj_ID_node"] and node["parent_node"] != others["parent_node"] and \
                        node["f_value"] < others["f_value"]:
                    print("if")
                    temp_id = others["adj_ID_node"]
                    temp_id_list.append(temp_id)
                    temp_parent = others["parent_node"]
                    temp_parent_list.append(temp_parent)
                    temp_value = others["f_value"]
                    temp_value_list.append(temp_value)
                elif node["adj_ID_node"] == others["adj_ID_node"] and node["parent_node"] != others["parent_node"] and \
                        node["f_value"] >= others["f_value"]:
                    print("elif")
                    temp_id = node["adj_ID_node"]
                    temp_id_list.append(temp_id)
                    temp_parent = node["parent_node"]
                    temp_parent_list.append(temp_parent)
                    temp_value = node["f_value"]
                    temp_value_list.append(temp_value)

                #2021.05.10
                #f값이 큰것을 제거하는 것 하지만 제거가 완벽하지 않음
                # temp_index = 0
                # for i in self.open_list:
                #     if i["adj_ID_node"] == temp_id and i["parent_node"] == temp_parent and i["f_value"] == temp_value:
                #         del self.open_list[temp_index]
                #     temp_index = temp_index + 1

                """
                2021.05.10
                중복이 제거된 오픈리스트에서 (위에서 제거) f값이 큰 기존의 오픈리스트 리스트 한개를 삭제함
                이것은 이제 노드의 이름은 같지만 부모와 f값이 틀릴 경우 우선순위가 낮은 것을 삭제하는 결과
                """
                # index = 0
                # for i in new_list:
                #     if i["adj_ID_node"] == temp_id and i["parent_node"] == temp_parent and i["f_value"] == temp_value:
                #         del new_list[index]
                #     index = index + 1
                #

                for tp in range(len(temp_id_list)):
                    #print("tp", tp)
                    index = 0
                    #print("init_index", index)
                    for i in new_list:
                        #print(index)
                        if i["adj_ID_node"] == temp_id_list[tp] and i["parent_node"] == temp_parent_list[tp] and i[
                            "f_value"] == temp_value_list[tp]:
                            #print(i)
                            #print("new_list[index]", new_list[index])
                            print("del") #2021.05.11 제대로 삭제가 안되나 중복이 남아있네
                            del new_list[index]
                        pass
                        index = index + 1

        return new_list

    def result_parsing(self, close_list_final):
        final_path = []
        temp = close_list_final.copy()
        pre_path_list = temp[-1].copy()

        final_path.append(pre_path_list[-1])
        adj_ID_node = pre_path_list[-1]["adj_ID_node"]
        parent_node = pre_path_list[-1]["parent_node"]
        del pre_path_list[-1]

        #2021.05.10 밤 print("pre_path_list[::-1]", pre_path_list[::-1])  # 2021.05.03 확인용
        # file = open('C:/Users/m/Desktop/kisti재난대피/2차년도/test.txt', 'a')
        # file.write("pre_path_list[::-1]: \n")
        # file.write(pre_path_list[::-1])
        # file.write('\n')
        #
        # file.close()

        for pre_path in pre_path_list[::-1]:
            if pre_path["adj_ID_node"] == parent_node:
                final_path.append(pre_path)
                adj_ID_node = pre_path["adj_ID_node"]
                parent_node = pre_path["parent_node"]

        temp_list = []
        for i in final_path[::-1]:
            temp_list.append(i)

        final_path = temp_list

        return final_path

    def from_id_to_xy(self, final_path):
        temp_path_list = final_path.copy()
        final_path_list = []

        for path in temp_path_list:
            temp_list = []
            ID = path["adj_ID_node"]
            length = path["g_value"]
            x = self.get_x_of(ID)
            y = self.get_y_of(ID)
            temp_list.append(ID)
            temp_list.append(length)
            temp_list.append(x)
            temp_list.append(y)

            final_path_list.append(temp_list)

        return final_path_list



