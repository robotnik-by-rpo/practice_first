# Подключение всех библиотек
import numpy as np
import csv


# Модуль с основной логикой работы программы

# Переменные 
_CONST_COOR_A = ()
_CONST_COOR_B = ()
_NP_MATRIX = None
_STEP = 0

# Функции 

# Получает шаг сетки и кол-во координат по х и y
def process_data(filename):
    with open(filename,'r',encoding="utf8") as file:
        read_csv = csv.reader(file)
        data = list(read_csv)
        low_row_x = float(data[0][0])
        low_row_y = float(data[-1][1])
        max_row_x = float(data[-1][0])
        max_row_y = float(data[0][1])
        amount_x = max_row_x - low_row_x
        amount_y = max_row_y - low_row_y
        for idx,d in enumerate(data):
            if low_row_x != float(d[0]):
                step_x = float(d[0]) - float(data[idx-1][0])
                break
    # Возвращаем шаг сетки
    _NP_MATRIX = step_x
    return (step_x,int(amount_y/step_x)+1,int(amount_x/step_x)+1)

"""Создает транспонированную numpy матрицу, где 0 - это земля, а 1 - это вода"""
def create_np_mas(row_f, col_f,filename):
    
    row = int(row_f)
    col = int(col_f)
    with open(filename,'r',encoding="utf8") as file:
        read_csv = csv.reader(file)
        data = list(read_csv)
        res_matrix = np.zeros((row,col), dtype = np.int8)
        for y in range(row):
            for x in range(col):
                index_file = y*col + x
                if index_file < len(data):
                    res_matrix[y, x] = int(data[index_file][2])
        for row in res_matrix:
            row = row[::-1]

    result = res_matrix.T
    _NP_MATRIX = result
    return result

