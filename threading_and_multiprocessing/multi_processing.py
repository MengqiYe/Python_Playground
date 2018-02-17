import time
import multiprocessing

results = []

def calc_square(numbers, results, q):
    print("Calculate square numbers")
    for idx,n in enumerate(numbers):
        r = n*n
        results[idx] = r
        q.put(r)
        print(f"square : {r}, at time : {time.time()}")
    print(f"Inside process : {results}")

def calc_cube(numbers):
    print("Calculate cube numbers")
    for n in numbers:
        print(f"cube : {n*n*n}, at time : {time.time()}")


if __name__ == '__main__':
    arr = [2, 3, 8, 9]
    t = time.time()
    shared_queue = multiprocessing.Queue()
    shared_results = multiprocessing.Array('i',4)
    p1 = multiprocessing.Process(target=calc_square, args=(arr, shared_results, shared_queue))
    p2 = multiprocessing.Process(target=calc_cube, args=(arr,))
    p1.start()
    p2.start()
    p1.join()
    p2.join()

    while not shared_queue.empty():
        print(shared_queue.get())

    print(f"Done in : {time.time() - t}")
    print(f"Outside of process : {shared_results[:]}")