import boto3
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
from tweepy import Stream
import time
import json

con_key ='XsN14NyGhAMumZ5TCpYwnSnzI'
con_secret ='3omWnyyBhlZPCNMoBR3GGpXsIzzjCHl4XKfh3gQqxWDXSY5u6G'
acess_token ='114146024-DqyhbCcLnrefWB1pAVv0533VoDR8E3t1ZMuYpxgZ'
acess_secret = 'p6E13yqgqRCHuy26UcVLFdIG1F4mWpaMRsfB5kfyzrN0x'


sqs = boto3.resource('sqs', region_name="us-west-2")

# queue = sqs.create_queue(QueueName ='drumil_Queue_test', Attributes={'DelaySeconds':'5'})
q = sqs.get_queue_by_name(QueueName='drumil_Queue_test')
print (q.url)
print(q.attributes.get('DelaySeconds'))
#res = q.send_message(MessageBody="FirstData")


class listener(StreamListener):

    def on_data(self, raw_data):

        print raw_data
        all_data = json.loads(raw_data)
        loc_en = all_data["user"]["geo_enabled"]
        lang = all_data["user"]["lang"]

        if 'text' in all_data and loc_en and lang=="en":

            tweets = all_data["retweeted_status"]["text"]

            username = all_data["user"]["screen_name"]
            location = all_data["user"]["location"]

            response = q.send_message(MessageBody=tweets,
                                          MessageAttributes={
                                              'language': {
                                                  'DataType': 'String',
                                                  'StringValue': lang
                                              },
                                              'location': {
                                                  'DataType': 'String',
                                                  'StringValue': location
                                              }
                                          })



           # print (response.get('Failed'))

       ## print ((username,tweets))
    def on_error(self, status_code):
        print status_code

    def on_connect(self):
        print self

auth = OAuthHandler(con_key, con_secret)
auth.set_access_token(acess_token, acess_secret)

twitterStream = Stream(auth, listener())
terms = [
        'elections', 'cloud computing', 'nyc', 'new year'
        ,'india','usa','dhoni','microsoft','apple'
        ,'hollywood','bollywood'
        ]

while True:
    try: twitterStream.filter(track=terms)
    except:continue

