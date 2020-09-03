
A_star = pf.Neo4jHelper('bolt://13.209.69.92:7687', user='dilab', password='1q2w3e4r@')
현재 임시로 구성한 클라우드 서버입니다. 곧 다른 서버로 업데이트 할 예정입니다.


path_result = A_star.disaster_A_star('129.07428826981172','35.13797209189209', 1)
disater_A_star('경도', '위도', 1)
parameter 1: 경도
parameter 2: 위도
parameter 3: 재난코드 
현재 재난 코드 지진 코드인 1번만 사용가능합니다.


