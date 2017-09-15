# -*- utf-8 -*-
# version 2017-09-11

# import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import math
# from texttable import Texttable
from scipy import stats


# create a score dataframe with fields 'sf', used to test some application
def exp_scoredf_normal(mean=70, std=10, maxscore=100, minscore=0, samples=100000):
    df = pd.DataFrame({'sf': [max(minscore, min(int(np.random.randn(1)*std + mean), maxscore))
                       for x in range(samples)]})
    return df


# create normal distributed data N(mean,std), [-std*stdNum, std*stdNum], sample points = size
def create_normaltable(size=400, std=1, mean=0, stdnum=4):
    """
    function
        create normal distributed data(pdf,cdf) with preset std,mean,samples size
        at interval: [-stdNum * std, std * stdNum]
    parameter
        size: samples number for create normal distributed PDF and CDF
        std:  standard difference
        mean: mean value
        stdnum: used to define data range [-std*stdNum, std*stdNum]
    return
        DataFrame: 'sv':stochastic variable, 'pdf':pdf value, 'cdf':cdf value
    """
    interval = [mean - std * stdnum, mean + std * stdnum]
    step = (2 * std * stdnum) / size
    x = [mean + interval[0] + v*step for v in range(size+1)]
    nplist = [1/(math.sqrt(2*math.pi)*std) * math.exp(-(v - mean)**2 / (2 * std**2)) for v in x]
    ndf = pd.DataFrame({'sv': x, 'pdf': nplist})
    ndf['cdf'] = ndf['pdf'].cumsum() * step
    return ndf


def read_normaltable(readrows=10000):
    """
    :function
    read normal distributed N(0,1) data from a high pricise data 100w samples in [-6, 6]
    used to make low precise data that is suitable to some applications
    :parameter
        readrows: rows to read from 100w samples with -6 and 6
    :return
        dataframe['No','sv','pdf','cdf']
    """
    if type(readrows) == int:
        skipv = int(1000000/readrows)
        skiprowlist = [x if x % skipv != 0 else -1 for x in range(1000000)]
        skiprowlist = list(set(skiprowlist))
        if -1 in skiprowlist:
            skiprowlist.remove(-1)
        if 1 in skiprowlist:
            skiprowlist.remove(1)
    else:
        skiprowlist = []
    nt = pd.read_csv('normaldist100w.csv',
                     dtype={'sv': np.float32, 'cdf': np.float64, 'pdf': np.float64},
                     skiprows=skiprowlist)
    return nt


# use scipy.stats descibe report dataframe info
def report_stats_describe(dataframe, decnum=4):
    """
    峰度（Kurtosis）与偏态（Skewness）就是量测数据正态分布特性的两个指标。
    峰度衡量数据分布的平坦度（flatness）。尾部大的数据分布峰度值较大。正态分布的峰度值为3。
        Kurtosis = 1/N * Sigma(Xi-Xbar)**4 / (1/N * Sigma(Xi-Xbar)**2)**2
    偏态量度对称性。0 是标准对称性正态分布。右（正）偏态表明平均值大于中位数，反之为左（负）偏态。
        Skewness = 1/N * Sigma(Xi-Xbar)**3 / (1/N * Sigma(Xi-Xbar)**2)**3/2
    :param
        dataframe: pandas DataFrame, raw data
        decnum: decimal number in report print
    :return(print)
        records
        min,max
        mean
        variance
        skewness
        kurtosis
    """
    def toround(listvalue, rdecnum):
        return '  '.join([f'%(v).{rdecnum}f' % {'v': round(x, rdecnum)} for x in listvalue])
    # for key, value in stats.describe(dataframe)._asdict().items():
    #    print(key, ':', value)
    sd = stats.describe(dataframe)
    print('\trecords: ', sd.nobs)
    print('\tmin: ', toround(sd.minmax[0], 0))
    print('\tmax: ', toround(sd.minmax[1], 0))
    print('\tmean: ', toround(sd.mean, decnum))
    print('\tvariance: ', toround(sd.variance, decnum))
    print('\tskewness: ', toround(sd.skewness, decnum))
    print('\tkurtosis: ', toround(sd.kurtosis, decnum))
    dict = {'records': sd.nobs, 'max': sd.minmax[1], 'min': sd.minmax[0],
            'mean': sd.mean, 'variance': sd.variance, 'skewness': sd.skewness,
            'kurtosis': sd.kurtosis}
    return dict

