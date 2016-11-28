import boto3
from multiprocessing.dummy import Pool as ThreadPool

from elasticsearch import RequestsHttpConnection

from alchemyapi import AlchemyAPI
from elasticsearch import Elasticsearch
from datetime import datetime


sqs = boto3.resource('sqs', region_name="us-west-2")
q = sqs.get_queue_by_name(QueueName='drumil_Queue_test')
print q.url
alchemyapi = AlchemyAPI()
snsClient = boto3.client('sns', region_name="us-west-2")

host = "search-tweet21-h25el5zjzgy7jgosb77uhbbe4a.us-west-2.es.amazonaws.com"
port = 443

#create ES object here
es = Elasticsearch(
        hosts=[{'host': host, 'port': port}],
        use_ssl=True,
        # http_auth=awsauth,
        verify_certs=True,
        connection_class=RequestsHttpConnection
        )

print(es.info())


def getSQSQueue(n):
    try:
    # code to retrieve all text data from the SQS
        for message in q.receive_messages(MessageAttributeNames=['location']):
            text = message.body
            #print  text
            res_al = alchemyapi.sentiment("text", text)
            sentiment = res_al["docSentiment"]["type"]
            print "Sentiment of Tweet is: ", sentiment
            loc = message.message_attributes.get('location').get('StringValue')
            print loc
            es.index(index='cloud_tweet',doc_type='twitter',
                     body={
                         'content':text,
                         'location':loc,
                         'sentiment':sentiment,
                     })

                # insert into es index (tweet text,location,sentiment)

        return text
    except:
        print "Senti or ES Index Failed"


# function to be mapped over
def calculateParallel(numbers, threads):
    # configuring the worker pool

    pool = ThreadPool()
    results = pool.map(getSQSQueue,numbers)
    pool.close()
    pool.join()
    return results




if __name__ == "__main__":
    numbers = [1, 2, 3, 4, 5, 6]

    for n in range(50):
        tweet_text = calculateParallel(numbers, 10)
        #print "Tweet is ", tweet_text
        print n
    response = snsClient.publish(TopicArn='arn:aws:sns:us-west-2:343185295102:SampleDrumilTopic',
                             Message='Sentiment Created and tweets indexed',
                             Subject='Indexing',
                             )
    if response is not None:
        print ("Notification Sent", response)
