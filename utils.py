import os

def create_directory(dir_name):
    try:
        # Create target Directory
        os.mkdir(dir_name)
        print("Directory " , dir_name ,  " Created ")
    except FileExistsError:
        print("Directory " , dir_name ,  " already exists")


def logging(model_name, text):
    with open(model_name+"/log.txt", "a") as myfile:
        myfile.write(text+ '\n\n')

def map_oht_state(oht_state):
    player_id = oht_state[0]
    state = oht_state[1:]
    out = []
    for piece in state:
        if piece == 0 or piece == 1:
            out.append(piece)
        else:
            out.append(-1)

    mask = [1 if x==0 else 0 for x in out]
    out.append(player_id)
    return out, mask
