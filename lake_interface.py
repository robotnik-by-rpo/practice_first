
# Подключение библиотек
from tkinter import *
from tkinter import messagebox
import a_star_pca
import lake_logic
from tkinter import ttk
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

# Модуль интерфейс для программы

# Переменные от пользователя 
CONST_VAL = None
CONST_FILE = None
CONST_GRID = ()
CONST_DOT = []

# Класс с интерфейсом второго окна

class FullScrollableMatrix:
    def __init__(self, root, matrix=None, total_blocks=50, block_size_px=5):
        self.root = root
        self.total_blocks = total_blocks
        self.block_size_px = block_size_px
        self.locked = False
        
        # Размер всего поля в пикселях
        self.total_px = total_blocks * block_size_px
        
        # Матрица блоков (0 - белый, 1 - синий, 2 - красный)
        if matrix is None:
            self.matrix = np.zeros((total_blocks, total_blocks), dtype=np.int8)
        else:
            self.matrix = matrix.astype(np.int8)
            self.total_blocks = max(matrix.shape[0], matrix.shape[1])

        # Создаем главный фрейм с прокруткой
        self.main_frame = Frame(root)
        self.main_frame.pack(fill=BOTH, expand=True)
        
        # Холст и полосы прокрутки
        self.canvas = Canvas(self.main_frame)
        self.h_scroll = ttk.Scrollbar(self.main_frame, orient="horizontal", command=self.canvas.xview)
        self.v_scroll = ttk.Scrollbar(self.main_frame, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=self.h_scroll.set, yscrollcommand=self.v_scroll.set)
        
        self.h_scroll.pack(side=BOTTOM, fill=X)
        self.v_scroll.pack(side=RIGHT, fill=Y)
        self.canvas.pack(side=LEFT, fill=BOTH, expand=True)
        
        # Фрейм для содержимого
        self.content_frame = Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.content_frame, anchor="nw")
        
        # Настройка matplotlib
        self.fig, self.ax = plt.subplots(figsize=(self.total_px/100, self.total_px/100), dpi=100)
        self.fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
        
        # Устанавливаем границы (ось Y направлена вниз)
        self.ax.set_xlim(0, self.total_blocks)
        self.ax.set_ylim(self.total_blocks, 0)
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.ax.set_aspect('equal')
        
        # Сетка
        self.ax.set_xticks(np.arange(0, self.total_blocks + 1, 1), minor=True)
        self.ax.set_yticks(np.arange(0, self.total_blocks + 1, 1), minor=True)
        self.ax.grid(which='minor', color='black', linestyle='-', linewidth=0.2)
        
        # Цветовая карта: 0 - белый, 1 - синий, 2 - красный
        self.cmap = ListedColormap(['white', 'blue', 'red'])
        
        # Инициализация отображения (транспонируем матрицу для правильной ориентации)
        self.display_matrix = self.matrix.copy()
        self.img = self.ax.imshow(
            self.display_matrix, 
            cmap=self.cmap, 
            vmin=0, 
            vmax=2,
            extent=[0, self.total_blocks, self.total_blocks, 0],  # Инвертируем Y
            interpolation='none',
            origin='upper'  # Начало координат в верхнем левом углу
        )
        
        # Встраиваем matplotlib
        self.mpl_canvas = FigureCanvasTkAgg(self.fig, master=self.content_frame)
        self.mpl_widget = self.mpl_canvas.get_tk_widget()
        self.mpl_widget.pack(fill=BOTH, expand=True)
        
        # Привязываем события
        self.mpl_canvas.mpl_connect('button_press_event', self.on_click)
        self.content_frame.update_idletasks()
        self.canvas.config(scrollregion=(0, 0, self.total_px, self.total_px))
    
    def check_red_blocks(self):
        #Проверяет количество красных блоков и блокирует окно при необходимости
        red_count = np.count_nonzero(self.matrix == 2)
        if red_count >= 2 and not self.locked:
            self.locked = True
            self.root.attributes('-disabled', True)  # Блокируем окно
            messagebox.showinfo("Блокировка", "Обнаружено 2 красных блока! Окно заблокировано.")
            a_star_pca.take_info(lake_logic.create_np_mas(int(CONST_GRID[2]),int(CONST_GRID[1]),CONST_FILE), CONST_GRID[0],CONST_VAL)
            way, res, _, t = a_star_pca.a_star(CONST_DOT[0],CONST_DOT[1])
            print(way)
            print(res)
            print(t)
            for w in way:
                self.display_matrix[w[0],w[1]] = 2
        
            # Обновляем отображение
            self.img.set_data(self.display_matrix)
            self.mpl_canvas.draw()
        
            # Разблокируем окно
            self.root.attributes('-disabled', False)
            self.locked = False
            messagebox.showinfo("Файл создан", "Матрица смежности сохранена")

    # Реакция на клик пользователя
    def on_click(self, event):
        if event.inaxes != self.ax:
            return
        
        # Получаем координаты (учитываем инверсию Y)
        col = int(event.xdata)
        row = int(event.ydata)
        CONST_DOT.append((row, col))
        print(f"row={row}, col={col}")
        
        if 0 <= row < self.total_blocks and 0 <= col < self.total_blocks:
            # Защищаем синие блоки от изменений
            if self.matrix[row, col] == 1:
                print("Нельзя изменить синие блоки")
                return
                
            # Меняем белый на красный и наоборот
            if self.matrix[row, col] == 0:
                self.matrix[row, col] = 2
            else:
                self.matrix[row, col] = 0 
                CONST_DOT.pop()
            
            self.display_matrix = self.matrix.copy()
            self.img.set_data(self.display_matrix)
            self.mpl_canvas.draw()

            self.check_red_blocks()

