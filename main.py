import path_finding as pf
"""
path_finding using Astar ver1.0
"""

if __name__ == '__main__':
    A_star = pf.Neo4jHelper('bolt://13.209.69.92:7687', user='dilab', password='1q2w3e4r@')
    path_result = A_star.disaster_A_star('129.07428826981172','35.13797209189209', 1)
    print(path_result)
    A_star.close()