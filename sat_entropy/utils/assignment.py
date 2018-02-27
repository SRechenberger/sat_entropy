import random

class Assignment:

    def __init__(self, atoms = None, varCount = None, seed = None):
        if atoms == None and varCount == None:
            self.atoms = None
            self.varCount = None
            self.isInit = False
        elif atoms == None:
            if not type(varCount) == int:
                raise TypeError("varCount was no int.")
            self.varCount = varCount
            self.initRandomly()
        else:
            if varCount == None:
                self.varCount = len(atoms)
                self.atoms = atoms
            else:
                if len(atoms) != varCount:
                    raise ValueError(
                        "len(atoms) = {} and given varCount = {} do net match."
                            .format(len(atoms), varCount))
                else:
                    self.varCount = varCount
                    self.atoms = atoms


    def initRandomly(self):
        self.atoms = [None]
        for i in range(1, self.varCount+1):
            if random.randint(0,1) == 0:
                self.atoms.append(False)
            else:
                self.atoms.append(True)


    def isTrue(self, literal):
        if not type(literal) == int:
            raise TypeError("literal = {} is no int.".format(literal))

        if var <= 0:
            raise ValueError("var = {} is negative or zero.".format(var))

        if var > self.varCount:
            raise ValueError("var = {} is greater than varCount = {}"
                            .format(var, self.varCount))

        return (literal > 0) == self.atoms[abs(literal)]


    def flip(self, var):
        if not type(var) == int:
            raise TypeError("var = {} is no int.".format(var))

        if var <= 0:
            raise ValueError("var = {} is negative or zero.".format(var))

        if var > self.varCount:
            raise ValueError("var = {} is greater than varCount = {}"
                            .format(var, self.varCount))

        self.atoms[var] = not self.atoms[var]


    def __str__(self):
        l = 0
        toReturn = 'n = {}'.format(self.varCount)
        for i in range(1,self.varCount+1):
            if l % 32 == 0:
                toReturn += '\n'
            if self.atoms[i]:
                toReturn += '1'
            else:
                toReturn += '0'
            l += 1

        return toReturn


