from neo4j import GraphDatabase
import csv
import math
from haversine import haversine

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
        self.risk_type_map= {} #2021.05.22
        self.load_property()
        self.open_list = []
        self.close_list = []
        self.path = []

        self.input_risk = 0 #2021.05.22

        """
        2021.04.28
        """
        self.cur_available_refugee = 0
        self.total_number_of_refugee = 0

        """
        2021.05.03 제어
        """
        self.multi_path_list = []
        self.path_flag = 0
        """
        2021.05.07 거리 오류 수정(유클리드 거리 입력값 문제 해결)
        2021.05.12 업데이트 후 아래 주석이 최종적인 결과(계속 결과를 수정함)
        path_flag = 0 --> start_node:  023dd00b8c end_node:  4897df8757 경로 마지막 전: d2e983d530 (일치) 경로까지 일치 19.5초
        path_flag = 1 --> start_node:  023dd00b8c end_node:  88757a837f 경로 마지막 전: b006a80174 (일치) 경로까지 일치
        path_flag = 2 --> start_node:  023dd00b8c end_node:  a8e1098a28 경로 마지막 전: a96801e563 (일치) 경로까지 일치
        path_flag = 3 --> start_node:  023dd00b8c end_node:  76a580bf25 경로 마지막 전: d0d45e89be (일치) 경로까지 일치
        path_flag = 4 --> start_node:  023dd00b8c end_node:  0d6540876a 경로 마지막 전: 827aecdfff (일치)

        path_flag = 5 --> start_node:  023dd00b8c end_node:  669c41fb2a 경로 마지막 전: 4928a8af6c (일치) 
        path_flag = 6 --> start_node:  023dd00b8c end_node:  e5b110fffa 경로 마지막 전: b6feeef3d1 (일치) 
        path_flag = 7 --> start_node:  023dd00b8c end_node:  591bf6b9b4 경로 마지막 전: ad2d347a27 (일치) 

        path_flag = 8 --> start_node:  023dd00b8c end_node:  28a56b1ee1 경로 마지막 전: 3018830e5d (일치) 경로까지 일치
        path_flag = 9 --> start_node:  023dd00b8c end_node:  18e4ac64ee 경로 마지막 전: 안나옴 

        --> 거리 수정 했지만 이 부분 오류는 해결이 안됨. start_node:  023dd00b8c end_node:  18e4ac64ee
        """

        # path_flag = 0 --> start_node:  023dd00b8c end_node:  4897df8757 경로 마지막: 4897df8757 (일치)
        # path_flag = 1 --> start_node:  023dd00b8c end_node:  a8e1098a28 경로 마지막: a96801e563 (마지막 노드와 연결되어 있음)
        # path_flag = 2 --> start_node:  023dd00b8c end_node:  0d6540876a 경로 마지막: c2604e43c2 (실패, 엉뚱한 곳)
        # path_flag = 3 --> start_node:  023dd00b8c end_node:  88757a837f 경로 마지막: 88757a837f (일치)
        # path_flag = 4 --> start_node:  023dd00b8c end_node:  e5b110fffa 경로 마지막: fbed0fc93b (엉뚱한 곳)

        # 2021.05.06
        # 엮는 곳 수정 제대로 안하는데 결과
        # k=0,1,2,3,4 전부 제대로 경로가 도출됨 (result_parsing을 수정하지 않았는데 되네?)

        # 2021.05.07
        # = 6으로 테스트
        # shelter_candidate:   [{'nodeID': '18e4ac64ee', 'distance': 1196.8226918944483}, {'nodeID': '55f2842a2b', 'distance': 1225.2091943246955}]
        # start_node:  023dd00b8c end_node:  18e4ac64ee

    def load_property(self):
        #with open('C:/Users/m/Desktop/kisti재난대피/1차년도/QGIS 개발/neo4j 핵심자료/Resource/TL_SPRD_CRS_WGS84.csv', 'r', encoding='utf-8') as crs_id:
        with open('C:/Users/m/Desktop/kisti재난대피/1차년도/QGIS 개발/neo4j 핵심자료/Resource/TL_SPRD_CRS_WGS84(21.05.21).csv', 'r',
              encoding='utf-8') as crs_id:
            csvf = csv.DictReader(crs_id)
            for row in csvf:
                crs = dict(row)
                self.crs_map[crs['CRS_ID']] = crs

        #with open('C:/Users/m/Desktop/kisti재난대피/1차년도/QGIS 개발/neo4j 핵심자료/Resource/TL_SPRD_CRS_WGS84.csv', 'r', encoding='utf-8') as xy:
        with open('C:/Users/m/Desktop/kisti재난대피/1차년도/QGIS 개발/neo4j 핵심자료/Resource/TL_SPRD_CRS_WGS84(21.05.21).csv', 'r', encoding='utf-8') as xy:
            csvf = csv.DictReader(xy)
            for row in csvf:
                xy = dict(row)
                self.xy_map[xy['xcoord'], xy['ycoord']] = xy

        #with open('C:/Users/m/Desktop/kisti재난대피/1차년도/QGIS 개발/neo4j 핵심자료/Resource/TL_SPRD_RD.csv', 'r',encoding='utf-8') as rd_id:
        with open('C:/Users/m/Desktop/kisti재난대피/1차년도/QGIS 개발/neo4j 핵심자료/Resource/TL_SPRD_RD(21.05.21).csv', 'r',encoding='utf-8') as rd_id:
            csvf = csv.DictReader(rd_id)
            for row in csvf:
                rd = dict(row)
                self.rd_map[rd['ID']] = rd

        # with open('C:/Users/m/Desktop/kisti재난대피/1차년도/QGIS 개발/neo4j 핵심자료/Resource/TL_SPRD_RD(21.05.21).csv', 'r',encoding='utf-8') as rk_ty:
        #     csvf = csv.DictReader(rk_ty)
        #     for row in csvf:
        #         risk_type = dict(row)
        #         self.risk_type_map[risk_type['length'], risk_type['ID']] = risk_type

        print('Property Load Done')

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
                            edge_map[eid] = [None, None, None, None,None,None]
                        edge_map[eid][1] = float(self.get_length_of(eid))
                        edge_map[eid][2] = float(self.get_x_of(_id))
                        edge_map[eid][3] = float(self.get_y_of(_id))

                        #2021.05.22
                        if self.get_rk1_of(eid) != '':
                            edge_map[eid][4] = str(self.get_rk1_of(eid))
                        else:
                            edge_map[eid][4] = str(self.get_rk_of(eid))

                        if self.get_rk2_of(eid) != '':
                            edge_map[eid][5] = str(self.get_rk2_of(eid))
                        else:
                            edge_map[eid][5] = str(self.get_rk2_of(eid))

                    # from connected road to other crs
                    if ed_set.issubset({'Cross'}) and st_set.issubset({'Road'}) and enode['ID'] != _id:
                        nid = snode['ID']
                        if edge_map.get(nid) is None:
                            edge_map[nid] = [None, None, None, None,None,None]
                        edge_map[nid][0] = enode['ID']

            for edge_id in edge_map.keys():
                adj_list.append(edge_map[edge_id])
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

    #2021.05.22 속성값 로드 #엣지 정보에서 그 엣지가 무엇에 취약한지 확인하는 속성을 가져온다
    def get_rk1_of(self, _rn_id):
        return self.rd_map[_rn_id]['RISK_TYPE_1']

    def get_rk2_of(self, _rn_id):
        return self.rd_map[_rn_id]['RISK_TYPE_2']

    def search(self, id):
        start_node = self.retrieve_adj_node_from_cross(id)
        #node_list = [{"main_node_name": id, "main_node_x": start_node[0][2], "main_node_y": start_node[0][3], "main_node_risk_type1": start_node[0][4], "main_node_risk_type2": start_node[0][5]}]
        node_list = [{"main_node_name": id, "main_node_x": start_node[0][2], "main_node_y": start_node[0][3]}]
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

    def adj_euclidean_distance(self, node_info_start, node_info_end):
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

            if (start_x != None) and (end_x != None) and (start_y != None) and (end_y != None):
                #2021.05.22 여기다 가중치 업데이트 하면 됨
                if (risk_cd_1 == '2') or (risk_cd_2 == '2'): #여기서 가중치 조절
                    temp_dict["adj_distance"] = self.haversine_euclidean_distance(start_y, start_x, end_y, end_x) * 1234
                    each_node_distance.append(temp_dict)
                else:
                    temp_dict["adj_distance"] = self.haversine_euclidean_distance(start_y, start_x, end_y, end_x) * 0.0001
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

    """
    21.04.28
    수용인원 변환 추가
    """

    def retrieve_adj_shelter(self, crs_id, k):
        current_x = self.get_x_of(crs_id)
        current_y = self.get_y_of(crs_id)

        shelters = self.get_all_shelter_json()
        shelters_list = []

        for shelter in shelters:
            # shelters_list.append([shelter['ID'], self.haversine_euclidean_distance(current_x, current_y, shelter['xcord'], shelter['ycord'])])

            # 수용인원 변수 추가
            # shelters_list.append([shelter['ID'],self.haversine_euclidean_distance(current_x, current_y, shelter['xcord'],shelter['ycord']),shelter['fclty_ar']])
            # 2021.05.07 거리 값 수정
            shelters_list.append([shelter['ID'],
                                  self.haversine_euclidean_distance(current_y, current_x, shelter['ycord'],
                                                                    shelter['xcord']), shelter['fclty_ar']])
        # print("shelters_list",shelters_list)

        return sorted(shelters_list, key=lambda sh: sh[1])[:k]

    def value_update(self, pre_open_list, pre_close_list):
        update_open_list = pre_open_list
        update_close_list = pre_close_list

        for i in update_open_list:
            for j in update_close_list:
                if self.start_flag == False:
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

        # start_node:  023dd00b8c end_node:  a8e1098a28 // start_node:  023dd00b8c end_node:  0d6540876a

        # print("start_point_node",start_point_node)
        # print("destination_node",destination_node)
        # 인접노드 거리 계산
        each_node_distance = self.adj_euclidean_distance(node_info_start, node_info_end)
        adj_search = self.search(start_point_node)
        # print("each_node_distance",each_node_distance)
        # print("adj_search",adj_search)

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

        for i in self.open_list[-1:]:
            for k in self.open_list:
                if 'road_length' in k.keys():
                    k["g_value"] = k["road_length"]
                    del k["road_length"]
                    k["f_value"] = k["g_value"] + k["h_value"]

            self.open_list = sorted(self.open_list, key=lambda adj_dist: (adj_dist["f_value"]), reverse=True)

            self.value_update(self.open_list, self.close_list)

            self.open_list = sorted(self.open_list, key=lambda adj_dist: (adj_dist["f_value"]), reverse=True)

            #self.update_de_duplicate()
            #2021.05.12 추가
            up_ip_list = self.update_de_duplicate() #2021.05.10 수정
            self.open_list = up_ip_list
            self.open_list = sorted(self.open_list, key=lambda adj_dist: (adj_dist["f_value"]), reverse=True)


            temp_list = self.open_list[-1:].pop()
            #i = temp_list 2021.05.12 주석처리
            close_node_name = temp_list["adj_ID_node"]

            del self.open_list[-1]
            #self.close_list.append(temp_list)

            # 20201.05.04
            # print(" self.close_list", self.close_list)

            if i["adj_ID_node"] == destination_node:
                for j in node_info_start:
                    try:
                        if j["adj_ID_node"] == destination_node:
                            self.close_list.append(i)  # 2021.05.06 마지막 노드 추가 (i)에서 붙임
                            self.path.append(self.close_list)
                    except:
                        pass
            else:
                self.close_list.append(temp_list)
                restart_node = self.search(close_node_name)
                self.path_finding(restart_node, node_info_end)

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

    """
    2021.04.30
    1. 피난민 인원 수 확인
    2. 현재 근거리 대피소 탐색
    3. 근거리 대피소 수용인원 확인
    4. 총 수용인원 - 대피소 수용인원
    5. 경로 탐색 - 반복
    """

    """
    2021.04.30
    path_flag 제어
    disaster_a_star 제어
    """

    def multi_path(self, x, y, disaster_code, refugee):
        paths = self.disaster_A_star(x, y, disaster_code, refugee)  # 2021.05.03 리턴을

        if self.total_number_of_refugee > 0:
            self.path_flag = self.path_flag + 1
            self.multi_path(x, y, disaster_code, self.total_number_of_refugee)
        elif self.total_number_of_refugee <= 0:
            return paths

    # path_flag 제어

    def disaster_A_star(self, x, y, disaster_code, refugee):  # refugee 난민

        self.input_risk=disaster_code
        print("self.in_r",self.input_risk)

        self.total_number_of_refugee = refugee  # 전체 피난민의 수
        dic_seq_path = {}

        start_ID = self.get_ID_of(x, y)
        start_node_info = {'adj_ID_node': start_ID, 'parent_node': None, 'g_value': 0, 'h_value': 0, 'f_value': 0,
                           'flag_var': False}

        self.close_list.append(start_node_info)

        #disaster code 2 = 붕괴위험
        if disaster_code == 2:
            shelter_list = []

            # 시작노드, 대피소 갯수만큼 정렬해서 불러옴
            # 그 중 가장 가까운 대피소를 가져오고 그 대피소에 가장 가까운 크로스 노드를 가져옴
            # 5 --> 20으로 바꿔야 함
            shelter_num = 5
            for sh in self.retrieve_adj_shelter(start_ID,
                                                shelter_num + self.path_flag):  # 처음엔 0번째 그다음엔 6개중 1번째 그다음엔 7개중 2번째
                shelter_list.append(sh)
            print("shelter_list", shelter_list)

            """
            2021.04.28
            수용인원 변환 (fclty_ar -> available_refugee)
            """
            update_shelter_list = shelter_list.copy()
            # 처음엔 수용인원 그대로

            for i in update_shelter_list:
                temp = round(i[2] * 1.212)  # 면적에 1.212 곱하면 수용인원

                i[2] = temp
            print("update_shelter_list", update_shelter_list)

            shelter_list = update_shelter_list.copy()

            dic_seq_path['shelter_id'] = shelter_list[self.path_flag][0]
            self.cur_available_refugee = shelter_list[self.path_flag][2]
            dic_seq_path['available_refugee'] = self.cur_available_refugee

            print("self.cur_available_refugee", self.cur_available_refugee)  # 대피소 인원
            print("self.total_number_of_refugee", self.total_number_of_refugee)  # 총 대피 인원

            self.total_number_of_refugee = self.total_number_of_refugee - self.cur_available_refugee
            print("self.total_number_of_refugee", self.total_number_of_refugee)  # 총 대피 인원

            print("dic_seq_path", dic_seq_path)

            first_shelter = shelter_list[self.path_flag][0]
            # 인접 cross_node 탐색
            shelter_adj_cross = self.to_cross_from_shelter(first_shelter)
            # print("shelter",shelter_adj_cross)

        start_node = self.search(start_ID)
        temp_adj_cross = []
        for i in shelter_adj_cross:
            ii = self.search(i)
            temp = self.node_l2_distance(start_node, ii)
            temp_tupple = {"nodeID": i, "distance": temp}
            temp_adj_cross.append(temp_tupple)
        temp_adj_cross = sorted(temp_adj_cross, key=lambda temp_adj_cross: (temp_adj_cross["distance"]), reverse=False)

        print("shelter_candidate: ", temp_adj_cross)

        end_node = self.search(temp_adj_cross[0]['nodeID'])

        # 2021.04.14 20시 주석
        print("start_node: ", start_node_info['adj_ID_node'], "end_node: ", end_node[0]["main_node_name"])

        close_list_final = self.path_finding(start_node, end_node)
        path = self.result_parsing(close_list_final)

        # 2021.05.03 확인용
        # print("path",path)

        final_path = self.from_id_to_xy(path)
        # print("final_path",final_path)

        dic_seq_path['path'] = final_path

        # 2021.05.03
        self.multi_path_list.append(dic_seq_path)
        print("multi_path_list", self.multi_path_list)
        # return path
        # return final_path
        return 0

    def update_de_duplicate(self):
        temp_openlist = self.open_list.copy()

        temp_id = 0
        temp_parent = 0
        temp_value = 0
        temp_id_list = []
        temp_parent_list = []
        temp_value_list = []

        new_list = []
        for i in temp_openlist:
            if i not in new_list:
                new_list.append(i)

        for node in new_list:
            for others in new_list:
                if node["adj_ID_node"] == others["adj_ID_node"] and node["parent_node"] != others["parent_node"] and \
                        node["f_value"] < others["f_value"]:
                    temp_id = others["adj_ID_node"]
                    temp_id_list.append(temp_id)
                    temp_parent = others["parent_node"]
                    temp_parent_list.append(temp_parent)
                    temp_value = others["f_value"]
                    temp_value_list.append(temp_value)
                elif node["adj_ID_node"] == others["adj_ID_node"] and node["parent_node"] != others["parent_node"] and \
                        node["f_value"] >= others["f_value"]:
                    temp_id = node["adj_ID_node"]
                    temp_id_list.append(temp_id)
                    temp_parent = node["parent_node"]
                    temp_parent_list.append(temp_parent)
                    temp_value = node["f_value"]
                    temp_value_list.append(temp_value)

                # temp_index = 0
                # for i in self.open_list:
                #     if i["adj_ID_node"] == temp_id and i["parent_node"] == temp_parent and i["f_value"] == temp_value:
                #         del self.open_list[temp_index]
                #     temp_index = temp_index + 1

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
                            #print("del") #2021.05.11 제대로 삭제가 안되나 중복이 남아있네
                            del new_list[index]
                        pass
                        index = index + 1
        return new_list
    """
    2021.05.03 문제 발견
    경로탐색 알고리즘 자체는 문제가 없는 것으로 확인
    결과 취합 단계의 오류
    9f1eec14a7 --> f8fd468be6 -> 26b81151ea --> fa70247fd6 --> cd23fd69a9 --> 5083f16879 --> f4cef0c516 --> 7f70a3633e
    --> 73f5fbf53e --> e61dad0b06 --> 6e95a74d52

    827aecdfff - 874fb2caa8 - 890348e133 - d9660d1094 - 9abb7aa60d - 51a838d4e1 - 9699c01b49 - c67d50c3d7 - 
    <여기도 문제 0d8d3f7738 타면 안댐> - 0dd100e638 - 43173c9f0d - 05527c600a - 
    a4219d7048 - 73f633db52 - 5083f16879 - cd23fd69a9 - fa70247fd6 - 26b81151ea - f8fd468be6 - 위쪽이 정상(여기가 문제 111b000b6e 타면안댐) - 
    9f1eec14a7 - b5cf91f24d - 91d2ee10a3 - 
    8fd8d5b11a - 1ee2331ac9 - 0397a89819 - 9b9448c77b - 64cede8234 - b3fc377006 - 5c8ff4dcde - 03be9162ca - 1e3d23eb97 - 
    0326197ad7 - e44ac9b28d - ef5007c2b5 - f52dca0bbb - 8e20b4d8ae - 023dd00b8c (역순)

    9f1eec14a7 - 111b000b6e - 1a2994f783 - c2604e43c2 (--> 방향)
    왜 얘가 마지막? {'adj_ID_node': '27a28f37d3', 'parent_node': '581cd6fbee', 'g_value': 349.0811594452879, 'h_value': 728.1688888724525, 'f_value': 1077.2500483177405, 'flag_var': True}]
    {'adj_ID_node': 'c2604e43c2', 'road_length': 58.139464590539895, 'parent_node': '1a2994f783', 'g_value': 0, 'h_value': 0.0, 'f_value': 0.0, 'flag_var': False}]
    {'adj_ID_node': '3b1baa3e30', 'road_length': 15.35313022951852, 'parent_node': '1a2994f783', 'g_value': 0, 'h_value': 38.55644170707723, 'f_value': 38.55644170707723, 'flag_var': False}
    """

    def result_parsing(self, close_list_final):

        print("close_list_final",close_list_final)
        final_path = []

        temp = close_list_final.copy()
        #print("temp",temp)
        pre_path_list = temp[-1].copy()
        # {'adj_ID_node': 'c2604e43c2', 'parent_node': '1a2994f783'

        final_path.append(pre_path_list[-1])
        # print("final_path",final_path)

        adj_ID_node = pre_path_list[-1]["adj_ID_node"]

        parent_node = pre_path_list[-1]["parent_node"]

        del pre_path_list[-1]

        # print("pre_path_list[::-1]", pre_path_list[::-1]) #2021.05.03 확인용

        for pre_path in pre_path_list[::-1]:
            # print("pre_path",pre_path)
            if pre_path["adj_ID_node"] == parent_node:
                # print("pre_path",pre_path["adj_ID_node"] )
                # print("parent_node",parent_node)
                final_path.append(pre_path)
                adj_ID_node = pre_path["adj_ID_node"]
                parent_node = pre_path["parent_node"]

                # print("adj_ID_node",adj_ID_node)
                # print("parent_node",parent_node)

        # start_node:  023dd00b8c end_node:  4897df8757  k0
        # start_node:  023dd00b8c end_node:  a8e1098a28 -a96801e563 k1
        """
        k2
        start_point_node 827aecdfff
        destination_node 0d6540876a
        """

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



