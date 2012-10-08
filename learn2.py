from decimal import Decimal

class linearProgram:
    import re

    """ Class to parse input file and setup all the variables """
    commaDelimitedPattern = re.compile(',')
    offset = 0
    rowCol = 0
    rows = 0
    cols = 0
    rowVals = []
    objCo = []
    lowerb = []
    upperb = []
    vlowerb = []
    vupperb = []    
    basic = []
    nonbasic = []

    def __init__(self, f):
        for i,line in enumerate(f):
            if not(self.setOffset(line)):
                self.setRowsAndCols(i,line)
                self.setObjectiveCoefficients(i,line)
                self.setRowValues(i,line)
                self.setLowerBounds(i,line)
                self.setUpperBounds(i,line)
                self.setVarLowerBounds(i,line)
                self.setVarUpperBounds(i,line)
        self.setBasic()

    """ Set offset if line is newline  """
    def setOffset(self,line):
        if line == '\n':
            self.offset += 1
            return True
        return False

    """ Set appropriate variables """
    def setRowsAndCols(self,i,line):
        """ first row is #rows,#cols """
        if self.rowCol == 0 and i == 0:
            self.rowCol = self.commaDelimitedPattern.split(line)
            self.rows = int(self.rowCol[0])
            self.cols = int(self.rowCol[1])

    def setObjectiveCoefficients(self,i,line):
        """ second row is the coefficients of objective function """
        if self.objCo == [] and i > 0:
            for obj in self.commaDelimitedPattern.split(line):
                self.objCo.append(Decimal(obj.rstrip()))

    def setRowValues(self,i,line):
        """ next m+1 rows for row values """
        if self.offset+1 < i and i <= self.rows+self.offset+1:
            items = []
            for obj in self.commaDelimitedPattern.split(line):
                items.append(Decimal(obj.rstrip()))
            self.rowVals.append(items)

    def setLowerBounds(self,i,line):
        """ lower bounds """
        if self.lowerb == [] and i > self.rows+self.offset+1:
            for obj in self.commaDelimitedPattern.split(line):
                self.lowerb.append(Decimal(obj.rstrip()))
    
    def setUpperBounds(self,i,line):
        """ upper bounds """
        if self.upperb == [] and i > self.rows+self.offset+2:
            for obj in self.commaDelimitedPattern.split(line):
                self.upperb.append(Decimal(obj.rstrip()))
        
    def setVarLowerBounds(self,i,line):
        """ var lower bounds """
        if self.vlowerb == [] and i > self.rows+self.offset+3:
            for obj in self.commaDelimitedPattern.split(line):
                self.vlowerb.append(Decimal(obj.rstrip()))
    
    def setVarUpperBounds(self,i,line):
        """ var lower bounds """
        if self.vupperb == [] and i > self.rows+self.offset+4:
            for obj in self.commaDelimitedPattern.split(line):
                self.vupperb.append(Decimal(obj.rstrip()))

    def setBasic(self):
        """ sets the basic """
        if self.basic == []:
            for i in range(0,self.cols):
                self.basic.append('x'+str(i))
        if self.nonbasic == []:
            for i in range(0,self.rows):
                self.nonbasic.append('w'+str(i))

    """ Print """
    def printAll(self):
        self.printRows()
        self.printCols()
        self.printObjective()
        self.printLowerBounds()
        self.printUpperBounds()
        self.printVarLowerBounds()
        self.printVarUpperBounds()
        self.printRowVals()
        self.printBasic()
        self.printMatrix()
    def printRows(self):
        print 'rows =', self.rows
    def printCols(self):
        print 'cols =', self.cols
    def printObjective(self):
        print 'objective coefficients =', self.objCo
    def printLowerBounds(self):
        print 'lower bounds =', self.lowerb
    def printUpperBounds(self):
        print 'upper bounds =', self.upperb
    def printVarLowerBounds(self):
        print 'variable lower bounds =', self.vlowerb
    def printVarUpperBounds(self):
        print 'variable upper bounds =', self.vupperb
    def printRowVals(self):
        for i,item in enumerate(self.rowVals):
            print 'row values row',i,'=', item
    def printBasic(self):
        print 'basic =', self.basic
        print 'nonbasic =', self.nonbasic
    def printMatrix(self):
        print ''
        for i in range(0,self.rows):
            #stri = '{0} {1} | {2} | {3'.format(self.lowerb[i],self.upperb[i],self.nonbasic[i])
            #print stri
            stmt = ''
            for j in range(0,self.cols):
                stmt += str(self.rowVals[i][j])
                stmt += '         '
            print self.lowerb[i], self.upperb[i], '|',self.nonbasic[i],'|', stmt
        print '            --------------------'
        stmt1 = '            | z  | '
        stmt2 = '            |    | '
        stmt3 = '            |    | '
        for j in range(0,self.cols):
            stmt1 += str(self.objCo[j])
            stmt1 += '        '
            stmt2 += str(self.vlowerb[j])
            stmt2 += '         '
            stmt3 += str(self.vupperb[j])
            stmt3 += '         '
        print stmt1
        print stmt2
        print stmt3

