# import neo4j_algorithms3 as pf
# import path_finding as pf
import standard_pathfinding_method_ver2 as pf
import time

import sys

"""
2021.04.08
메인함수
경로탐색 알고리즘
"""

"""
2021.05.07
경로탐색에서 붙여넣는 부분 수정 : 해결
현재 거리 계산 문제 추정
엮기 문제 추정 
"""

if __name__ == '__main__':
    start_time = time.time()
    # 객체 생성
    # time 5 : 90.00748085975647
    # time 20 : 369.99176263809204
    # time 1,000:

    #A_star = pf.Neo4jHelper('bolt://165.194.27.127:7687', user='neo4j', password='1234')
    #A_star = pf.Neo4jHelper('bolt://13.209.69.92:7687', user='+', password='1q2w3e4r@')

    A_star = pf.Neo4jHelper('bolt://13.209.69.92:7687', user='dilab', password='1q2w3e4r@')
    #A_star = pf.Neo4jHelper('bolt://13.209.69.92:7687', user='disasterDB', password='1q2w3e4r@')
    # helper.retrieve_adj_shelter('072fd6eee5', 5)

    # 여기에서 나온 쉘터의 id -> 근처 도로와 크로스 노드 조회 -> 크로스 노드 id와 출발점 거리 중 가까운 것을 택하여 도착지점으로 선정

    # 노드 조회
    # start_node=helper.search('072fd6eee5')
    # start_node = helper.search('6fcc8083d7')
    # end_node = helper.search('023dd00b8c')
    # end_node=helper.search('8e20b4d8ae') -> 무한루프
    # end_node = helper.search('6fcc8083d7')
    # end_node = helper.search('9597610a3c')
    # end_node = helper.search('b7f1907d7f')
    # path=helper.path_finding(start_node,end_node)
    # print(path)

    # 지진 코드 1
    # path_result = A_star.disaster_A_star('023dd00b8c',1)
    # print(path_result)

    # 지진코드 1 , 경도 위도 사용
    # path_result = A_star.disaster_A_star('129.07428826981172','35.13797209189209', 1)

    # 2021.04.14 밤8시 주석처리 ###############################################
    # print(path_result)

    # print(A_star.get_x_of('023dd00b8c'))
    # print(A_star.get_ID_of('129.07428826981172','35.13797209189209')) #129.074288269812-xlsx
    # test
    """
    start_node:  023dd00b8c end_node:  4897df8757 경로 마지막: d2e983d530 (마지막 노드와 연결되어 있음)
    start_node:  023dd00b8c end_node:  a8e1098a28 경로 마지막: a96801e563 (마지막 노드와 연결되어 있음)
    start_node:  023dd00b8c end_node:  0d6540876a 경로 마지막: 827aecdfff (마지막 노드와 연결되어 있음)
    start_node:  023dd00b8c end_node:  88757a837f 경로 마지막: b006a80174 (마지막 노드와 연결되어 있음)
    start_node:  023dd00b8c end_node:  e5b110fffa 경로 마지막: b6feeef3d1 (마지막 노드와 연결되어 있음) 
    ---> 클로즈 리스트는 이제 문제가 없다 21.05.04 밤 8시 23분
    2021.05.04 밤 8시 결론
    path_finding 함수는 close_list.append가 else에 붙도록 수정하였고 이게 맞는듯
    multi에서 안되는건 엮는게 문제같음
    즉, result_parsing 함수 문제인듯
    """
    # multi의 경우
    # path_flag = 0 --> start_node:  023dd00b8c end_node:  4897df8757 경로 마지막: 4897df8757 (일치)
    # path_flag = 1 --> start_node:  023dd00b8c end_node:  a8e1098a28 경로 마지막: a96801e563 (마지막 노드와 연결되어 있음)
    # path_flag = 2 --> start_node:  023dd00b8c end_node:  0d6540876a 경로 마지막: c2604e43c2 (실패, 엉뚱한 곳)
    # path_flag = 3 --> start_node:  023dd00b8c end_node:  88757a837f 경로 마지막: 88757a837f (일치)
    # path_flag = 4 --> start_node:  023dd00b8c end_node:  e5b110fffa 경로 마지막: fbed0fc93b (엉뚱한 곳)
    #start_node=A_star.search('023dd00b8c') #basic - 18e4ac64ee : 문제
    #start_node=A_star.search('a67198e2b8') #우암동 재난코드
    #start_node = A_star.search('fded2a84d0') #2021.05.10 -분할 테스트
    #start_node = A_star.search('e13a5c334a')
    #end_node = A_star.search('4897df8757')
    # end_node = A_star.search('e5b110fffa')
    #end_node = A_star.search('4774290076') #basic
    #end_node = A_star.search('0d6540876a') #2021.05.12 오류 발견 close list가 안나옴 -> i=temp_list 주석처리 및 h->f로 수정
    #end_node = A_star.search('18e4ac64ee')  #이 노드를 목표로 할 때 안나옴 뭐가 문제지?
    #end_node = A_star.search('f9eeb67eae')  #우암동 재난코드

    """
    2021.06.04
    실험을 위한 경로 테스트
    """
    start_node=A_star.search('2fc8284145')
    end_node = A_star.search('deb1b740b5')
    """
    2fc8284145
35.217450259856165, 129.009012769615651
6f8d89812b
35.239367967767969, 129.014089274760380

    """

    ########

    #end_node = A_star.search('4f6aa29d62') #2021.05.10 분할 테스트 / 수정- 중복제거업데이트 부분
    # 수정전: 26초(중복있음)  수정후: 20초 /2차수정: 19.57

    #start_node = A_star.search('023dd00b8c')
    #end_node = A_star.search('b74a798e23') --> ok 결과 나옴

    #start_node = A_star.search('b74a798e23')
    #end_node = A_star.search('18e4ac64ee') #--> 결과 안나옴 반복노드: a58d232c89 2021.05.11 중복노드 삭제가 안돼 ㅠ

    # start_node = A_star.search('b74a798e23')
    # end_node = A_star.search('dc294429cb')  # --> 결과 안나옴 ee446ac7dc
    """
    {'adj_ID_node': '88b4b28af9', 'road_length': 9.700373813903775, 'parent_node': 'a58d232c89', 'g_value': 0, 'h_value': 1047.517409442316, 'f_value': 1047.517409442316, 'flag_var': False}
    {'adj_ID_node': '88b4b28af9', 'parent_node': 'a58d232c89', 'g_value': 39.00348761186162, 'h_value': 1047.517409442316, 'f_value': 1086.5208970541776, 'flag_var': True
    2021.05.10
    엑셀로 중복값을 뽑아보니, start node가 중복되서 나타난다. 이것은 오픈리스트에 중복으로 들어가서 가져와서 꺼내서
    새롭게 스타트로 지정하고 해서 나오는 문제 같음. 
    """
    """
    start_point_node 1a3ef8d389
    destination_node 18e4ac64ee
    마지막이 이렇게 나옴
    """
    #start_node = A_star.search('b74a798e23')
    #end_node = A_star.search('c37de81199') #--> ok 결과 나옴
    #start_node = A_star.search('c37de81199')
    #end_node = A_star.search('18e4ac64ee') #--> ok 결과 나옴

    #start_node = A_star.search('b74a798e23')
    #end_node = A_star.search('1a3ef8d389')  # --> ok 결과 나옴

    #start_node = A_star.search('1a3ef8d389')
    #end_node = A_star.search('18e4ac64ee')  # --> ok 결과 나옴

    """
    each_node_distance [{'adj_ID_node': '072fd6eee5', 'adj_distance': 1681.1317897490133}, {'adj_ID_node': 'd2bb5fc5e7', 'adj_distance': 1652.5923544574357}, 
    {'adj_ID_node': '8e20b4d8ae', 'adj_distance': 1651.1931646812752}]
    
    shelter_candidate:   [{'nodeID': '18e4ac64ee', 'distance': 1196.8226918944483}, --> 문제네? 1681...이 나와야함
     {'nodeID': '55f2842a2b', 'distance': 1225.2091943246955}]
    start_node:  023dd00b8c end_node:  18e4ac64ee
    
    start_point_node 1a2994f783
    destination_node c2604e43c2

    3b1baa3e30
    111b000b6e
    c2604e43c2
    """
    # start_node_info = {'adj_ID_node': '4897df8757', 'parent_node': None, 'g_value':0, 'h_value':0, 'f_value':0, 'flag_var': False}
    # print("start_node_info", start_node_info)
    # A_star.close_list.append(start_node_info)
    #
    close_list_final = A_star.path_finding(start_node, end_node)
    # sys.stdout = open('C:/Users/m/Desktop/kisti재난대피/2차년도/test.txt','w')
    #print(path)
    path = A_star.result_parsing(close_list_final)
    final_path = A_star.from_id_to_xy(path)
    """
    2021.06.06 가중치 변경했을 때 self.rd_map[_rd_id]['length'] 부분 오류남
    
    """
    print("final_path: ",final_path)
    # sys.stdout.close()
    A_star.close()
    print("time: ", time.time() - start_time)