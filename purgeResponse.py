import os
import re

def delete_file(start):
    N = start
    while os.path.exists(f"bot_responses{N}.txt"):
        N += 1
    for i in range(start, N):
        filename = f"bot_responses{i}.txt"
        os.remove(filename)
        print(f"{filename} has been deleted.")

# Call the function with the specific start number
delete_file(2)
