import praw
import nltk
import time
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine
import pymysql
pymysql.install_as_MySQLdb()
import mysql.connector
from mysql.connector import Error
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

import matplotlib.pyplot as plt

import config

sia = SentimentIntensityAnalyzer()
#connect to reddit client

reddit = praw.Reddit(client_id=config.client_id,
                     client_secret=config.client_secret,
                     user_agent=config.user_agent)

password = config.password


#connect to mysql method to add data to the IBKR
def connect(timestamp_ms, reddit_sentiment, reddit_comm_sentiment, news_sentiment):

    try:
        con = mysql.connector.connect(
        host = 'localhost',
        #database='ibpy',
        database='twitterdb', 
        user='root', 
        password = password)

        if con.is_connected():

            cursor = con.cursor()
            # connect this to the IBKR DB
            # CREATE IBKR DATA ON ibpy and then append to it
            query = "INSERT INTO rednewsDB (timestamp_ms, reddit_sentiment, reddit_comm_sentiment, news_sentiment) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (timestamp_ms, reddit_sentiment, reddit_comm_sentiment, news_sentiment))
            con.commit()
            
            
    except Error as e:
    
        print(e)

    cursor.close()
    con.close()

    return

# changes a string to datetime format
def toDateTime(yabadabadoo):
    toDateTime = datetime.strptime(yabadabadoo, '%Y-%m-%d %H:%M:%S')
    return toDateTime


################################################### change to connect to the main df from ibpy
# gets the time from the main database 
def getTime():
    date = []
    try:
        con = mysql.connector.connect(
        host = 'localhost',
        #database='ibpy',
        database='twitterdb', 
        user='root', 
        password = password)

        cursor = con.cursor()
        query = "select * from TwitterSent"
        cursor.execute(query)
        # get all records
        db = cursor.fetchall()

        df = pd.DataFrame(db)

        date.append(df[0].iloc[-1])
        date.append(df[0].iloc[-2])


    except mysql.connector.Error as e:
        print("Error reading data from MySQL table", e)

    cursor.close()
    con.close()

    return date

# will get scores of each post
def getRedditSentiment():
    scoreList = []
    score = 0
    submissions = 0

    # change this so that the ticker can be changed externally 
    # chooses the top posts 
    hot_posts = reddit.subreddit(config.stock).hot()
    # will get reddit and comment score

    for submission in hot_posts:
        # will store in vs and append it all into a list and compact it
        vs = sia.polarity_scores(submission.title)
        sentiment = vs['compound']

        # adds onto the score list
        scoreList.append(sentiment)
        submissions += 1
        

    for x in scoreList:
        score += x

    score = score/submissions

    return score



def getNewSentiment():
    score = 0
    return score


def getMarketSentiment():
    score = 0
    return score

# returns a df of the twitter data organized by the minute
def df_resample_sizes():
    try:
        con = mysql.connector.connect(
        host = 'localhost',
        database='twitterdb', 
        user='root', 
        password = password)

        cursor = con.cursor()
        query = "select * from TwitterSent"
        cursor.execute(query)
        # get all records
        db = cursor.fetchall()

        df = pd.DataFrame(db)

    except mysql.connector.Error as e:
        print("Error reading data from MySQL table", e)

    cursor.close()
    con.close()

    Holder_List = []
    holder = df[0]
    holder = toDateTime(holder[0])
    holder = holder.minute
    counter = 0
    total = 0


    df1 = pd.DataFrame(columns = ['timestamp_ms', 'tweetsent'])

    for index, row in df.iterrows():
        date1 = toDateTime(row[0])
        date = date1.minute
        if(date != holder):
            holder = date
            total = sum(Holder_List)
            try:
                total = total/counter  # will have to use later after i implement rounding on tssmysql     
                total = round(total, 4)
            except ZeroDivisionError as e:
                pass


            date1 = date1.replace(second=0)
            df1 = df1.append({'timestamp_ms':date1, 'tweetsent':total}, ignore_index=True)
            #print(date, total) #shows the condensed data organized

            #resets the params
            total = 0
            Holder_List = []
            counter = 0

        else:
            Holder_List.append(float(row[1]))
            counter = counter + 1

    df1['tweetsent'] = df1['tweetsent'].rolling(int(len(df1)/5)).mean()

    return df1


def main():
    run = True
    timeout = time.time() + 1
    timeCompare = getTime()
    timeNow = toDateTime(timeCompare[0])

    #df.to_sql(con=con, name='tweetdb', if_exists='replace')


    # constantly refreshes to check if there is a new ticker update
    while(run):

        timeCompare = getTime()
        timePast = toDateTime(timeCompare[1])

        # whenever we detect that interactive brokers data has updated into the mysql database
        # we will add to our table and then join to it
        # IF THERE IS A NEW TICKER
        if timePast == timeNow:
            #add
            timeNow = toDateTime(timeCompare[0])
            # GET THE SENTIMENT FROM THE TWITTER AND STORE IT ALL TOGETHER
            # STORE INTO MYSQL DB

            #works LOL
            df = df_resample_sizes()
            engine = create_engine(config.engine)
            with engine.begin() as connection:
                df.to_sql(name='tweetdb', con=connection, if_exists='append', index=False)


            connect(timeNow, getRedditSentiment(), )




            # use to connect method to store into the db
            # (timestamp, twitter, reddit, news on stock from finviz, overall stock news s&p500, s&p500 data?)
            #connect(timeNow, )
            # then join it to the main table


        # use if necessary
        #time.sleep(1)




        # kills main after a certain amount of time
        test = 0
        if test == 5 or time.time() > timeout:
            run = False
            break
        test = test - 1




if __name__== '__main__':
    main()





