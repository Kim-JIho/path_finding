import PathFinding_Ex_method_ver1 as pf
import time


if __name__ == '__main__':
    start_time = time.time()
    A_star = pf.Neo4jHelper('bolt://13.124.229.145:7687', user='dilab', password='1q2w3e4r@')

    #case 1
    path_result = A_star.disaster_A_star('129.008956','35.21675673', '129.0116131', '35.23976858', 5)
    print(path_result)

    #case 2
    #path_result = A_star.Shelter_disaster_A_star('129.008956','35.21675673', 1)
    #print(path_result)


    A_star.close()
    print("time: ", time.time() - start_time)


