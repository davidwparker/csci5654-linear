from decimal import Decimal

class linearProgram:
    """ Class to parse input file and setup all the variables """
    import re
    commaDelimitedPattern = re.compile(',')
    # instance variables
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
        self.offset = 0
        self.rowCol = 0
        self.rows = 0
        self.cols = 0
        self.rowVals = []
        self.objCo = []
        self.lowerb = []
        self.upperb = []
        self.vlowerb = []
        self.vupperb = []   
        self.basic = []
        self.nonbasic = []
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
                self.basic.append('x'+str(i+1))
        if self.nonbasic == []:
            for i in range(0,self.rows):
                self.nonbasic.append('w'+str(i+1))

    """ Print """
    def printAll(self):
        print 'Parsed file with the following INPUTS:'
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
        print 'MATRIX: '
        for i in range(0,self.rows):
            stmt = ''
            for j in range(0,self.cols):
                stmt += str(self.rowVals[i][j])
                stmt += '*'
                stmt += self.basic[j]
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
    """ Class to solve a simplex problem via an linearProgram object """
    # Instance variables
    resting = []
    bounds = []
    w = []
    e = []
    newObjCo = []
    z = 0

    def __init__(self, input):
        self.resting = []
        self.bounds = []
        self.w = []
        self.e = []
        self.newObjCo = []
        self.z = 0
        self.data = input

    def solve(self):
        if printDetails: print '\nsolving...'
        self.initialize()
        self.solveSimplex()

    def initialize(self):
        if printDetails: print 'initializing...'
        self.formInitialDictionary()
        self.calculateRows()
        if not(self.isFeasible()):
            self.createEvariables()
            self.changeObjective()
            self.solveSimplex()
            self.removeEvariables()

    def formInitialDictionary(self):
        """ need to choose starting resting variables here """
        if printDetails: print 'forming initial dictionary...'
        self.setInitResting()
    
    def setInitResting(self):
        """ set resting variable upper or lower """
        if printDetails: print 'setting resting variables...'
        self.resting = []
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
        #print self.resting
        
    def calculateRows(self):
        """ calculate the row values to check if within bounds  """
        self.w = []
        for i in range(0,self.data.rows):
            sum = Decimal('0')
            for j in range(0,self.data.cols):
                # calculate sum t
                if (self.resting[j] == 'lower'):
                    #TODO: remove this once solved +/- infinity?
                    if self.data.vlowerb[j].is_finite():
                        #print j, self.data.rowVals[i][j] * self.data.vlowerb[j]
                        sum += self.data.rowVals[i][j] * self.data.vlowerb[j]
                    else:
                        sum += 0
                elif (self.resting[j] == 'upper'):
                    #TODO: remove this once solved +/- infinity?
                    if self.data.vupperb[j].is_finite():
                        #print j, self.data.rowVals[i][j] * self.data.vupperb[j]
                        sum += self.data.rowVals[i][j] * self.data.vupperb[j]
                    else:
                        sum += 0
            #print sum
            self.w.append(sum)
        #print self.w

    
    def isFeasible(self):
        """ check values of w's... """
        if printDetails: print 'checking if feasible...'
        for i in range(0,self.data.rows):
            # check versus lower and upper bounds
            #print i, self.w[i], self.data.lowerb[i], self.data.upperb[i] 
            if (self.w[i] > self.data.upperb[i]):
                if printDetails: print 'infeasible too high...'
                return False
            if (self.w[i] < self.data.lowerb[i]):
                if printDetails: print 'infeasible too low...'
                return False
        if printDetails: print 'feasible... moving on.'
        return True

    def isFinal(self):
        """ check if dictionary is final """
        if printDetails: print 'checking if final...'
        isFinal = True
        for i in range(0,self.data.cols):
            if (self.resting[i] == 'upper'):
                if (self.data.objCo[i] < 0):
                    isFinal = False
            elif (self.resting[i] == 'lower'):
                if (self.data.objCo[i] >= 0):
                    isFinal = False
        if (isFinal):
            if printDetails: print 'Final Dictionary Found!'
        return isFinal

    def createEvariables(self):
        """ if infeasible (w outside bounds), then create variables e to add/subtract from row """
        #TODO fix this!
        if printDetails: print 'creating e variables...'
        for i in range(0,self.data.rows):
            if (self.w[i] > self.data.upperb[i]):
                # create subtraction e
                if printDetails: print 'row #', i, '(', self.w[i], ') too high > ', self.data.upperb[i], 'subtracting e'
                self.e.append(Decimal('-1'))
                #self.data.rowVals[i].append(Decimal('-1'))
            elif (self.w[i] < self.data.lowerb[i]):
                # create addition e
                if printDetails: print 'row #', i, '(', self.w[i], ') too low <', self.data.lowerb[i], 'adding e'
                self.e.append(Decimal('1'))
                #self.data.rowVals[i].append(Decimal('1'))
            else:
                self.e.append(Decimal('0'))
                #self.data.rowVals[i].append(Decimal('0'))
        #print self.e
        #print self.data.rowVals

    def removeEvariables(self):
        """ remove the e's and reintroduce the original objective in terms of w's """
        #TODO this!
        if printDetails: print 'removing e variables...'

    def changeObjective(self):
        """ change objective function to minimize variables e """
        #TODO this!
        if printDetails: print 'changing objective...'
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
        if printDetails: print 'determining the entering variable...'
        for i in range(0,self.data.cols):
            #TODO: make this so it doesn't just select the first eligible?
            if (self.resting[i] == 'lower' and self.data.objCo[i] >= 0):
                if printDetails: print self.data.basic[i], 'is eligible to enter.'
                return i
            elif (self.resting[i] == 'upper' and self.data.objCo[i] < 0):
                if printDetails: print self.data.basic[i], 'is eligible to enter.'
                return i

    def determineExitingVar(self,enter):
        """ determines the exiting variable """
        if printDetails: print 'determining the exiting variable...'
        restingVal = 0
        exitingVal = Decimal("Infinity")
        exit = {'value':-1,'bound':'lower'}
        bounds = []
        if self.resting[enter] == 'lower':
            restingVal = self.data.vlowerb[enter] # +
        elif self.resting[enter] == 'upper':
            restingVal = self.data.vupperb[enter] # -
        for i in range(0,self.data.rows):
            rowVal = self.data.rowVals[i][enter]
            value = rowVal*restingVal
            ubound = self.data.upperb[i]-value
            # TOOD: check for division by zero?
            ubound /= rowVal
            lbound = self.data.lowerb[i]-value
            lbound /= rowVal
            if (rowVal < 0):
                tmp = {'v':lbound,'bound':'lower'}
                bounds.append(tmp)
            else:
                tmp = {'v':ubound,'bound':'upper'}
                bounds.append(tmp)
        for i in range(0,len(bounds)):
            if (exitingVal > bounds[i]['v']):
                exitingVal = bounds[i]['v']
                exit['value'] = i
                exit['bound'] = bounds[i]['bound']
        if printDetails: print self.data.nonbasic[exit['value']], 'is eligible to exit.'
        return exit

    def setResting(self,enter,bound):
        """ set resting variable upper or lower """
        if printDetails: print 'setting resting variables...'
        self.resting[enter] = bound

    def swapBounds(self,enter,exit):
        """ swaps the bounds """
        if printDetails: print 'swapping the bounds...'
        temp = self.data.lowerb[exit]
        self.data.lowerb[exit] = self.data.vlowerb[enter]
        self.data.vlowerb[enter] = temp
        temp = self.data.upperb[exit]
        self.data.upperb[exit] = self.data.vupperb[enter]
        self.data.vupperb[enter] = temp

    def swapBasicNonbasic(self,enter,exit):
        """ swaps the basic and nonbasic variables """
        if printDetails: print 'swapping the basic and nonbasic variables...'
        en = self.data.basic[enter]
        ex = self.data.nonbasic[exit]
        if printDetails: print en,'entering and',ex,'exiting...'
        self.data.basic.remove(en)
        self.data.basic.insert(enter,ex)
        self.data.nonbasic.remove(ex)
        self.data.nonbasic.insert(exit,en)

    def pivotExitRow(self,enter,exit):
        """ pivots the exit row """
        if printDetails: print 'pivoting the exit row...'
        # calculate exit row first, then every other row
        oldVal = self.data.rowVals[exit][enter]
        for i in range(0,self.data.rows):
            if (i == exit):
                for j in range(0,self.data.cols):
                    if (j == enter):
                        self.data.rowVals[exit][enter] = Decimal("-1")/-oldVal
                    elif (j != enter):
                        self.data.rowVals[i][j] = self.data.rowVals[i][j]/-oldVal

    def pivotNonExitRows(self,enter,exit):
        """ pivots the non exit rows """
        if printDetails: print 'pivoting non-exit rows...'
        # Not the exit row
        for i in range(0,self.data.rows):
            if (i != exit):
                enterVal = self.data.rowVals[i][enter]
                for j in range(0,self.data.cols):
                    # Change the entering column's value
                    if (j == enter):
                        self.data.rowVals[i][j] = enterVal*self.data.rowVals[exit][j]
                    # Change the non-entering column's value
                    elif (j != enter):
                        self.data.rowVals[i][j] = enterVal*self.data.rowVals[exit][j]+self.data.rowVals[i][j]

    def updateObjective(self,enter,exit):
        """ updates the objective coefficients """
        if printDetails: print 'updating the objective coefficient...'
        # recalculate objective coefficients
        objEnterVal = self.data.objCo[enter]
        self.data.objCo[enter] = objEnterVal*self.data.rowVals[exit][enter]
        for i in range(0,self.data.cols):
            if (i != enter):
                self.data.objCo[i] = objEnterVal*self.data.rowVals[exit][i]+self.data.objCo[i]

    def pivotColumns(self,enter,exit):
        """ pivot column and rows """
        if printDetails: print 'pivoting columns and rows...'
        self.swapBasicNonbasic(enter,exit)
        self.swapBounds(enter,exit)
        self.pivotExitRow(enter,exit)
        self.pivotNonExitRows(enter,exit)
        self.updateObjective(enter,exit)
    
    def calculateZ(self):
        """ calculate the value of z """
        if printDetails: print 'calculating z...'
        self.z = 0
        for i in range(0,self.data.cols):
            if (self.resting[i] == 'lower'):
                self.z += self.data.objCo[i] * self.data.vlowerb[i]
            elif (self.resting[i] == 'upper'):
                self.z += self.data.objCo[i] * self.data.vupperb[i]
        self.printZ()

    def solveSimplex(self):
        """ simplex """
        if printDetails: print 'solving via simplex...'
        # Max number of iterations to not be stuck in infinite loop
        MAX = 500
        i = 0
        final = self.isFinal()
        while(not final and self.isFeasible() and i < MAX):
            enter = self.determineEnteringVar()
            exit  = self.determineExitingVar(enter)
            self.pivotColumns(enter,exit['value'])
            self.data.printMatrix()
            self.setResting(enter,exit['bound'])
            self.calculateRows()
            final = self.isFinal()
            print 'final?', final
            print self.resting
            i += 1
        if (final):
            print 'FINAL',self.data.printMatrix()
            self.calculateZ()
      
    """ Print """
    def printZ(self):
        print 'solution Z =',self.z
    def printResting(self):
        print 'resting =',self.resting

# Iterate through all of the different types of inputs that we think of...
# Original input from Sriram's programming assignment
#   inputOriginal.txt
# Input that is already in the final format
#   inputFinal.txt
# Input that needs to be initialized (lp-initial-general.pdf)
#   inputInitialize.txt
# Input that doesn't require initialization (lecture 10, slides 10+)
#   inputNoInit.txt
# Input that cycles (requires blands rule)
#   inputCycling.txt
# Input that demonstrates degeneracy
#   inputDegenerate.txt

linearPrograms = [
    'inputOriginal.txt',
    'inputFinal.txt',
    'inputInitialize.txt',
    'inputNoInit.txt',
    #'inputCycling.txt',
    #'inputDegenerate.txt'
    ]

printDetails = True

for lp in linearPrograms:
    with open(lp,'r') as f:
        print '\n','Solving lp:',lp
        d = linearProgram(f)
        if printDetails: d.printAll()
        solver = simplexSolver(d)
        solver.solve()
    
