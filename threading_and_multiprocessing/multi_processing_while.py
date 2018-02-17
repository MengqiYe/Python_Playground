import threading
from multiprocessing import Pool, Process
import random
import time

q = None

class Queue:
    def __init__(self):
        self.data = []
        self.index = -1

    def __iter__(self):
        return self

    def __next__(self):
        self.index += 1
        if self.index == len(self.data):
            raise StopIteration
        return self.data[self.index]

    def Enqueue(self, x):
        self.data.append(x)

    def Dequeue(self):
        x = self.data[0]
        self.data = self.data[1:]
        return x

    def Peek(self):
        return self.data[0]


def process_num(n):
    print(f"n : {n}")


def input_loop():
    x = 0
    global q
    while True:
        q.Enqueue(x)
        x += 1


if __name__ == '__main__':
    workers_queue = Queue()
    q = Queue()

    t = threading.Thread(target=input_loop, args=())
    t.start()

    p = Pool()

    print(q)
    p.map(process_num, q)

