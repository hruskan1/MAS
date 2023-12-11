import numpy as np
import sys
from scipy.stats import rv_continuous
from dataclasses import dataclass
import scipy 
import scipy.stats as stats


@dataclass
class _DistParam:
    # This is just to make scipy.fit happy, ignore it. ;)
    name: str = ""
    integrality: bool = False
    domain: object = (-np.inf, np.inf)


class OrderStatisticNormal(rv_continuous):
    """Order statistic of a normal distribution.

    Attributes
        n: sample size,
        k: the k'th-smallest value.
    """

    def __init__(self, n, k, *args, **kwargs):
        super(OrderStatisticNormal, self).__init__(*args, **kwargs)
        self.n = n
        self.k = k

    def _shape_info(self):
        return [_DistParam("mean"), _DistParam("sd", domain=(0, np.inf))]

    def _pdf(self, x, mean, sd):
        """Evaluates the PDF of the order statistic of a normal distribution"""

        # Implement this if you want to use 'scipy.fit()'
        fx = stats.norm.pdf(x,loc=mean,scale=sd)
        Fx = stats.norm.cdf(x,loc=mean,scale=sd) 
        
        fkx = self.k * scipy.special.comb(self.n,self.k) * Fx **(self.k-1) * (1-Fx)**(self.n-self.k) * fx
        return fkx

    def _cdf(self, x, mean, sd):
        """Evaluates the CDF of the order statistic of a normal distribution"""

        # (Optional for testing) Helps generate samples with '.rvs()'.
        
        Fx = stats.norm.cdf(x,loc=mean,scale=sd) 
        summands = np.stack([scipy.special.comb(self.n,j) *  Fx**j * (1-Fx)**(self.n-j) for j in np.arange(self.k,self.n+1,1)])
        summ = np.sum(summands,axis=0)
        
        return summ


def read_input(io):
    """Parses the private value, the number of participating bidders, and
    the list of past winning bids.
    """

    flt = np.vectorize(float)

    str_private, str_bidders = io.readline().split()
    private, bidders = flt(str_private), np.int32(str_bidders)          
    history = np.array(flt(io.readlines()))

    return private, bidders, history


if __name__ == "__main__":
    private, bidders, history = read_input(sys.stdin)
    # print(f"{private=}")
    # print(f"{bidders=}")
    # print(f"{history=}")
    # 1) Fit the distribution.
    Y = OrderStatisticNormal(bidders,bidders-1)
    bounds = {'mean' : (0,np.max(history)),'sd' : (0,2*np.max(history))}
    y = stats.fit(Y,history,bounds) 
    if y.success:
        est_mean = y.params.mean    
        est_sd = y.params.sd   
    else:
        raise RuntimeError('The fit function could not fit history!') 
    # print(f"{est_mean=}")
    # print(f"{est_sd=}")
    
    # 1a) Test data
    # data = Y.rvs(mean=10,sd=2,size=1000)
    # bounds = {'mean' : (0,np.max(data)),'sd' : (0,np.max(data))}
    # y = stats.fit(Y,data,bounds=bounds)
    # if y.success: 
    #     print(f"{y.params._fields=}")
    #     est_mean = y.params.mean    
    #     est_sd = y.params.sd   
    
    # 2) Estimate the optimal bid.
    # a)
    Z = OrderStatisticNormal(bidders-1,bidders-1)
    bid_to_submit = Z.expect(lambda x : x, (est_mean,est_sd),lb=-np.inf,ub=private,conditional=True) # Should be True,right
    
    # b) Law of large numbers
    large_number = 100
    truncated_rv = stats.truncnorm(a=-np.inf,b=private,loc=est_mean,scale=est_sd)
    samples = truncated_rv.rvs(size=(bidders-1,large_number))
    lln_bid_est = np.mean(np.max(samples,axis=0))

    print(f"{lln_bid_est}") 
    print(f"{bid_to_submit}")