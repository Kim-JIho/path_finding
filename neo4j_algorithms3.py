from neo4j import GraphDatabase
import csv
import math
from haversine import haversine


class Neo4jHelper:
    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password), encrypted=False)
        self.rd_map = {}
        self.crs_map = {}
        self.load_property()
        self.open_list = []  # 검색해야하는 노드
        self.close_list = []  # 검색이 끝난 노드
        self.path = [] #사용 x

    def load_property(self):
        with open('C:/Users/m/Desktop/kisti재난대피/QGIS 개발/neo4j 핵심자료/Resource/TL_SPRD_CRS_WGS84.csv', 'r', encoding='utf-8') as crs_id:
            csvf = csv.DictReader(crs_id)
            for row in csvf:
                crs = dict(row)
                self.crs_map[crs['CRS_ID']] = crs


        #with open('C:\\Users\pkjoh\Desktop\Resource\dilpreprocessor\graph\data\TL_SPRD_RD_COMPLETE4.csv', 'r', encoding='utf-8') as rd_id:
        with open('C:/Users/m/Desktop/kisti재난대피/QGIS 개발/neo4j 핵심자료/Resource/TL_SPRD_RD.csv', 'r', encoding='utf-8') as rd_id:
            csvf = csv.DictReader(rd_id)
            for row in csvf:
                rd = dict(row)
                self.rd_map[rd['ID']] = rd

        print('Property Load Done')
    """
    준우추가
    """
    def close(self):
        self._driver.close()
    """
    준우추가
    """
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
                            edge_map[eid] = [None, None, None, None]
                        edge_map[eid][1] = float(self.get_length_of(eid))
                        edge_map[eid][2] = float(self.get_x_of(_id))
                        edge_map[eid][3] = float(self.get_y_of(_id))
                    # from connected road to other crs
                    if ed_set.issubset({'Cross'}) and st_set.issubset({'Road'}) and enode['ID'] != _id:
                        nid = snode['ID']
                        if edge_map.get(nid) is None:
                            edge_map[nid] = [None, None, None, None]
                        edge_map[nid][0] = enode['ID']

            for edge_id in edge_map.keys():
                adj_list.append(edge_map[edge_id])
            return sorted(adj_list, key=lambda x: x[1])
    """
    준우추가
    """
    @staticmethod
    def execute_query(tx, query):
        result = tx.run(query)
        record = result.single()
        if record is not None:
            return record[0]
        else:
            return None

    """
    return: generator
    """
    """
    준우추가
    """
    @staticmethod
    def execute_query_multi_result(tx, query):
        result = tx.run(query)
        record = result.records()
        if record is not None:
            return record

    #####################################################
    #CRS 정보

    def get_x_of(self, _crs_id):
        return float(self.crs_map[_crs_id]['xcoord'])

    def get_y_of(self, _crs_id):
        return float(self.crs_map[_crs_id]['ycoord'])

    #####################################################
    #RD 정보
    def get_length_of(self, _rd_id):
        return self.rd_map[_rd_id]['length']

    def get_rn_of(self, _rn_id):
        return self.rd_map[_rn_id]['RN']
    #####################################################

    """
     조회노드 및 인접노드 정보 가져옴
     main_node: ID / x / y
     adj_node: ID / main과의 거리 / x / y
    """
    def search(self, id):
        # 노드 정보 수집
        start_node = helper.retrieve_adj_node_from_cross(id)
        #불러오는 정보
        # 0번인덱스 : 인접노드 id
        # 1번인덱스 : 중심노드와 인접노드의 길이 (도로길이)
        # 2번인덱스 : 중심노드의 x좌표
        # 3번인덱스 : 중심노드의 y좌표

        # 추가사항
        # 인접노드의 좌표
        # 중심노드와 연결된 도로 노드 및 길이 정보
        # 대피소 노드 정보 조회
        node_list = [{"main_node_name":id,"main_node_x":start_node[0][2],"main_node_y":start_node[0][3]}]

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
    """
    준우추가
    """
    @classmethod
    def euclidean_distance(cls, sx, sy, ex, ey):
        return math.sqrt(math.pow(ex-sx, 2) + math.pow(ey-sy, 2))

    """
    위도 경도를 이용한 직선거리 계산 
    haversine 패키지
    """
    def haversine_euclidean_distance(cls, sx, sy, ex, ey):
        # print("sx,sy",sx,sy)
        # print("ex,ey",ex,ey)
        start=(sx,sy) # (위도,가로, 경도,세로)
        end=(ex,ey) # (위도,가로, 경도,세로)
        result= haversine(start, end)*1000
        return result

    def node_l2_distance(self, node_info_start, node_info_end): #중심노드와 목적지
        start_x = node_info_start[0]["main_node_x"]
        start_y = node_info_start[0]["main_node_y"]
        end_x = node_info_end[0]["main_node_x"]
        end_y = node_info_end[0]["main_node_y"]
        #return self.euclidean_distance(start_x, start_y, end_x, end_y)
        return self.haversine_euclidean_distance(start_x, start_y, end_x, end_y)

    def adj_euclidean_distance(self,node_info_start,node_info_end): #인접노드와 목적지
        each_node_distance=[]
        dis_dict = {"adj_ID_node": None, "destination_node_ID": None, "adj_distance": None}
        dis_dict["destination_node_ID"]=node_info_end[0]["main_node_name"]

        #각 인접노드와 목표노드와의 거리 계산
        for i in node_info_start[1:]:
            #print("i",i)
            temp_dict={"adj_ID_node":None,"adj_distance":None}
            start_node_ID = i["adj_ID_node"]
            temp_dict["adj_ID_node"]=start_node_ID
            end_node_ID = node_info_end[0]["main_node_name"]

            start_x = i["adj_node_x"]
            start_y = i["adj_node_y"]
            end_x = node_info_end[0]["main_node_x"]
            end_y = node_info_end[0]["main_node_y"]

            if (start_x != None) and (end_x != None) and (start_y != None) and (end_y != None):
                # subtract_x = end_x - start_x
                # subtract_y = end_y - start_y
                # EC_distance = math.sqrt(math.pow(subtract_x, 2) + math.pow(subtract_y, 2))
                # temp_dict["adj_distance"] = EC_distance

                temp_dict["adj_distance"] = self.haversine_euclidean_distance(start_y,start_x,end_y,end_x)
                each_node_distance.append(temp_dict)
            else:
                pass


        return each_node_distance
    """
    준우추가
    """
    def get_all_shelter(self):
        query = 'match (s:Shelter) return (s);'
        with self._driver.session() as session:
            result = session.write_transaction(self.execute_query_multi_result, query)
            return result
    """
    준우추가
    """
    def get_all_shelter_json(self):
        import json
        with open('C:/Users/m/Desktop/kisti재난대피/QGIS 개발/neo4j 핵심자료/Resource/shelter_rn_id.json', 'r', encoding='utf-8') as shelters:
            return json.loads(shelters.read(), encoding='utf-8')

    """
    상위 k개 대피소 가져옴(인접한 노드 순으로)
    준우추가
    """
    def retrieve_adj_shelter(self, crs_id, k):
        current_x = self.get_x_of(crs_id)
        current_y = self.get_y_of(crs_id)
        shelters = self.get_all_shelter_json()
        shelters_list = []
        for shelter in shelters:
            # print(shelter)
            #shelters_list.append([shelter['ID'], self.euclidean_distance(current_x, current_y, shelter['xcord'], shelter['ycord'])])
            shelters_list.append([shelter['ID'], self.haversine_euclidean_distance(current_x, current_y, shelter['xcord'], shelter['ycord'])])
        return sorted(shelters_list, key=lambda sh : sh[1])[:k]

    """
    여기서 업데이트하고 던져주고 그 다음 정렬해서 꺼내와야 함
    """
    def value_update(self,pre_open_list, pre_close_list):
        update_open_list = pre_open_list
        update_close_list = pre_close_list
        #print("update_open_list111111",update_open_list)
        for i in update_open_list:
            #print("iii", i["parent_node"])
            for j in update_close_list:
                #print("jjj", j["adj_ID_node"])
                if (i["parent_node"] == j["adj_ID_node"])and (i["flag_var"] == False):
                    print("-------update------")
                    i["g_value"] = i["g_value"] + j["g_value"]
                    i["f_value"] = i["g_value"] + i["h_value"]
                    i["flag_var"] = True
        print("update_open_list222222", update_open_list)

        """
        새로운 오픈리스트가 기존의 경로보다 짧을경우 오픈리스트에 넣고 아니면 오픈리스트를 그대로 둬야 함
        """
        return update_open_list


    def path_finding(self,node_info_start,node_info_end):
        #시작노드 node_info_start
        #종점노드 node_info_end
        start_point_node=node_info_start[0]["main_node_name"]
        destination_node= node_info_end[0]["main_node_name"]
        print("strat",node_info_start)
        print("end",node_info_end)

        # 두 노드 사이의 거리 계산 --> 실제 가진 length데이터와 유클리드 거리의 큰 차이가 나타나지 않음
        # 그냥 진행해도 상관없음
        #distance = helper.euclidean_distance(start_node, end_node)
        #print("중심노드와 도착노드의 거리:", distance)

        # 인접노드 거리 계산
        each_node_distance = self.adj_euclidean_distance(node_info_start, node_info_end)
        adj_search = self.search(start_point_node)
        # print("adj_search",adj_search)
        # print("각 인접노드와 도착노드와의 거리:", each_node_distance)

        for i in each_node_distance:
            for j in adj_search[1:]:
                if i["adj_ID_node"] == j["adj_ID_node"]:
                    i["road_length"] = j["road_length"]
                    i["parent_node"] = start_point_node
        print("adj_search", adj_search)
        print("각 인접노드와 도착노드와의 거리:", each_node_distance)

        #조회해서 opnelist에 붙이는 과정
        each_node_value= each_node_distance
        for i in each_node_value:
            i["g_value"]=0
            i["h_value"]=i["adj_distance"]
            i["f_value"] = i["g_value"] + i["h_value"]
            i["parent_node"] = node_info_start[0]["main_node_name"]
            del i["adj_distance"]
            i["flag_var"]=False

            #openlist에 붙이기
            if not self.close_list:
                self.open_list.append(i)
            elif self.close_list[-1]["parent_node"] != i["adj_ID_node"]:
                self.open_list.append(i)




        #print("each_node_value",each_node_value)
        self.open_list=sorted(self.open_list,key=lambda adj_dist:(adj_dist["h_value"]),reverse=True)

        #다음 노드가 바로 인접이면 끝
        for i in self.open_list[-1:]:
            print("pre_openlist",self.open_list)
            print("pre_closelist",self.close_list)

            # load_length--> g_value
            for k in self.open_list:
                if 'road_length' in k.keys():
                    k["g_value"]=k["road_length"]
                    del k["road_length"]
                    k["f_value"]=k["g_value"]+k["h_value"]

            self.open_list = sorted(self.open_list, key=lambda adj_dist: (adj_dist["f_value"]), reverse=True)
            #################################################
            """
            지금 만든애들 대상으로 붙여야 함
            기존 리스트를 새로운 변수에 copy
            새로운 copy 리스트 -> 밑에서 조건문 
            """
            #################################################
            print("pre2_openlist", self.open_list)
            print("pre2_closelist", self.close_list)

            """
            update
            이 부분에서 선택적으로 업데이트가 필요함... 방법...
            """
            # update_close_list = self.value_update(self.close_list)
            #self.open_list = [self.value_update(self.open_list,self.close_list)]
            hello_test = [self.value_update(self.open_list, self.close_list)]

            # 정렬을 f(x) 기준으로 필요함
            self.open_list = sorted(self.open_list, key=lambda adj_dist: (adj_dist["f_value"]), reverse=True)

            # 오픈리스트의 항목들 h(x)가 크면 새로운 노드로 변환 - 2020-08-11
            # for node in self.open_list:
            #     print("node",node)
            #     for others in self.open_list:
            #         if node["adj_ID_node"] == others["adj_ID_node"] and node["f_value"] < others["f_value"]:
            #             for del_node in self.open_list:
            #                 del del_node
            #         elif node["adj_ID_node"] == others["adj_ID_node"] and node["f_value"] >= others["f_value"]:

            #정렬한 openlist에서
            #f(x)가 가장 작은 값을 closelist에 pop
            #openlist에서 방금 꺼낸 값을 삭제하기
            temp_list=self.open_list[-1:].pop()
            close_node_name = temp_list["adj_ID_node"] # --> 재시작을 위해서 노드id저장하기
            del self.open_list[-1]
            self.close_list.append(temp_list)

            print("post_openlist",self.open_list)
            print("post_closelist",self.close_list)

            if i["adj_ID_node"] == destination_node:
                for j in node_info_start:
                    try:
                        if j["adj_ID_node"] == destination_node:
                            # i["g_value"] = j["road_length"]
                            # i["h_value"] = 0
                            # i["f_value"] = i["g_value"]+i["h_value"]

                            self.path.append(self.close_list)
                    except:
                        pass
            else:
                print("*****************")
                restart_node = self.search(close_node_name)
                print("restart_node",restart_node)
                self.path_finding(restart_node,node_info_end)

            return self.path

    def to_cross_from_shelter(self,_id):
        query = 'match(s: Shelter) where s.ID = "' + str(_id) + '" return (s) - [:Connection]-(:Road) - [: Connection]-(:Cross)'
        """
        이 부분 수정해야 함
        """
        with self._driver.session() as session:
            result = session.write_transaction(self.execute_query, query)
            adj_list = []
            for path in result:
                for rel in path.relationships:
                    snode = rel.nodes[0]
                    enode = rel.nodes[1]
                    st_set = set(snode.labels)
                    ed_set = set(enode.labels)

                    if ed_set.issubset({'Cross'}) :
                        adj_list.append(enode['ID'])

                    elif st_set.issubset({'Cross'}):
                        adj_list.append(snode['ID'])

            temp_list= set(adj_list)
            adj_list=[]
            for cross in temp_list:
                adj_list.append(cross)

            return adj_list

    def disaster_A_star(self,start_ID,disaster_code):
        # 지진상황 대피소 추출
        if disaster_code==1:
            shelter_list = []
            for sh in self.retrieve_adj_shelter('072fd6eee5', 5):
                shelter_list.append(sh)

            #가장 가까운 대피소 노드에서 인접한 cross 노드 추출
            first_shelter = shelter_list[0][0]
            shelter_adj_cross = self.to_cross_from_shelter(first_shelter)

        # 시작노드, 도착노드 선정
        start_node = self.search(start_ID)
        temp_adj_cross=[]
        for i in shelter_adj_cross:
            ii = self.search(i)
            temp = self.node_l2_distance(start_node,ii)
            temp_tupple={"nodeID":i, "distance":temp}
            temp_adj_cross.append(temp_tupple)
        temp_adj_cross = sorted(temp_adj_cross,key=lambda temp_adj_cross: (temp_adj_cross["distance"]),reverse=False)

        end_node = self.search(temp_adj_cross[0]['nodeID'])
        #end_node = self.search('b7f1907d7f')


        path = self.path_finding(start_node, end_node)
        print(path)


