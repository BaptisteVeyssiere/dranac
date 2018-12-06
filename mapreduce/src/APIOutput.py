import json

from Tweet import TweetManager

class APIOutput():

    @classmethod
    def sortingDates(self, i):
        datetime = i.split(':', 1)[0].replace(' ', '/')
        splitup = datetime.split('/')
        return splitup[2], splitup[1], splitup[0], splitup[3]

    @classmethod
    def sortDates(self, tweets_per_hour):
        hour_list = json.loads(tweets_per_hour)
        tweets_per_hour = [s.encode('ascii') for s in hour_list]
        return sorted(tweets_per_hour, key=self.sortingDates)