# segment table for score dataframe
# version 0915-2017
class SegTable(object):
    """
    :raw data 
        rawdf: dataframe, with a value field(int,float) to calculate segment table
           segfields, list, field names to calculate, empty for calculate all fields
    :parameters
        segmax: int,  maxvalue for segment, default=150
        segmin: int, minvalue for segment, default=0
        segstep: int, levels for segment value, default=1
        segsort: str, 'ascending' or 'descending', default='descending'(sort seg descending)
    :result
        segdf: dataframe with field 'seg, segfield_count, segfield_cumsum, segfield_percent'
    example:
        seg = py2ee_lib.SegTable()
        df = pd.DataFrame({'sf':[i for i in range(1000)]})
        seg.set_data(df, 'sf')
        seg.set_parameters(segmax=100, segmin=1, segstep=1, segsort='descending')
        seg.run()
        seg.segdf    #result dataframe, with fields: sf, sf_count, sf_cumsum, sf_percent
    Note:
        segmax and segmin can be used to constrain score value scope in [segmin, segmax]
        score fields type is int
    """

    def __init__(self):
        self.__rawDf = None
        self.__segFields = []
        self.__segStep = 1
        self.__segMax = 150
        self.__segMin = 0
        self.__segSort = 'descending'
        self.__segDf = None
        return

    @property
    def segdf(self):
        return self.__segDf

    @segdf.setter
    def segdf(self, df):
        self.__segDf = df

    @property
    def rawdf(self):
        return self.__rawDf

    @property
    def segfields(self):
        return self.__segFields

    @segfields.setter
    def segfields(self, sfs):
        self.__segFields = sfs

    def set_data(self, df, segfields):
        self.__rawDf = df
        self.__segFields = segfields

    def set_parameters(self, segmax=100, segmin=0, segstep=1, segsort='descending'):
        self.__segMax = segmax
        self.__segMin = segmin
        self.__segStep = segstep
        self.__segSort = segsort

    def show_parameters(self):
        print('seg max value:{}'.format(self.__segMax))
        print('seg min value:{}'.format(self.__segMin))
        print('seg step value:{}'.format(self.__segStep))
        print('seg sort mode:{}'.format(self.__segSort))

    def check(self):
        if type(self.__rawDf) == pd.Series:
            self.__rawDf = pd.DataFrame(self.__rawDf)
        if type(self.__rawDf) != pd.DataFrame:
            print('data set is not ready!')
            return False
        if self.__segMax <= self.__segMin:
            print('segmax value is not greater than segmin!')
            return False
        if (self.__segStep <= 0) | (self.__segStep > self.__segMax):
            print('segstep is too small or big!')
            return False
        if type(self.segfields) != list:
            if type(self.segfields) == str:
                self.segfields = [self.segfields]
            else:
                print('segfields error:', type(self.segfields))
                return False
            for f in self.segfields:
                if f not in self.rawdf.columns.values:
                    print('field in segfields is not in rawdf:', f)
                    return False
            return True
        return True

    def run(self):
        if not self.check():
            return
        # create output dataframe with segstep = 1
        seglist = [x for x in range(self.__segMin, self.__segMax + 1)]
        self.segdf = pd.DataFrame({'seg': seglist})
        if not self.segfields:
            self.segfields = self.rawdf.columns.values
        for f in self.segfields:
            r = self.rawdf.groupby(f)[f].count()
            self.segdf[f + '_count'] = self.segdf['seg'].\
                apply(lambda x: np.int64(r[x]) if x in r.index else 0)
            if self.__segSort != 'ascending':
                self.segdf = self.segdf.sort_values(by='seg', ascending=False)
            self.segdf[f + '_cumsum'] = self.__segDf[f + '_count'].cumsum()
            maxsum = max(max(self.segdf[f + '_cumsum']), 1)
            self.segdf[f + '_percent'] = self.segdf[f + '_cumsum'].apply(lambda x: x / maxsum)
            if self.__segStep > 1:
                segcountname = f+'_count{0}'.format(self.__segStep)
                self.segdf[segcountname] = np.int64(-1)
                c = 0
                curpoint, curstep = ((self.__segMin, self.__segStep)
                                     if self.__segSort == 'ascending' else
                                     (self.__segMax, -self.__segStep))
                for index, row in self.segdf.iterrows():
                    c += row[f+'_count']
                    if np.int64(row['seg']) in [curpoint, self.__segMax, self.__segMin]:
                        # row[segcountname] = c
                        self.segdf.loc[index, segcountname] = c
                        c = 0
                        curpoint += curstep
        return
# SegTable class end
