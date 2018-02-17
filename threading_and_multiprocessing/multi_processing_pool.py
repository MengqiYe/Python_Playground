from multiprocessing import Pool
import time


def f(n):
    sum = 0
    for n in range(1000):
        sum += n * n
    return sum


if __name__ == '__main__':
    arr = [1, 2, 3, 4, 5]
    t1 = time.time()
    p = Pool()
    result = p.map(f, range(1000000))
    print(f"Pool time {time.time() - t1 }")

    t2 = time.time()
    result = []
    for n in range(1000000):
        result.append(f(n))
    print(f"Serial time {time.time() - t2}")
