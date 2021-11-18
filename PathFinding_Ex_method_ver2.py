from neo4j import GraphDatabase
import csv
import math
from haversine import haversine


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
        with open('TL_SPRD_CRS_WGS84_v1.csv', 'r',
                  encoding='utf-8') as crs_id:
            csvf = csv.DictReader(crs_id)
            for row in csvf:
                crs = dict(row)
                self.crs_map[crs['CRS_ID']] = crs

        with open('TL_SPRD_CRS_WGS84_v1.csv', 'r',
                  encoding='utf-8') as xy:
            csvf = csv.DictReader(xy)
            for row in csvf:
                xy = dict(row)
                self.xy_map[xy['xcoord'], xy['ycoord']] = xy

        with open('TL_SPRD_RD_v1.csv', 'r',
                  encoding='utf-8') as rd_id:
            csvf = csv.DictReader(rd_id)
            for row in csvf:
                rd = dict(row)
                self.rd_map[rd['ID']] = rd

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

                        if self.get_rk1_of(eid) != '':
                            edge_map[eid][4] = str(self.get_rk1_of(eid))


                        if self.get_rk2_of(eid) != '':
                            edge_map[eid][5] = str(self.get_rk2_of(eid))

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

    def get_rk1_of(self, _rn_id):
        return self.rd_map[_rn_id]['RISK_TYPE_1']

    def get_rk2_of(self, _rn_id):
        return self.rd_map[_rn_id]['RISK_TYPE_2']


    def search(self, id):
        start_node = self.retrieve_adj_node_from_cross(id)
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


            if (start_x != None) and (end_x != None) and (start_y != None) and (end_y != None):
                #weight value
                #if (risk_cd_1 == '2') or (risk_cd_2 == '2'): #여기서 가중치 조절
                if (risk_cd_1 == '5') or (risk_cd_2 == '5'): #여기서 가중치 조절
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
        with open('shelter_rn_id.json', 'r', encoding='utf-8') as shelters:
            return json.loads(shelters.read(), encoding='utf-8')

    def retrieve_adj_shelter(self, crs_id, k):
        current_x = self.get_x_of(crs_id)
        current_y = self.get_y_of(crs_id)
        shelters = self.get_all_shelter_json()
        shelters_list = []
        for shelter in shelters:
            shelters_list.append([shelter['ID'],
                                  self.haversine_euclidean_distance(current_y, current_x, shelter['ycord'],
                                                                    shelter['xcord']), shelter['fclty_ar']])

        return sorted(shelters_list, key=lambda sh: sh[1])[:k]

    def value_update(self, pre_open_list, pre_close_list): #flag_update
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
        risk_cd_1 = 0

        adj_search = self.search(start_point_node)


        risk_cd_1=adj_search[0]['main_node_risk1']
        risk_cd_2=adj_search[0]['main_node_risk2']


        each_node_distance = self.adj_euclidean_distance(node_info_start, node_info_end,risk_cd_1,risk_cd_2)

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

        self.open_list = sorted(self.open_list, key=lambda adj_dist: (adj_dist["f_value"]), reverse=True) #2021.05.12


        for i in self.open_list[-1:]:
            for k in self.open_list:
                if 'road_length' in k.keys():
                    k["g_value"] = k["road_length"]
                    del k["road_length"]
                    k["f_value"] = k["g_value"] + k["h_value"]


            self.open_list = sorted(self.open_list, key=lambda adj_dist: (adj_dist["f_value"]), reverse=True)

            self.value_update(self.open_list, self.close_list)

            self.open_list = sorted(self.open_list, key=lambda adj_dist: (adj_dist["f_value"]), reverse=True)

            up_ip_list = self.update_de_duplicate()
            self.open_list = up_ip_list

            self.open_list = sorted(self.open_list, key=lambda adj_dist: (adj_dist["f_value"]), reverse=True)


            temp_list = self.open_list[-1:].pop()


            close_node_name = temp_list["adj_ID_node"]
            del self.open_list[-1]  # pop으로 꺼내온 마지막 f가 가장 낮은 노드를 삭제

            if i["adj_ID_node"] == destination_node:
                for j in node_info_start:

                    try:
                        if j["adj_ID_node"] == destination_node:

                            self.close_list.append(i)
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

    def Shelter_disaster_A_star(self, x, y, disaster_code):

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

        end_node = self.search(temp_adj_cross[0]['nodeID'])

        close_list_final = self.path_finding(start_node, end_node)
        path = self.result_parsing(close_list_final)
        final_path = self.from_id_to_xy(path)

        return final_path


    def disaster_A_star(self, s_x, s_y,d_x,d_y, disaster_code):

        start_ID = self.get_ID_of(s_x, s_y)
        start_node_info = {'adj_ID_node': start_ID, 'parent_node': None, 'g_value': 0, 'h_value': 0, 'f_value': 0,
                           'flag_var': False}

        self.close_list.append(start_node_info)
        start_node = self.search(start_ID)

        destination_ID = self.get_ID_of(d_x, d_y)
        destination_node_info = {'adj_ID_node': destination_ID, 'parent_node': None, 'g_value': 0, 'h_value': 0, 'f_value': 0,
                           'flag_var': False}

        self.close_list.append(destination_node_info)
        end_node = self.search(destination_ID)

        close_list_final = self.path_finding(start_node, end_node)
        path = self.result_parsing(close_list_final)
        final_path = self.from_id_to_xy(path)

        return final_path

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



                for tp in range(len(temp_id_list)):
                    index = 0
                    for i in new_list:

                        if i["adj_ID_node"] == temp_id_list[tp] and i["parent_node"] == temp_parent_list[tp] and i[
                            "f_value"] == temp_value_list[tp]:
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



