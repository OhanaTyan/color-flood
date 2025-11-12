import random
import enum
import tkinter as tk
from tkinter import messagebox
import tkinter as tk
from copy import deepcopy

class GameFinishException(Exception):
    def __init__(self, point_of_player:int, point_of_computer:int):
        self.point_of_player = point_of_player
        self.point_of_computer = point_of_computer
 
        super().__init__()
       
    def get_point_of_player(self) -> int:
        return self.point_of_player
    
    def get_point_of_computer(self) -> int:
        return self.point_of_computer

	
class ColorFlood:
    
    class Logic:
        class Grid:
            def __init__(self, color:int, assimilated:bool = False):
                self.color = color
                self.assimilated = assimilated
                
            def get_color(self) -> int:
                return self.color
            
            def set_color(self, color:int) -> None:
                self.color = color
                
            def is_assimilated(self) -> bool:
                return self.assimilated
            
            def get_assimilated(self) -> bool:
                return self.is_assimilated()
            
            def set_assimilated(self, assimilated:bool) -> None:
                self.assimilated = assimilated
                
        class Turn(enum.Enum):
            PLAYER = 1
            COMPUTER = 2
        
        def __init__(self, size_of_map:int, num_of_type_of_color:int):
            self.size_of_map = size_of_map
            self.num_of_type_of_color = num_of_type_of_color
            assert(size_of_map > 5 and num_of_type_of_color > 0)
            
            # 初始化玩家信息
            self.last_player = -1
            self.last_computer = -1
            self.turn = self.Turn.PLAYER
            
            self.map=[
                [
                    self.Grid(random.randint(0, num_of_type_of_color-1))
                    for i in range(size_of_map)
                ] 
                for j in range(size_of_map)
            ]
            self.map[0][0].assimilated = True
            self.map[size_of_map-1][size_of_map-1].assimilated = True
            
        def get_color(self, x:int, y:int) -> int:
            return self.map[x][y].get_color()
        
        def get_grid(self, x: int, y: int) -> int:
            return self.map[x][y]
        
        def base_operate(self, x:int, y:int, color:int, prev_color: int):
            visited_grids = [(x, y)]
            directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
            
            def dfs(x: int, y: int):
                self.map[x][y].set_color(color)
                for dx, dy in directions:
                    nx, ny = x+dx, y+dy
                    if nx<0 or nx>=self.size_of_map or ny<0 or ny>=self.size_of_map:
                        continue
                    if (nx, ny) in visited_grids:
                        continue
                    if self.map[nx][ny].get_assimilated() and self.map[nx][ny].get_color() == prev_color:
                        visited_grids.append((nx, ny))
                        dfs(nx, ny)
                    elif self.map[nx][ny].get_color() == color:
                        visited_grids.append((nx, ny))
                        self.map[nx][ny].set_assimilated(True)
                        dfs(nx, ny)
                    """
                    if self.map[nx][ny].get_color() in [prev_color, color]:
                        self.map[nx][ny].set_assimilated(True)
                        # self.map[nx][ny].set_color(color)
                        visited_grids.append((nx, ny))
                        dfs(nx, ny)
                    """
                        
            dfs(x, y)
            
            finished = True 
            point_of_player = 0
            point_of_computer = 0
            for i in range(self.size_of_map):
                for j in range(self.size_of_map):
                    if not self.map[i][j].is_assimilated():
                        finished = False
                    if self.map[i][j].get_color() == self.last_player:
                        point_of_player += 1
                    elif self.map[i][j].get_color() == self.last_computer:
                        point_of_computer += 1
            
            if finished:
                raise GameFinishException(point_of_player, point_of_computer)
             
        def player_operate(self, color: int) -> bool: 
            if color >= self.num_of_type_of_color:
                return False
            if color in [self.last_player, self.last_computer]:
                return False
            if self.turn == self.Turn.COMPUTER:
                return False
            
            prev_color = self.last_player
            self.last_player = color
            self.turn = self.Turn.COMPUTER
            
            self.base_operate(self.size_of_map-1, self.size_of_map-1, color, prev_color)
            
            return True
            
        def computer_operate(self, color: int) -> bool:
            if color >= self.num_of_type_of_color:
                return False
            if color in [self.last_player, self.last_computer]:
                return False
            if self.turn == self.Turn.PLAYER:
                return False
            
            prev_color = self.last_computer
            self.last_computer = color
            self.turn = self.Turn.PLAYER
            
            self.base_operate(0, 0, color, prev_color)
            
            return True

        def print_map(self):
            for i in range(self.size_of_map):
                for j in range(self.size_of_map):
                    print(self.map[i][j].get_color(), end=" ")
                print()
            
    
    class UI:
        def __init__(self, logic: "Logic", computer_ai: "ComputerAIBase", debug:bool=False):
            self.logic = logic
            self.root = tk.Tk()
            self.root.title("颜色洪水战")
            
            # 游戏状态显示
            self.status_var = tk.StringVar()
            self.status_var.set("玩家回合")
            status_label = tk.Label(self.root, textvariable=self.status_var, font=('Arial', 12))
            status_label.pack()
            
            # 地图显示
            self.map_frame = tk.Frame(self.root)
            self.map_frame.pack()
            self.map_buttons = []
            
            # 颜色选择
            self.color_frame = tk.Frame(self.root)
            self.color_frame.pack()
            self.color_buttons = []
            
            # 控制按钮
            control_frame = tk.Frame(self.root)
            control_frame.pack()
            tk.Button(control_frame, text="重新开始", command=self.reset_game).pack(side=tk.LEFT)
            
            # 电脑 AI
            self.computer_ai = computer_ai
            
            self.debug = debug
            
            self.init_ui()
            
        def init_ui(self):
            # 初始化地图显示
            for i in range(self.logic.size_of_map):
                row = []
                for j in range(self.logic.size_of_map):
                    btn = tk.Button(self.map_frame, width=3, height=1,
                                   bg=self.get_color_name(self.logic.get_color(i,j)),
                                   state=tk.DISABLED)
                    btn.grid(row=i, column=j)
                    row.append(btn)
                self.map_buttons.append(row)
            
            # 初始化颜色选择按钮
            for color in range(self.logic.num_of_type_of_color):
                btn = tk.Button(self.color_frame, text=str(color), width=3,
                               bg=self.get_color_name(color),
                               command=lambda c=color: self.player_select_color(c))
                btn.pack(side=tk.LEFT)
                self.color_buttons.append(btn)
            
            self.update_ui()
            
        def get_color_name(self, color:int) -> str:
            """获取颜色名称，使用更丰富的颜色选项"""
            colors = [
                '#FF0000', '#00FF00', '#0000FF', '#FFFF00',  # 红、绿、蓝、黄
                '#FF00FF', '#FFA500', '#FFC0CB', '#00FFFF',  # 紫、橙、粉、青
                '#A52A2A', '#008000', '#000080', '#808000'   # 棕、深绿、深蓝、橄榄
            ]
            return colors[color % len(colors)]
            
        def player_select_color(self, color:int):
            try:
                if self.logic.player_operate(color):
                    self.update_ui()
                    self.root.after(1000, self.computer_turn)
            except GameFinishException as e:
                self.show_game_result(e)
                
        def computer_turn(self): 
            new_map = [
                deepcopy(l) for l in self.logic.map
            ]
            assert new_map[-1][-1].color == self.logic.last_player
            color = self.computer_ai.get_color(self.logic.num_of_type_of_color, new_map)#deepcopy(self.logic.map))
            try:
                if self.logic.computer_operate(color):
                    self.update_ui()
            except GameFinishException as e:
                self.show_game_result(e)
            # 简单AI: 随机选择可用颜色
            """
            available_colors = [c for c in range(self.logic.num_of_type_of_color)
                              if c not in [self.logic.last_player, self.logic.last_computer]]
            if available_colors:
                color = random.choice(available_colors)
                self.logic.computer_operate(color)
                self.update_ui()
            """
            
        def update_ui(self):
            if self.debug:
                self.logic.print_map()
            
            # 更新地图显示
            for i in range(self.logic.size_of_map):
                for j in range(self.logic.size_of_map):
                    grid = self.logic.get_grid(i,j)
                    btn = self.map_buttons[i][j]
                    btn.config(bg=self.get_color_name(grid.get_color()))
                    if grid.is_assimilated():
                        btn.config(relief=tk.SUNKEN)
            
            # 更新状态
            if self.logic.turn == self.logic.Turn.PLAYER:
                self.status_var.set("玩家回合")
            else:
                self.status_var.set("电脑回合")
            
            # 更新颜色按钮状态
            for i, btn in enumerate(self.color_buttons):
                if i in [self.logic.last_player, self.logic.last_computer]:
                    btn.config(state=tk.DISABLED)
                else:
                    btn.config(state=tk.NORMAL)
            
                
        def show_game_result(self, e):
            message = f"游戏结束!\n玩家得分: {e.point_of_player}\n电脑得分: {e.point_of_computer}"
            if e.point_of_player > e.point_of_computer:
                message += "\n玩家获胜!"
            else:
                message += "\n电脑获胜!"
            tk.messagebox.showinfo("游戏结束", message)
            self.reset_game()
            
        def reset_game(self):
            self.logic = self.logic.__class__(self.logic.size_of_map, self.logic.num_of_type_of_color)
            self.update_ui()
            
        def mainloop(self):
            self.root.mainloop()
        
    class ComputerAIBase:
        def __init__(self):
            pass
        
        def set_color(self, num_of_type_of_color:int, map: list[list["ColorFlood.Logic.Grid"]]):
            pass
        
    class EasyComputerAI(ComputerAIBase):
        def __init__(self):
            pass
        
        def get_color(self, num_of_type_of_color:int, map: list[list["ColorFlood.Logic.Grid"]]) -> int:
            """简单AI: 随机选择可用颜色"""
            last_computer = map[0][0].get_color()
            last_player = map[logic.size_of_map-1][logic.size_of_map-1].get_color()
            while True:
                color = random.randint(0, num_of_type_of_color-1)
                if color not in [last_computer, last_player]:
                    return color
    
    class GreedyComputerAI(ComputerAIBase):
        """
        贪心算法：
        优先选择可以扩散最多的颜色
        """    
            
        def __init__(self):
            pass
        
        def get_color(self, num_of_type_of_color:int, map: list[list["ColorFlood.Logic.Grid"]]) -> int:
            """贪心算法: 优先选择可以扩散最多的颜色"""
            last_computer = map[0][0].get_color()
            last_player = map[-1][-1].get_color()
            
            # 统计每种颜色能同化的格子数
            color_counts = {}
            directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
            
            for color in range(num_of_type_of_color):
                # 跳过上次选择的颜色
                if color in [last_computer, last_player]:
                    continue
                    
                # 模拟同化过程
                visited = set()
                queue = [(0, 0)]  # 从电脑的格子开始
                count = 0
                
                while queue:
                    x, y = queue.pop(0)
                    if (x, y) in visited:
                        continue
                        
                    visited.add((x, y))
                    count += 1
                    
                    # 检查相邻格子
                    for dx, dy in directions:
                        nx, ny = x + dx, y + dy
                        if (0 <= nx < len(map) and 0 <= ny < len(map) and 
                            map[nx][ny].get_color() in [color, last_computer]):
                            queue.append((nx, ny))
                
                color_counts[color] = count
                
            if not color_counts:
                # 没有可选颜色，随机选择
                while True:
                    color = random.randint(0, num_of_type_of_color-1)
                    if color not in [last_computer, last_player]:
                        return color
                        
            # 选择能同化最多格子的颜色
            max_count = max(color_counts.values())
            best_colors = [c for c, cnt in color_counts.items() if cnt == max_count]
            return random.choice(best_colors)
            

            
        
            
if __name__ == "__main__":
    """游戏主入口"""
    # 初始化游戏逻辑: 6种颜色
    logic = ColorFlood.Logic(20, 6)
    # 创建并启动UI
    ui = ColorFlood.UI(logic, ColorFlood.GreedyComputerAI())
    ui.mainloop()
            

        
            








