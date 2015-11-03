import re
from lxml import html
from ch.apis import Requests, Response

class MXOptionResponse(Response):
    _MAPPING = {
        'last price:': '_lastPrice',
        'net change:': '_netChange',
        'volume:': '_volume',
        'bid price:': '_bidPrice',
        'bid size:': '_bid size',
        'open interest:': '_open interest',
        'ask price:': '_askPrice',
        'ask size:': '_askSize',
        'implied volatility:': '_impliedVolatility'
    }
    def __init__(self, requests, responseObj):
        super(MXOptionResponse, self).__init__(requests, responseObj)
        htmlTree = html.fromstring(self.getContentAsText())
        for tr in htmlTree.xpath('//div[@id="quotes"]/section/section/table/tbody/tr'):
            td = tr.xpath('./td')
            #For each header in the table row
            for i, th in enumerate(tr.xpath('./th')):
                th_text = th.text.strip().lower() if th.text is not None else ''
                #If it is a mapped name
                if th_text in self._MAPPING:
                    #Throw exception if no value is present
                    if len(td) <= i:
                        raise Exception('Failed to match value for "%s" using index %d"' % (th_text, i))
                    #Assume all values are float, trim any spacing or symbols
                    setattr(self, self._MAPPING[th_text], float(re.sub('\s*([-+]?(?:\d*[.])?\d+).*', '\g<1>', td[i].text)))
                    
    def getLastPrice(self):
        return self._lastPrice
    def getNetChange(self):
        return self._netChange
    def getVolume(self):
        return self._volume
    def getBidPrice(self):
        return self._bidPrice
    def getBidSize(self):
        return self._bidSize
    def getOpenInterest(self):
        return self._openInterest
    def getAskPrice(self):
        return self._askPrice
    def getAskSize(self):
        return self._askSize
    def getImpliedVolatility(self):
        return self._impliedVolatility
    
    def __str__(self):
        mappingStr = ""
        for mappingItem in self._MAPPING.items():
            attrName = mappingItem[1]
            mappingStr = "%s [%s->%f]" % (mappingStr, attrName, getattr(self, attrName))
        return "%s (%d): %s" %(self.__class__.__name__, 
                               self.getStatusCode(), mappingStr)
        
class MXOptionRequests(Requests):
    _api_url = None
    def __init__(self, configuration, responseHandler=MXOptionResponse):
        super(MXOptionRequests, self).__init__(
                configuration=configuration,
                responseHandler=responseHandler)
        self._api_url = configuration.getMxApiOptionsUrl()

    def getOption(self, instrument):
        data = { }
        data['instrument'] = instrument
        return super(MXOptionRequests, self).get(url=self._api_url, params=data)