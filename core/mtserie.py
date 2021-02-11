from mts.core.utils import allowed_downsample_rule
import pandas as pd
import numpy as np
import copy


class MTSerie:
    """
    A class used to represent multivariate time series

    ...

    Attributes
    ----------
    variables : dict of np.ndarray<float>
        The variables in this dict are assumed to be time-dependent , thus, they are 
        represented as arrays of float values.
        a dict on numpy arrays of type float and length T. The number of elements
        in [variables] is D which is the number of variables. 
    variablesDates : dict of np.ndarray<DateTime>
        These dict is used in case [isDataDated] and [isDataDatedPerVariables] are true.
        a dict on numpy arrays of type DateTime and length T. The number of elements
        in [variables] is D which is the number of variables.
        It is assumed that [isDataEven] and [isDataAligned] is true. Otherwise, it will
        be empty
        
    variablesNames : list of str
        Names of the time dependent variables. These are used to make the queries in 
        [variables] and [variablesDates].
    
    dates : np.ndarray<DateTime>
        This array is used in case [isDataDated] is true and [isDataDatedPerVariables]
        is false.
        dates of the time dependent variables. Its length is equal to the length
        of each variable array in [variables].
        It is assumed that [isDataEven] and [isDataAligned] is true. Otherwise, it will
        be empty.
        
    isDataDated: boolean 
        True if time-dependent variables are dated either for each variable or for all
        variables. 
    
    isDataDatedPerVariable: boolean 
        True if time-dependent variables are dated per each variable. Otherwise all 
        time-dependent variables share same dates.
    
    isDataEven: boolean
        True if all time-dependent variables data have the same length
    
    isDataAligned: boolean
        True if all time-dependent variables data have the same length and share the 
        same dates. 
        In other words true if ([isDataEven and isDataDated and !isDataDatedPerVariable])
        
    isAnyVariableNamed: boolean
        True if a list of str of names is given to identify each time-dependent variable
        Otherwise the names in are given base on its index e.g: 0, 1, 2 ....
    
    timeLength: float or a list of floats
        if [isEven] is true then it returns the length of the time-dependent series,
        otherwise, it returns a list of floats with the length of each time serie
    
    variablesLength: float
        returns the number of time-dependent variables
    
    """

    def __init__(self):
        self.variablesNames = []
        self.variables = {}
        
        self.dates = np.array([])
        self.variablesDates = {}
        
        self.metadata = {}
        
        self.categoricalFeatures = np.array([])
        self.categoricalLabels = []
        
        self.numericalFeatures = np.array([])
        self.numericalLabels = []
        
        self.isDataDated = False
        self.isDataDatedPerVariable = False
        
        self.isDataEven = False
        self.isDataAligned = False
        
        self.isAnyVariableNamed = False
        
        self.hasNumericalFeatures = False
        self.hasCategoricalFeatures = False
        self.hasMetadata = False
        
        self.timeLength = -1
        self.variablesLength = -1
        
        super().__init__()
    
    def resample(self, rule):
        assert self.isDataEven and self.isDataAligned
        assert self.isDataDated and not self.isDataDatedPerVariable
        
        df = pd.DataFrame(self.variables)
        df['Datetime'] = self.dates
        df = df.set_index('Datetime')
        df = df.resample(rule).mean()
        
        mtserie = self.clone()
        for varName in self.variablesNames:
            mtserie.variables[varName] = df[varName].to_numpy()
            
        mtserie.dates = df.index.to_numpy()
        mtserie.timeLength = mtserie.computeTimeLength()
        # todo perhaps compute other properties that could have changed
        
        return mtserie

    def clone(self):
        mtserie = MTSerie()
        assert isinstance(mtserie, MTSerie)
        mtserie.variables = copy.deepcopy(self.variables)
        mtserie.dates = copy.deepcopy(self.dates)
        mtserie.variablesNames = copy.deepcopy(self.variablesNames)
        mtserie.dates = copy.deepcopy(self.dates)
        mtserie.metadata = copy.deepcopy(self.metadata)
        mtserie.categoricalFeatures = copy.deepcopy(self.categoricalFeatures)
        mtserie.categoricalLabels = copy.deepcopy(self.categoricalLabels)
        mtserie.isDataDated = copy.deepcopy(self.isDataDated)
        mtserie.isDataDatedPerVariable = copy.deepcopy(self.isDataDatedPerVariable)
        mtserie.isDataEven = copy.deepcopy(self.isDataEven)
        mtserie.isDataAligned = copy.deepcopy(self.isDataAligned)
        mtserie.isAnyVariableNamed = copy.deepcopy(self.isAnyVariableNamed)
        mtserie.hasNumericalFeatures = copy.deepcopy(self.hasNumericalFeatures)
        mtserie.hasCategoricalFeatures = copy.deepcopy(self.hasCategoricalFeatures)
        mtserie.hasMetadata = copy.deepcopy(self.hasMetadata)
        mtserie.timeLength = copy.deepcopy(self.timeLength)
        mtserie.variablesLength = copy.deepcopy(self.variablesLength)
        return mtserie
        
    
    def computeUniformity(self):
        seriesSize = None
        for (_, v) in self.variables.items():
            assert isinstance(v, np.ndarray)
            if seriesSize == None:
                seriesSize = len(v)
            elif seriesSize != len(v):
                return False
        return True
    
    def computeAlignment(self):
        if self.isDataDated:
            if not self.isDataDatedPerVariable:
                return True
            elif not self.isDataEven:
                return False
            else:
                for i in range(self.timeLength):
                    temp = self.variablesDates[self.variablesNames[0]][i]
                    for j in range(self.variablesLength):
                        if temp != self.variablesDates[self.variablesNames[j]][i]:
                            return False
                return True
        else:
            return True

    def computeTimeLength(self):
        if self.isDataEven:
            return len(next(iter(self.variables.values())))
        else:
            return [len(serie) for (_, serie) in self.variables.items()]
    
    def getVariablesNames(self):
        return self.variablesNames
    
    def getSerie(self, dimension):
        return self.variables[dimension]

    def removeTimeSerie(self, varName):
        del self.variables[varName]
        self.variablesNames.remove(varName)
        
        if self.isDataDated and self.isDataDatedPerVariable:
            del self.variablesDates[varName]

        self.variablesLength = self.variablesLength - 1
    
    def getCategoricalFeatures(self):
        return self.categoricalFeatures

    def getCategoricalLabels(self):
        return self.categoricalLabels
    
    def getNumericalLabels(self):
        return self.numericalLabels

    def getNumericalFeatures(self):
        return self.numericalFeatures
    
    def getDatesRange(self):
        if self.isDataDatedPerVariable:
            rangeDict = {}
            for variableName in self.variablesNames:
                rangeDict[variableName] = (self.variablesDates[variableName][0], self.variablesDates[variableName][-1])
            return rangeDict
        else:
            return (self.dates[0], self.dates[-1])
        
    # ! carefull
    def setSameRange(self, n):
        for dimension in self.variablesNames:
            self.variablesDates[dimension] = self.variablesDates[dimension][-n: ]
            self.variables[dimension] = self.variables[dimension] [-n:]
        self.length = self.calculateLength()
        
    def normalizeData(self):
        for variableName in self.variablesNames:
            x = self.variables[variableName]
            self.variables[variableName] = (x-min(x))/(max(x)-min(x))
    
    def at(self, d):
        if isinstance(d, str):
            return self.variables[d]
        else:
            return self.variables[str(d)]

    def queryByIndex(self, beginIndex, endIndex, toList = False):
        assert self.isDataEven
        assert isinstance(toList, bool)
        result = {}
        for variableName in self.variablesNames:
            serie = self.variables[variableName]
            assert isinstance(serie, np.ndarray)
            if toList:
                result[variableName] = serie[beginIndex: endIndex].tolist()
            else:
                result[variableName] = serie[beginIndex: endIndex]
        return result
    
    
    @staticmethod
    def fromNumpy(X, numericalFeatures = np.array([]), \
        categoricalFeatures = np.array([]), \
        dimensions = [], dates = [], metadata = {}, \
        categoricalLabels = [], numericalLabels = []):
        assert isinstance(X, np.ndarray) or isinstance(X, list)
        assert isinstance(dimensions, list)
        assert isinstance(dates, list)
        assert isinstance(categoricalLabels, list)
        assert isinstance(numericalLabels, list)
        assert isinstance(numericalFeatures, np.ndarray)
        assert isinstance(categoricalFeatures, np.ndarray)
        assert isinstance(metadata, dict)
        
        mtserie = MTSerie()
        
        if len(dimensions) != 0:
            assert len(dimensions) == len(X)
            mtserie.isAnyVariableNamed = True
            mtserie.variablesNames = dimensions
        else:
            mtserie.isAnyVariableNamed = False
            
            mtserie.variablesNames = [str(i) for i in range(len(X))]
        
        if len(dates) != 0:
            assert len(dates) == len(X) or len(dates) == 1
            mtserie.isDataDated = True
            if(len(dates) != 1):
                mtserie.isDataDatedPerVariable = True
        
        
        # saving the numerical features
        if len(numericalFeatures) != 0:
            mtserie.hasNumericalFeatures = True
            mtserie.numericalFeatures = numericalFeatures
        
        # saving the categorical features
        if len(categoricalFeatures) != 0:
            mtserie.hasCategoricalFeatures = True
            mtserie.categoricalFeatures = categoricalFeatures
            
        # saving the metadata
        if len(metadata) != 0:
            mtserie.hasMetadata = True
            mtserie.metadata = metadata
        
        if len(numericalLabels) != 0:
            mtserie.numericalLabels = numericalLabels
        
        if len(categoricalLabels) != 0:
            mtserie.categorialLabels = categoricalLabels
               
        # saving the time series data
        if(mtserie.isAnyVariableNamed):
            for i in range(len(X)):
                mtserie.variables[dimensions[i]] = X[i]
        else:
            for i in range(len(X)):
                mtserie.variables[str(i)] = X[i]

        # saving the dates
        if(mtserie.isDataDated):
            if(mtserie.hasDatesPerDimension):
                for i in range(len(X)):
                    if(mtserie.isAnyVariableNamed):
                        mtserie.variablesDates[dimensions[i]] = X[i]
                    else:
                        mtserie.variablesDates[str(i)] = X[i]
            else:
                mtserie.dates = dates[0]
                
        
        
        
        # calculate internal variables
        mtserie.variablesLength = len(mtserie.variablesNames)
        mtserie.isDataEven = mtserie.computeUniformity()
        mtserie.timeLength = mtserie.computeTimeLength()
        mtserie.isDataAligned = mtserie.computeAlignment()
        
        return mtserie
    
    @staticmethod
    def fromDict(X, numericalFeatures = np.array([]), \
        categoricalFeatures = np.array([]), dates = np.array([]),\
        metadata = {}, categoricalLabels = [], numericalLabels = []):
        assert isinstance(X, dict)
        assert isinstance(dates, dict) or isinstance(dates, np.ndarray)
        assert isinstance(categoricalLabels, list)
        assert isinstance(numericalLabels, list)
        assert isinstance(numericalFeatures, np.ndarray)
        assert isinstance(categoricalFeatures, np.ndarray)
        assert isinstance(metadata, dict)
        
        mtserie = MTSerie()
        
        mtserie.isAnyVariableNamed = True
        mtserie.variablesNames = list(X.keys())
        
        if isinstance(dates, np.ndarray):
            if len(dates) != 0:
                mtserie.isDataDatedPerVariable = False
                mtserie.isDataDated = True
        elif isinstance(dates, dict):
            mtserie.isDataDatedPerVariable = True
            mtserie.isDataDated = True
            
        # saving the dates
        if(mtserie.isDataDated):
            if(mtserie.isDataDatedPerVariable):
                mtserie.variablesDates = dates
            else:
                mtserie.dates = dates
                
            
        # saving the numerical features
        if len(numericalFeatures) != 0:
            mtserie.hasNumericalFeatures = True
            mtserie.numericalFeatures = numericalFeatures
        
        
        # saving the categorical features
        if len(categoricalFeatures) != 0:
            mtserie.hasCategoricalFeatures = True
            mtserie.categoricalFeatures = categoricalFeatures
            
        # saving the metadata
        if len(metadata) != 0:
            mtserie.hasMetadata = True
            mtserie.metadata = metadata
        
        if len(numericalLabels) != 0:
            mtserie.numericalLabels = numericalLabels
        
        if len(categoricalLabels) != 0:
            mtserie.categoricalLabels = categoricalLabels
               
        # saving the time series data
        mtserie.variables = X
       
        
        # calculate internal variables
        mtserie.variablesLength = len(mtserie.variablesNames)
        mtserie.isDataEven = mtserie.computeUniformity()
        mtserie.timeLength = mtserie.computeTimeLength()
        mtserie.isDataAligned = mtserie.computeAlignment()
                
        return mtserie