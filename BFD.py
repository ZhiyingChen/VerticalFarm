# -*- coding: utf-8 -*-
"""
Created on Mon Jul 25 12:45:41 2022

@author: CZY
"""




""" Partition a list into sublists whose sums don't exceed a maximum 
    using a First Fit Decreasing algorithm. See
    http://www.ams.org/new-in-math/cover/bins1.html
    for a simple description of the method.
"""


class Bin(object):
    """ Container for items that keeps a running sum """
    def __init__(self):
        self.items = []
        self.sum = 0

    def append(self, item):
        self.items.append(item)
        self.sum += item

    def __str__(self):
        """ Printable representation """
        return 'Bin(sum=%d, items=%s)' % (self.sum, str(self.items))


def pack(values, maxValue):
    values = sorted(values, reverse=True)
    bins = []

    for item in values:
        # Try to fit item into a bin
        for bin in bins:
            if bin.sum + item <= maxValue:
                #print 'Adding', item, 'to', bin
                bin.append(item)
                break
        else:
            # item didn't fit into any bin, start a new bin
            #print 'Making new bin for', item
            bin = Bin()
            bin.append(item)
            bins.append(bin)

    return bins

def bfpack(values, maxValue):
    values = sorted(values, reverse=True)
    bins = []

    for item in values:
        # Try to fit item into a bin
        
        n = len(bins)
        tightestInd = n
        leftMin = maxValue
        for i in range(n):
            
            try:
                bin = bins[i]
                if bin.sum + item <= maxValue:
                    left = maxValue - bin.sum - item
                    if left < leftMin:
                        tightestInd = i
                
                
            except IndexError:
                bin = Bin()
                bin.append(item)
                bins.append(bin)
        try:
            bins[tightestInd].append(item)
        except IndexError:
                bin = Bin()
                bin.append(item)
                bins.append(bin)
                

    return bins
  
# Driver code  
if __name__ == '__main__':  
    blockSize = [100, 500, 200, 300, 600]  
    processSize = [212, 417, 112, 426]  
    m = len(blockSize)  
    n = len(processSize)  
  
    bestFit(blockSize, m, processSize, n) 

if __name__ == '__main__':
    import random

    def packAndShow(aList, maxValue):
        """ Pack a list into bins and show the result """
        print ('List with sum', sum(aList), 'requires at least', (sum(aList)+maxValue-1)/maxValue, 'bins')

        bins = pack(aList, maxValue)

        print ('Solution using', len(bins), 'bins:')
        for bin in bins:
            print (bin)

        print()


    aList = [10,9,8,7,6,5,4,3,2,1]
    packAndShow(aList, 11)

    aList = [random.randint(1, 11) for i in range(100)]
    packAndShow(aList, 11)