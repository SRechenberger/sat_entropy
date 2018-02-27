class Queue:
    """ Models a queue with no need for explicit deletion. """
    def __init__(self, size):
        self.size = size
        self.begin = 0
        self.filled = 0
        self.lst = []


    def isFilled(self):
        if self.size == None:
            return True
        return len(self.lst) >= self.size


    def write(self, elem):
        """ Writes an element into the queue and returns the value
        overwritten, or None.
        """
        if not self.isFilled() or self.size == None:
            # Filling phase
            self.lst.append(elem)
            self.filled += 1
            return None
        else:
            tmp = self.lst[self.begin]
            self.lst[self.begin] = elem
            self.begin += 1
            self.begin %= self.size
            return tmp