# Функции
# Получает данные об сетке из файла
def take_users():
    global CONST_VAL, CONST_FILE, CONST_GRID
    try:
        CONST_VAL = int(text_const.get().strip())
        CONST_FILE = text_file.get()
        if CONST_VAL <= 0 or isinstance(CONST_VAL,str):
            messagebox.showinfo("ошибка","Введино некорректное число")
        CONST_GRID = lake_logic.process_data(CONST_FILE)
        text_const.delete(0, END)
        text_file.delete(0, END)
        print(CONST_VAL)
        print(CONST_FILE)
        print(CONST_GRID)
    
        matrix_window(CONST_GRID[2],CONST_GRID[1])
        
    except:
        messagebox.showinfo("Ошибка","Заполните поля")

def on_closing():
    plt.close('all')
    root.destroy()
    

# Второе окно с матрицей
def matrix_window(rows,cols):
    root.destroy()
    second_window = Tk()
    second_window.title("Окно с матрицей")

    def on_closing_second():
        plt.close('all')
        second_window.destroy()

    second_window.protocol("WM_DELETE_WINDOW", on_closing_second)

    app = FullScrollableMatrix(second_window, lake_logic.create_np_mas(int(CONST_GRID[2]),int(CONST_GRID[1]),CONST_FILE),total_blocks=int(CONST_GRID[1]), block_size_px=5)

    second_window.mainloop()
   


if __name__ == "__main__":
    # Окно
    root = Tk()
    root.geometry("400x300")
    root.resizable(False, False)
    root.configure(bg = "#FFA07A")
    root.title("Стартовое окно")

    # Ввод константы
    label_const = Label(root, text = "Введите стоимостной коэффициент от 1 и больше")
    label_const.pack(pady = 20)
    text_const = Entry(root, width = 40)
    text_const.pack(pady = 5)

    # Ввод имя файла
    label_file = Label(root, text = "Введите название файла")
    label_file.pack(pady = 5)
    text_file = Entry(root, width = 40)
    text_file.pack(pady = 5)

    # Кнопка
    button_user = Button(root, text = "Получить матрицу с координатами", command = take_users)
    button_user.pack()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()