class simplexSolver:
    resting = []
    w = []
    e = []
    newObjCo = []
    z = 0
    """ Class to solve a simplex problem via an linearProgram object """
    def __init__(self, input):
        self.data = input

    def solve(self):
        print 'solving...'
        self.initialize()
        self.solveSimplex()
        self.data.printMatrix()

    def initialize(self):
        print 'initializing...'
        self.formInitialDictionary()
        self.calculateRows()
        if not(self.isFeasible()):
            self.createEvariables()
            self.changeObjective()
            self.solveSimplex()
            self.removeEvariables()

    def formInitialDictionary(self):
        """ need to choose starting resting variables here """
        print 'forming initial dictionary...'
        self.setResting()
    
    def setResting(self):
        """ set resting variable upper or lower """
        print 'setting resting variable'
        for i in range(len(self.data.vlowerb)):
            if (self.data.vlowerb[i] == Decimal('-Infinity')):
                self.resting.append('upper')
            elif (self.data.vupperb[i] == Decimal('Infinity')):
                self.resting.append('lower')
            elif not(self.data.vlowerb[i] == Decimal('-Infinity') and 
                     not(self.data.vupperb[i] == Decimal('Infinity'))):
                lowerObj = self.data.vlowerb[i] * self.data.objCo[i]
                upperObj = self.data.vupperb[i] * self.data.objCo[i]
                if (lowerObj > upperObj):
                    self.resting.append('lower')
                else:
                    self.resting.append('upper')
            #TODO: check if both are +/- infinity
            #print self.resting[i]
        
    def calculateRows(self):
        """ calculate the row values """
        # for every row
        for i in range(0,self.data.rows):
            sum = Decimal('0')
            # for every column
            for j in range(0,self.data.cols):
                # calculate sum t
                if (self.resting[j] == 'lower'):
                    #TODO: remove this once solved +/- infinity?
                    if self.data.vlowerb[j].is_finite():
                        sum += self.data.rowVals[i][j] * self.data.vlowerb[j]
                    else:
                        sum += 0
                elif (self.resting[j] == 'upper'):
                    #TODO: remove this once solved +/- infinity?
                    if self.data.vupperb[j].is_finite():
                        sum += self.data.rowVals[i][j] * self.data.vupperb[j]
                    else:
                        sum += 0
            self.w.append(sum)
            #print 'row =', i, 'value =', sum
    
    def isFeasible(self):
        """ check values of w's... """
        print 'checking if feasible...'
        for i in range(0,self.data.rows):
            # check versus lower and upper bounds
            if ((self.w[i] > self.data.upperb[i]) or (sum < self.data.lowerb[i])):
                print 'infeasible... initializing with e variables'
                return False
        print 'feasible... moving on.'
        return True

    def isFinal(self):
        """ check if dictionary is final """
        print 'checking if final'
        isFinal = True
        for i in range(0,self.data.cols):
            if (self.resting[i] == 'upper'):
                if not (self.data.objCo[i] >= 0):
                    print 'a'
                    isFinal = False
            elif (self.resting[i] == 'lower'):
                if not (self.data.objCo[i] <= 0):
                    isFinal = False
        if (isFinal):
            print 'Final Dictionary Found!'
            return True

    def createEvariables(self):
        """ if infeasible (w outside bounds), then create variables e to add/subtract from row """
        #TODO fix this!
        print 'creating e variables...'
        for i in range(0,self.data.rows):
           if (self.w[i] > self.data.upperb[i]):
               # create subtraction e
               print 'row', i, self.w[i], 'too high', self.data.upperb[i]
               self.e.append(Decimal('-1'))
               #self.data.rowVals[i].append(Decimal('-1'))
           elif (self.w[i] < data.lowerb[i]):
               # create addition e
               print 'row', i, self.w[i], 'too low', self.data.lowerb[i]
               self.e.append(Decimal('1'))
               #self.data.rowVals[i].append(Decimal('1'))
           else:
               self.e.append(Decimal('0'))
               #self.data.rowVals[i].append(Decimal('0'))
        print self.e
        #print self.data.rowVals

    def removeEvariables(self):
        """ remove the e's and reintroduce the original objective in terms of w's """
        #TODO this!
        print 'removing e variables...'

    def changeObjective(self):
        """ change objective function to minimize variables e """
        #TODO this!
        print 'changing objective...'
        le = 0
        for i in self.e:
            if i != Decimal('0'):
                le += 1
        
        for i in range(0,self.data.cols):
            self.newObjCo.append(Decimal('0'))
        for i in range(0,le):
            self.newObjCo.append(Decimal('-1'))

    def determineEnteringVar(self):
        """ determine the entering variable """
        print 'determining the entering variable'
        for i in range(0,self.data.cols):
            #TODO: make this so it doesn't just select the first eligible?
            if (self.resting[i] == 'lower' and self.data.objCo[i] > 0):
                print self.data.basic[i], 'is eligible to enter- lower'
                return i
            elif (self.resting[i] == 'upper' and self.data.objCo[i] < 0):
                print self.data.basic[i], 'is eligible to enter- upper'
                return i

    def determineExitingVar(self,enter):
        """ determine the exiting variable """
        print 'determining the exiting variable'
        x = 0
        exitVal = Decimal("Infinity")
        exit = -1
        bounds = []
        if self.resting[enter] == 'lower':
            x = self.data.vlowerb[enter] # +
        elif self.resting[enter] == 'upper':
            x = self.data.vupperb[enter] # -
        for i in range(0,self.data.rows):
            value = self.data.rowVals[i][enter]*x
            if value > 0:
                bounds.append(self.data.upperb[i]-value)
            else:
                bounds.append(-1*(self.data.lowerb[i]-value))
        for i in range(0,len(bounds)):
            if (exitVal > bounds[i]):
                exitVal = bounds[i]
                exit = i
        print self.data.nonbasic[exit], 'is eligible to exit'
        return exit

    def swapBounds(self,enter,exit):
        """ swaps the bounds """
        temp = self.data.lowerb[exit]
        self.data.lowerb[exit] = self.data.vlowerb[enter]
        self.data.vlowerb[enter] = temp
        temp = self.data.upperb[exit]
        self.data.upperb[exit] = self.data.vupperb[enter]
        self.data.vupperb[enter] = temp

    def pivotColumns(self,enter,exit):
        """ pivot column and rows """
        print 'pivoting columns and rows'

        # swap basic and nonbasic
        en = self.data.basic[enter]
        ex = self.data.nonbasic[exit]
        print en,'entering and',ex,'exiting'
        self.data.basic.remove(en)
        self.data.basic.insert(enter,ex)
        self.data.nonbasic.remove(ex)
        self.data.nonbasic.insert(exit,en)
        # recalculate each row's value based on which variable just entered/exited
        # calculate exit row first, then every other row
        for i in range(0,self.data.rows):
            if (i == exit):
                self.data.rowVals[i][enter] = Decimal("-1")/-self.data.rowVals[exit][enter]
                self.swapBounds(enter,exit)
            elif (i != exit):
                for j in range(0,self.data.cols):
                    # Change the entering column's value
                    if (j == enter):
                        self.data.rowVals[i][j] = self.data.rowVals[i][j]*self.data.rowVals[exit][enter]
                    # Change the non-entering colum's value
                    elif (j != enter):
                        #self.data.rowVals[i][j] = self.data.rowVals[i][j]-self.data.rowVals[i][enter]*self.data.rowVals[exit][j]
                        self.data.rowVals[i][j] = self.data.rowVals[i][enter]*self.data.rowVals[exit][j]+self.data.rowVals[i][j]
