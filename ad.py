class Ad(object):
    def __init__(self, adID:int, nextPromotionUnix:int):
        self.adID:int = adID
        self.nextPromotionUnix:int = nextPromotionUnix

    def getAdID(self):
        return self.adID

