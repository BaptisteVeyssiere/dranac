import json

from tweet import TweetManager

class APIOutput():

    @classmethod
    def sortingDates(self, i):
        """sorting function used to sort the tweets_per_hour list"""
        datetime = i.split(':', 1)[0].replace(' ', '/')
        splitup = datetime.split('/')
        return splitup[2], splitup[1], splitup[0], splitup[3]

    @classmethod
    def sortDates(self, tweets_per_hour):
        """Sort the tweets_per_hour list by date"""
        hour_list = json.loads(tweets_per_hour)
        tweets_per_hour = [s.encode('ascii') for s in hour_list]
        return sorted(tweets_per_hour, key=self.sortingDates)