#                    print self.data.rowVals[i][j]-self.data.rowVals[i][enter]*self.data.rowVals[exit][j]
#                    print self.data.rowVals[i][j]
#                    print self.data.rowVals[i][enter]*self.data.rowVals[exit][j]
        # recalculate objective coefficients
        for i in range(0,self.data.cols):
            if (i == enter):
                self.data.objCo[i] = self.data.objCo[i]*self.data.rowVals[exit][enter]
            elif (i != enter):
                self.data.objCo[i] = self.data.objCo[i]-self.data.objCo[enter]*self.data.rowVals[exit][i]
        self.data.printMatrix()                

    def calculateZ(self):
        """ calculate the value of z """
        for i in range(0,self.data.cols):
            if (self.resting[i] == 'lower'):            
                self.z += self.data.objCo[i] * self.data.vlowerb[i]
            elif (self.resting[i] == 'upper'):            
                self.z += self.data.objCo[i] * self.data.vupperb[i]
        self.printZ()

    def solveSimplex(self):
        """ simplex """
        print 'solving via simplex...'
        i = 0
        while(self.isFeasible() and not self.isFinal() and i < 2):
            enter = self.determineEnteringVar()
            exit  = self.determineExitingVar(enter)
            self.pivotColumns(enter,exit)
            self.setResting()
            i += 1
      
    """ Print """
    def printZ(self):
        print 'solution Z =',self.z

#f = open('input.txt','r')
#f = open('inputFinal.txt','r')
f = open('inputNoInit.txt','r')
#f = open('inputOnePivot.txt','r')
#f = open('inputCycling.txt','r')
#f = open('inputDegenerate.txt','r')

d = linearProgram(f)
d.printAll()
solver = simplexSolver(d)
solver.solve()


