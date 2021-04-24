def loadchunk(path):
    f = open(path + '.txt', 'r')
    data = f.read()
    f.close()
    data = data.split('\n')  # Split data by new line (into rows)
    file_chunk = []
    for row in data:
        file_chunk.append(list(row))  # Turn row(string) into an iterable object(list)
    return file_chunk

CHUNK_SIZE = 8

def generate_chunk():                #todo vertical chunk generation(?)
    chunk_data = []
    chunk = loadchunk('chunk1')
    for x in range(CHUNK_SIZE):
        for y in range(CHUNK_SIZE):
            print(x, y, chunk[x][y])

    # for y_pos in chunk[1]:
    #     for x_pos in chunk[0]:
    #         print(chunk[x_pos][y_pos])

generate_chunk()