import time
import threading


def calc_square(numbers):
    print("Calculate square numbers")
    for n in numbers:
        time.sleep(.2)
        print(f"square : {n*n}, at time : {time.time()}")


def calc_cube(numbers):
    print("Calculate cube numbers")
    for n in numbers:
        time.sleep(.2)
        print(f"cube : {n*n*n}, at time : {time.time()}")


if __name__ == '__main__':
    arr = [2, 3, 8, 9]
    t = time.time()
    t1 = threading.Thread(target=calc_square, args=(arr,))
    t2 = threading.Thread(target=calc_cube, args=(arr,))
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    print(f"Done in : {time.time() - t}")
