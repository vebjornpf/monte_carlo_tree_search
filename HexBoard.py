import networkx as nx
import matplotlib.pyplot as plt

PLAYER_1 = 1
PLAYER_2 = -1
EMPTY = 0

map_seed = {6:1, 4:2, 2:2, 3:3, 7:5, 8:15, 9:9, 10:10, 5:3}

class HexBoard():


    def __init__(self, board_size = 5, verbose=False):
        
        self.board_size = board_size
        self.board = self.board_init()
        self.verbose = verbose
        self.pieces = 0

    def set_verbose(self, verbose):
        self.verbose = verbose

    def reset_game(self):
        self.board = self.board_init()
        self.pieces = 0

    def all_moves(self):
        all_moves = []
        for i in range(self.board_size):
            for j in range(self.board_size):
                all_moves.append((i,j))
        return all_moves


        
    def board_init(self):
        board = {}
        for i in range(self.board_size):
            for j in range(self.board_size):
                board[i,j] = EMPTY
        return board

    def get_all_neighbours(self, pos):
        potential_neighbours = [(pos[0], pos[1]-1),
                                (pos[0]+1, pos[1]-1),
                                (pos[0]-1, pos[1]),
                                (pos[0]+1, pos[1]),
                                (pos[0]-1, pos[1]+1),
                                (pos[0], pos[1]+1)]
        neighbours = [n for n in potential_neighbours if n in self.board]
        return neighbours

    def get_top_down_neighbours(self, pos):
        potential_neighbours = [(pos[0] + 1, pos[1]),
                                (pos[0] + 1, pos[1] - 1),
                                (pos[0], pos[1] - 1),
                                (pos[0], pos[1] + 1)]

        neighbours = [n for n in potential_neighbours if n in self.board]
        return neighbours

    def get_right_left_neighbours(self, pos):
        potential_neighbours = [(pos[0], pos[1]+1),
                                (pos[0] - 1, pos[1] + 1),
                                (pos[0]-1, pos[1]),
                                (pos[0]+1, pos[1])]
        neighbours = [n for n in potential_neighbours if n in self.board]
        return neighbours

    def get_neighbours_with_value(self,pos, value):
        """
        if value == PLAYER_1:
            neighbours =self.get_top_down_neighbours(pos)
        else:
            neighbours =  self.get_right_left_neighbours(pos)
        """
        neighbours = self.get_all_neighbours(pos)
        return [n for n in neighbours if self.get_cell(n) == value]


    def get_cell(self, pos):
        return self.board[pos]

    def take_action(self, pos, player):

        if player == 1:
            self.board[pos] = PLAYER_1
        else:
            self.board[pos] = PLAYER_2
        self.pieces += 1

    # legal actions defined as cells with value (0,0)
    def get_legal_actions(self):
        actions = []
        for pos, value in self.board.items():
            if value == EMPTY:
                actions.append(pos)
        return actions

    def is_terminal_state(self):
        return self.pieces == self.board_size*self.board_size

    def is_winning_state(self, player):
        if player == 1:
            edges_1 = [(0,x) for x in range(self.board_size) if self.get_cell((0,x)) == PLAYER_1]
            edges_2 = [(self.board_size-1, x) for x in range(self.board_size) if
                       self.get_cell((self.board_size-1,x)) == PLAYER_1]
            objective = PLAYER_1
        else:
            edges_1 = [(x, 0) for x in range(self.board_size) if self.get_cell((x, 0)) == PLAYER_2]
            edges_2 = [(x, self.board_size - 1) for x in range(self.board_size) if
                       self.get_cell((x, self.board_size - 1)) == PLAYER_2]
            objective = PLAYER_2
        # is it a path from a node in edges_1 to an node in edges_2?
        if (len(edges_1) == 0 or len(edges_2) == 0):
            return False
        for pos in edges_1:
            path = []
            found = self.search_state_graph(pos, objective, edges_2)
            if found:
                return True
        return False

    def search_state_graph(self, start_pos, objective, terminals):
        frontier = list()
        frontier.append(start_pos)
        explored = set()

        while not len(frontier) == 0:
            current_node = frontier.pop()
            if current_node in explored:
                continue
            if current_node in terminals:
                return True

            for n in self.get_neighbours_with_value(current_node, objective):
                frontier.append(n)

            explored.add(current_node)
        return False


    def search_state_graph1(self, pos, objective, terminals, path):
        neighbours = self.get_neighbours_with_value(pos, objective)
        if len(neighbours) == 0:
            return False
        if not pos in path:
            path.append(pos)

            for n in neighbours:
                if n in terminals:
                    path.append(n)
                    print("found!")
                    return True
                elif self.get_cell(n) == objective:
                   return self.search_state_graph(n, objective, terminals, path)


    def get_state(self):
        return list(self.board.values())

    def get_state_mask(self):
        pieces = list(self.board.values())
        mask = [1 if piece==EMPTY else 0 for piece in pieces]
        return mask

    def draw_board(self, title="Board"):
        G = nx.Graph()
        color_map = []
        for pos, value in self.board.items():
            G.add_node(pos)
            neighbours = self.get_all_neighbours(pos)
            for n in neighbours:
                G.add_edge(pos, n)

        for node in G:
            if self.get_cell(node) == PLAYER_1:
                color_map.append('sandybrown')

            elif self.get_cell(node) == PLAYER_2:
                color_map.append('c')
            else:
                color_map.append('lightgrey')

        edges_1_1 = [(0, x) for x in range(self.board_size)]
        edges_1_2 = [(self.board_size - 1, x) for x in range(self.board_size)]

        edges_2_1 = [(x, 0) for x in range(self.board_size)]
        edges_2_2 = [(x, self.board_size - 1) for x in range(self.board_size)]

        color_edges = []
        widths_edges = []
        print(len(G.edges))
        for edge in G.edges:
            n1 = edge[0]
            n2 = edge[1]

            if (n1 in edges_1_1 and n2 in edges_1_1) or (n1 in edges_1_2 and n2 in edges_1_2):
                color_edges.append("sandybrown")
                widths_edges.append(2)

            elif (n1 in edges_2_1 and n2 in edges_2_1) or (n1 in edges_2_2 and n2 in edges_2_2):
                color_edges.append("c")
                widths_edges.append(2)
            elif self.get_cell(n1) == self.get_cell(n2) and self.get_cell(n1) == PLAYER_1:
                color_edges.append("sandybrown")
                widths_edges.append(1)
            elif self.get_cell(n1) == self.get_cell(n2) and self.get_cell(n1) == PLAYER_2:
                color_edges.append("c")
                widths_edges.append(1)
            else:
                color_edges.append("grey")
                widths_edges.append(1)







        options = {
            'node_size': 300,
            'fontsize': 2,
            'font_color': 'black',
            'node_color': color_map,
            'edge_color': color_edges,
            'width': widths_edges,

            'pos': nx.spring_layout(G, seed=map_seed[self.board_size]),  # Making sure it looks decent
        }
        plt.title(title, fontsize=16)
        nx.draw(G, with_labels=True, **options)
        plt.show()






if __name__ == '__main__':
    board = HexBoard(5)






    board.draw_board()




