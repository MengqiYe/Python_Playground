import threading
import time


class Timer:
    def __init__(self, count_down_time=10, func=None):
        self.count_down_time = count_down_time
        self.func = func

        self.last_time = time.time()
        self.is_counting = True

        self.thread = threading.Thread(target=self.count_down, args=())
        self.thread.start()

        print(f"Start timing!")

    def count_down(self):
        while self.is_counting:
            # print(f"Counting down, self.count_down_time : {self.count_down_time}")
            now = time.time()
            self.count_down_time -= (now - self.last_time)
            if self.count_down_time > 0:
                pass
            else:
                self.is_counting = False
                self.func()

            self.last_time = now
            time.sleep(0.2)

    def cancel(self):
        self.is_counting = False
        print(f"Count down canceled.")


def on_finish():
    print(f"Count down finished.")


if __name__ == '__main__':
    t = Timer(count_down_time=2, func=on_finish)