#현재 무한루프 돌고있음
#pre2_closelist [{'adj_ID_node': '6fcc8083d7', 'parent_node': '072fd6eee5', 'g_value': 7.827844438321279, 'h_value': 722.9935487595001, 'f_value': 730.8213931978214, 'flag_var': False}, {'adj_ID_node': '9597610a3c', 'parent_node': '6fcc8083d7', 'g_value': 26.353338951237703, 'h_value': 704.9301346504005, 'f_value': 731.2834736016382, 'flag_var': True}, {'adj_ID_node': 'b7f1907d7f', 'parent_node': '9597610a3c', 'g_value': 68.28846943339117, 'h_value': 662.7918016582996, 'f_value': 731.0802710916907, 'flag_var': True}, {'adj_ID_node': '6a83334252', 'parent_node': 'b7f1907d7f', 'g_value': 71.05835563779226, 'h_value': 659.7854279573796, 'f_value': 730.8437835951719, 'flag_var': True}, {'adj_ID_node': 'cc2b1c6777', 'parent_node': '6a83334252', 'g_value': 96.99261777197398, 'h_value': 633.7060402312245, 'f_value': 730.6986580031985, 'flag_var': True}, {'adj_ID_node': '2c2bde8e2b', 'parent_node': 'cc2b1c6777', 'g_value': 108.72659833716341, 'h_value': 622.6375237400423, 'f_value': 731.3641220772057, 'flag_var': True}]

if __name__ == '__main__':
    #객체 생성
    helper = Neo4jHelper('bolt://165.194.27.127:7687', user='neo4j', password='1234')
    #helper.retrieve_adj_shelter('072fd6eee5', 5)

    # 여기에서 나온 쉘터의 id -> 근처 도로와 크로스 노드 조회 -> 크로스 노드 id와 출발점 거리 중 가까운 것을 택하여 도착지점으로 선정

    #노드 조회
    #start_node=helper.search('072fd6eee5')
    #start_node = helper.search('6fcc8083d7')
    #end_node = helper.search('023dd00b8c')
    #end_node=helper.search('8e20b4d8ae') -> 무한루프
    #end_node = helper.search('6fcc8083d7')
    #end_node = helper.search('9597610a3c')
    #end_node = helper.search('b7f1907d7f')
    #path=helper.path_finding(start_node,end_node)
    #print(path)

    #지진 코드 1
    helper.disaster_A_star('072fd6eee5',1)

    #test
    # start_node=helper.search('072fd6eee5')
    # end_node = helper.search('69955b0043')
    # path=helper.path_finding(start_node,end_node)
    # print(path)

    helper.close()


