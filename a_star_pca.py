
# Библиотеки
import numpy as np
import lake_logic
import csv
import time

# Переменные
step = None
step_diag = None
const_er = None
matrix = None
size_searche = None

# Функция для получения пепременных
def take_info(matrix_file, step_i, const):
    global step, step_diag, const_er, matrix, size_searche
    step = step_i
    matrix = matrix_file
    step_diag = (step**2 + step**2)**0.5
    const_er = const
    size_searche = int(len(matrix)//4)
    return print(step, step_diag, const_er)

# эвристика для А*
def heuristic(c_a, c_b):
    return abs(c_a[0] - c_b[0]) + abs(c_a[1] - c_b[1])

# Нахожедние соседей у алгоритма А*
def neighbour_graph(coor):
    y, x = coor
    all_neighbour = [(y-1, x-1), (y, x-1),
                    (y-1, x+1), (y-1, x),
                    (y+1, x), (y+1, x+1),
                    (y, x+1), (y+1, x-1)]
             
    return [
        (ny, nx) for ny, nx in all_neighbour
        if 0 <= nx < len(matrix[0]) and 0 <= ny < len(matrix)]

# Стоимость вершины
def cost(a, b):
    dy = abs(b[0] - a[0])
    dx = abs(b[1] - a[1])
    base = step_diag if dx > 0 and dy > 0 else step
    return base * const_er if matrix[b[0]][b[1]] == 1 else base

# Алгоритм А*
def a_star(a, b):
    start_time = time.time()
    open_set = [(0 + heuristic(a, b), 0, a)]  # (f, g, point)
    close_set = set()
    parent = {}
    
    while open_set:
        open_set.sort()
        f_current, g_current, current = open_set.pop(0)
        
        if current == b:
            break

        close_set.add(current)
        
        # Если текущая точка - вода, применяем PCA
        if matrix[current[0]][current[1]] == 1:
            direction = adaptive_PCA(matrix, current,min_water_points=size_searche)
            if direction is not None:
                # Находим перпендикулярное направление
                perp_direction = np.array([-direction[1], direction[0]])
                perp_direction = perp_direction / np.linalg.norm(perp_direction)
                
                # Пробуем двигаться в обоих перпендикулярных направлениях
                for sign in [1, -1]:
                    next_point = (current[0] + int(round(sign * perp_direction[1])), 
                                  current[1] + int(round(sign * perp_direction[0])))
                    
                    if (0 <= next_point[0] < len(matrix)) and \
                       (0 <= next_point[1] < len(matrix[0])) and \
                       next_point not in close_set:
                        
                        tentative_g = g_current + cost(current, next_point)
                        open_set.append((tentative_g + heuristic(next_point, b), tentative_g, next_point))
                        parent[next_point] = current
        
        for neighbor in neighbour_graph(current):
            if neighbor in close_set:
                continue
                
            tentative_g = g_current + cost(current, neighbor)
            
            in_open = False
            for i, (f, g, p) in enumerate(open_set):
                if p == neighbor:
                    in_open = True
                    if tentative_g < g:
                        open_set[i] = (tentative_g + heuristic(neighbor, b), tentative_g, neighbor)
                        parent[neighbor] = current
                    break
                    
            if not in_open:
                open_set.append((tentative_g + heuristic(neighbor, b), tentative_g, neighbor))
                parent[neighbor] = current
    
    # Восстановление пути
    path = []
    current = b
    while current in parent:
        path.append(current)
        current = parent[current]
    path.append(a)
    path.reverse()
    
    if len(path) == 1:  # Если путь не найден
        return [], float('inf'), []
    
    total_cost = sum(cost(path[i], path[i+1]) for i in range(len(path)-1))
    adj_matrix(open_set,close_set)
    end_time = time.time()
    execution_time = end_time - start_time
   

    return path, total_cost, open_set, execution_time

# Алгоритм РСА
def adaptive_PCA(all_map, coor, min_window=3, max_window=10, min_water_points=5):
    current_window = min_window

    if min_water_points < 5:
        min_water_points = 5
    
    while current_window <= max_window:
        y_start = max(0, coor[0] - current_window // 2)
        y_end = min(all_map.shape[0], coor[0] + current_window // 2 + 1)
        x_start = max(0, coor[1] - current_window // 2)
        x_end = min(all_map.shape[1], coor[1] + current_window // 2 + 1)
        
        piece = all_map[y_start:y_end, x_start:x_end]
        rows, cols = np.where(piece == 1)
        num_water_points = len(rows)
        
        if num_water_points >= min_water_points:
            water_piece = np.column_stack((cols, rows))
            centered = water_piece - water_piece.mean(axis=0)
            
            if np.linalg.matrix_rank(centered) < 2:
                current_window += 2
                continue
                
            cov = np.cov(centered.T)
            eigenvals, eigenvecs = np.linalg.eig(cov)
            
            # Возвращаем главную компоненту
            return eigenvecs[:, np.argmax(eigenvals)]
        
        current_window += 2
    
    return None

# Запись матрицы смежности в csv файл
def adj_matrix(open_n, close_n):
    all_coor = []
    for o in open_n:
        all_coor.append(o[2])
    for c in close_n:
        all_coor.append(c)
    all_coor = sorted(list(set(all_coor)))
    
    # Матрицу смежности
    adj = {coord: {} for coord in all_coor}
    
    # Заполняем связи только для соседей
    for coord in all_coor:
        y, x = coord
        neighbors = neighbour_graph((y, x))
        for neighbor in neighbors:
            if neighbor in adj:
                adj[coord][neighbor] = 1
    
    # Записываем в CSV
    with open('adjacency_matrix.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=';')
        header = [""] + [f"{y},{x}" for (y, x) in all_coor]
        writer.writerow(header)
        
        for coord in all_coor:
            row = [f"{coord[0]},{coord[1]}"] + [adj[coord].get(other_coord, 0) for other_coord in all_coor]
            writer.writerow(row)


