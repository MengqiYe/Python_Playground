from multiprocessing import Process, Queue


def input_loop(queue):
    x = 0
    while True:
        queue.put(x)
        x += 1


def output_loop(queue):
    while True:
        print(queue.get())


if __name__ == '__main__':
    queue = Queue()
    p1 = Process(target=input_loop, args=(queue,))
    p2 = Process(target=output_loop, args=(queue,))
    p1.start()
    p2.start()
