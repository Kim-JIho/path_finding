#import neo4j_algorithms3 as pf
#import path_finding as pf
import multipath_method_ver2 as pf
import time
"""
2021.04.08
메인함수
경로탐색 알고리즘
"""

"""
2021.04.28
수용인원 추가
"""

if __name__ == '__main__':

    start_time=time.time()
    #객체 생성
    #time 5 : 90.00748085975647
    #time 20 : 369.99176263809204
    #time 1,000:
    #for i in range(5):
    A_star = pf.Neo4jHelper('bolt://165.194.27.127:7687', user='neo4j', password='1234')
    #A_star = pf.Neo4jHelper('bolt://13.209.69.92:7687', user='dilab', password='1q2w3e4r@')

    #A_star = pf.Neo4jHelper('bolt://13.209.69.92:7687', user='dilab', password='1q2w3e4r@')
    #helper.retrieve_adj_shelter('0 72fd6eee5', 5)

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
    # path_result = A_star.disaster_A_star('023dd00b8c',1)
    # print(path_result)


    #지진코드 1 , 경도 위도 사용
    #path_result = A_star.disaster_A_star('129.07428826981172','35.13797209189209', 1)
    #path_result = A_star.disaster_A_star('129.07428826981172','35.13797209189209', 1,50000) #수용인원추가
    #path_result = A_star.multi_path('129.07428826981172','35.13797209189209', 2,100) #2는 붕괴(지진)
    path_result = A_star.multi_path('129.088152081205','35.142001652285359', 2,100) #2는 붕괴(지진) #2021.06.04

    path_result = A_star.multi_path('129.088152081205','35.142001652285359', 2)

    """
    2021.05.06
    dic_seq_path {'shelter_id': '7d839f7dc81b9bd60d966d39762449b7', 'available_refugee': 3072}
    shelter_candidate:   [{'nodeID': '18e4ac64ee', 'distance': 1196.8226918944483}, {'nodeID': '55f2842a2b', 'distance': 1225.2091943246955}]
    k=6의 경우를 제대로 못찾고 거리가 이상한 것으로 추정됨(4시50분 경로 탐색 결과 안나옴)
    """
        # 2021.04.14 밤8시 주석처리 ###############################################
    print(path_result)

    # print(A_star.get_x_of('023dd00b8c'))
    # print(A_star.get_ID_of('129.07428826981172','35.13797209189209')) #129.074288269812-xlsx
    #test
    # start_node=A_star.search('023dd00b8c')
    # end_node = A_star.search('4897df8757')
    #
    # start_node_info = {'adj_ID_node': '4897df8757', 'parent_node': None, 'g_value':0, 'h_value':0, 'f_value':0, 'flag_var': False}
    # print("start_node_info", start_node_info)
    # A_star.close_list.append(start_node_info)
    #
    # path=A_star.path_finding(start_node,end_node)
    # print(path)

    A_star.close()
    print("time: ",time.time() - start_time)


    """
    2021.05.03
    다중 경로 
    af7a38d85a745685535db9560caa02e6 4897df8757 4897df8757
    af6fb05ee506e3517184a2fc5db32b17 a8e1098a28 a96801e563
    c585ff09fd826bfed7cc173cb758cda4 0d6540876a c2604e43c2
    """