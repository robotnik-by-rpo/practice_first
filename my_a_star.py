import igraph as ig
import numpy as np
import lake_logic
import heapq

# Переменные 
RESULT_WAY = 0
FLAG_WATER = False
STEP = lake_logic.get_step()
STEP_DIAG = (STEP**2 + STEP**2)**0.5
MATRIX = lake_logic.get_matrix()
DOT_A = lake_logic.get_a()
DOT_B = lake_logic.get_b()

# Алгоритм PCA

# Алгоритм A*

# Функция для нахождения соседей
def near_neighboor(coor):
    all_neighbour = []

    all_neighbour.append((coor[1]+1, coor[0]-1))
    all_neighbour.append((coor[1]+1, coor[0]))
    all_neighbour.append((coor[1]+1, coor[0]+1))
    all_neighbour.append((coor[1], coor[0]-1))
    all_neighbour.append((coor[1], coor[0]+1))
    all_neighbour.append((coor[1]-1, coor[0]-1))
    all_neighbour.append((coor[1]-1, coor[0]))
    all_neighbour.append((coor[1]-1, coor[0]+1))

    return tuple(all_neighbour)

def A_STAR():
    temp_dot = DOT_A
    temp_way = 0
    while temp_dot != DOT_B:
        np_array = np.zeros(8,dtype= np.float64)
        neightbours = near_neighboor(temp_dot)
        for idx,n in enumerate(temp_dot):
            temp_n = (abs(DOT_B[1] - n[1]),abs(DOT_B[0]-n[0]))
            sum_dot = (temp_n[0]+temp_n[1])*10
            
            if idx in [0,2,5,7]:
                sum_dot += STEP_DIAG
            else:
                sum_dot += STEP
            np_array[idx] = sum_dot

        min_index = np.argmin(np_array)        
        temp_dot = neightbours[min_index]


        