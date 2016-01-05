import time


class ProgressBar:
    def __init__(self, size):
        self.size = size
        self.transferred = 0
        self.time = time.time()
        self.snapshots = []
        self.last_info = time.time()

    def update(self, transferred):
        dt = time.time() - self.time
        self.time = time.time()
        self.snapshots.append((transferred, dt))
        if len(self.snapshots) >= 500:
            self.snapshots = self.snapshots[:-1]

    def average_speed(self):
        t = 0
        data = 0
        for snapshot in self.snapshots:
            t += snapshot[1]
            data += snapshot[0]
        return data/t

    def time_left(self):
        if self.size - self.transferred is not 0:
            return (self.size - self.transferred)/self.average_speed()
        return 0

    def info(self):
        if time.time() - self.last_info > 0.5:
            self.last_info = time.time()
        else:
            return
        avs = self.average_speed()
        tl = self.time_left()
        if avs / 2**20 >= 1:
            avs = "{} MiB/s".format(avs/2**20)
        else:
            avs = "{} KiB/s".format(avs/2**10)
        print("{}; eta {} seconds".format(avs, tl))
