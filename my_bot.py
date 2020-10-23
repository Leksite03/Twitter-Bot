import tweepy
import time
import json
import datetime
import logging

logging.basicConfig(level=logging.INFO)

keys = json.load(open('my_key.json'))
'''This part of the code '''
consumer_key = keys['consumer_key']
consumer_secret = keys['consumer_secret']
access_key = keys['access_key']
access_secret = keys['access_secret']

auth =tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_key, access_secret)
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

class DscFutaBot:
    def __init__(self,api,since_id_filename,instructor_handles_filename,dsc_handles_filename,
                 keywords,search_query):
        self.api = api
        self.me = api.me()
        self.since_id_filename = since_id_filename
        self.instructor_handles_filename = instructor_handles_filename
        self.dsc_handles_filename = dsc_handles_filename
        self.keywords = keywords
        self.search_query = search_query
        self.new_since_id = []
    
    def get_last_since_id(self):
        f_read = open(self.since_id_filename, 'r')
        last_since_id = int(f_read.read().strip())
        f_read.close()
        return last_since_id

    def save_last_since_id(self,last_since_id):
        f_write = open(self.since_id_filename, 'w')
        f_write.write(str(last_since_id))
        f_write.close()
        return


    def respond_to_dscfuta_instructors(self):
        """ This function checks the timeline of the current dsc
        instructors then retweet and like any post related to developer student club"""
        since_id = self.get_last_since_id()
        instructors = json.load(open(self.instructor_handles_filename))['handles']
        for instructor in instructors:
            tweets = api.user_timeline(screen_name= instructor, since_id=since_id)
            for tweet in reversed(tweets):
                if tweet.in_reply_to_status_id is not None:
                    continue
                if any(key in tweet.text.lower() for key in self.keywords):
                    try:
                        logging.info(f'found a new tweet on {instructor}\'s timeline....')
                        time.sleep(2)
                        tweet.retweet()
                        tweet.favorite()
                        logging.info(f'successfully retweeted and liked this tweet by @{tweet.user.screen_name}')
                    except tweepy.TweepError:
                        logging.error(f'Error while retweeting and liking', exc_info=True)
                self.new_since_id.append(tweet.id)
            time.sleep(5)
            logging.info(f'Done checking {instructor}\'s timeline found no new tweet ')
        if len(self.new_since_id) != 0:
            self.save_last_since_id(max(self.new_since_id))
        self.new_since_id.clear()


    def respond_to_keywords(self):
        '''This function searches for tweets having certain keywords in it and respond to them'''
        
        since_id = self.get_last_since_id()
        results = api.search(q=self.search_query, since_id = since_id,lang='en', tweet_mode='extended')
        for tweet in reversed(results):
            if tweet._json['in_reply_to_status_id'] is not None or tweet.user.id == self.me.id:
                continue
            else:
                try:
                    logging.info(f'found a tweet by @{tweet.user.screen_name}')
                    time.sleep(3)
                    tweet.retweet()
                    tweet.favorite()
                    logging.info(f'successfully liked and retweeted post made by @{tweet.user.screen_name}')
                except tweepy.TweepError:
                    logging.error('error while liking and retweeting', exc_info=True)
            time.sleep(1)
            self.new_since_id.append(tweet._json['id'])
        else:
            logging.info("Can't find any tweet related to data science, machine learning or AI")

        if len(self.new_since_id) != 0:
            self.save_last_since_id(max(self.new_since_id))
        self.new_since_id.clear()

    def respond_to_dsc_handles(self):
        '''This fucntion retrieves information from dsc handles in various nigeria instituitions and respond to it'''
        
        since_id = self.get_last_since_id()
        dsc_handles = json.load(open(self.dsc_handles_filename))['handles']
        for dsc in dsc_handles:
            tweets = api.user_timeline(screen_name= dsc, since_id=since_id)
            for tweet in reversed(tweets):
                if tweet.in_reply_to_status_id is not None:
                    continue
                if any(key in tweet.text.lower() for key in self.keywords):
                    try:
                        logging.info(f'found a new tweet on {dsc}\'s timeline....')
                        time.sleep(2)
                        tweet.retweet()
                        tweet.favorite()
                        logging.info(f'successfully retweeted and liked this tweet by @{tweet.user.screen_name}')
                    except tweepy.TweepError:
                        logging.error(f'Error while retweeting and liking', exc_info=True)
                self.new_since_id.append(tweet.id)
            time.sleep(2)
            logging.info(f'Done checking {dsc}\'s timeline found no new tweet ')
        if len(self.new_since_id) != 0:
            self.save_last_since_id(max(self.new_since_id))
        self.new_since_id.clear()
        
    def run_dsc_bot(self):
        while True:
            logging.info('DSCFUTA BOT ACTIVATED')
            time.sleep(2)
            self.respond_to_dscfuta_instructors()
            self.respond_to_dsc_handles()
            self.respond_to_keywords()
            logging.info('\nDSCFUTA BOT Temporarily deactivated, will resume in the next 1minute.......')
            time.sleep(60)






since_id = 'since_id.txt'
instructor_handles = 'instructors.json'
dsc_handles = 'dsc_handles.json'
keywords = ['dsc', 'developer student club','developer']
search_query = f'''#MachineLearning OR #datascience OR #artificialintelligence OR
                        machine learning OR data science OR artificial intelligence
                        -filter:retweets'''

if __name__ == "__main__":
    dscbot = DscFutaBot(api,since_id,instructor_handles,dsc_handles,keywords,search_query)
    dscbot.run_dsc_bot()

  