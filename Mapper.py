

class Mapper:


    def __init__(self, board_size = 4):
        self.board_size = board_size
        self.int_to_action = self.create_int_to_action_mapping()
        self.action_to_int = self.create_action_to_int_mapping()


    def create_int_to_action_mapping(self):
        d = {}
        c = 0
        for i in range(self.board_size):
            for j in range(self.board_size):
                d[c] = (i,j)
                c+=1
        return d

    def create_action_to_int_mapping(self):
        d = {}
        c = 0
        for i in range(self.board_size):
            for j in range(self.board_size):
                d[(i,j)] = c
                c += 1
        return d