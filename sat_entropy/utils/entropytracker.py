import math
from sat_entropy.utils.queue import *

class Entropytracker:
    def __init__(self, size = None):
        self.queue = Queue(size)
        self.count = {}
        self.entropy = 0
        self.size = size
        self.isInit = False


    def calculateEntropy(self):
        self.entropy = 0
        if self.size == None:
            elements = len(self.queue.lst)
        else:
            elements = self.size

        if not self.isInit or self.size == None:
            for _, cnt in self.count.items():
                p = cnt / elements
                self.entropy -= p * math.log(p,2)
            self.isInit = True and self.size != None



    def add(self, elem):
        """ Adds a new element to the queue, and updates the entropy. """
        ret = self.queue.write(elem)
        if self.size == None:
            elements = len(self.queue.lst)
        else:
            elements = self.size

        # if there is some return value,
        # the queue is filled sufficiently.
        if ret:
            # If the queue was not sufficiently filled until now,
            # initiate the entropy.
            self.calculateEntropy()

            # Calculate the old probability of the removed element.
            p = self.count[ret] / elements
            # Remove it from the sum.
            self.entropy += p * math.log(p,2)

            # Decrement the counter of the dropped element.
            self.count[ret] -= 1
            # If the counter is null, delete the field.
            if self.count[ret] == 0:
                del self.count[ret]
            # Otherwise, calculate the new entropy,
            # and add it to the sum.
            else:
                p = self.count[ret] / elements
                self.entropy -= p * math.log(p,2)

            # If the added element is new in the queue,
            # set its counter to 1.
            if elem not in self.count:
                self.count[elem] = 1
            # Otherwise, calculate the old probability of the new element,
            # and remove it from the sum.
            else:
                p = self.count[elem] / elements
                self.entropy += p * math.log(p,2)
                # Increment the counter of the new element.
                self.count[elem] += 1

            # Calculate the new probability of the added element,
            # and add it to the sum.
            p = self.count[elem] / elements
            self.entropy -= p *  math.log(p,2)
        else:
            if elem in self.count:
                self.count[elem] += 1
            else:
                self.count[elem] = 1


    def getEntropy(self):
        """ If the queue is sufficiently filled, return the entropy,
        otherwise return None.
        """

        # Return the entropy only, if the queue is sufficiently filled,
        # for it would not be valid otherwise.
        if self.queue.isFilled() or self.size == None:
            self.calculateEntropy()
            return self.entropy
        else:
            return None
