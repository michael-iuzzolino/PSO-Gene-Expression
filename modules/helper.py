class ThreadStopper(object):
    def __init__(self):
        self.stopped = False

    def stop(self):
        self.stopped = True
