import praw
import config
import csv

reddit = praw.Reddit(client_id = config.client_id,
                     client_secret= config.client_secret,
                    username=config.username,
                    password=config.password,
                     user_agent=config.user_agent
                     )
subreddit = reddit.subreddit('starcitizen')
hot_python = subreddit.hot(limit=10)

fields = ['Title,Score,ID,URL,Numb_Comments,created_utc,Body']
with open("reddit_test.csv", "w", encoding="utf-8", newline='') as doc:
    redcsv = csv.writer(doc, delimiter=',', escapechar='\"', quotechar='"', quoting=csv.QUOTE_ALL)
    redcsv.writerow(fields)
    for submission in hot_python:
        title = '{}'.format(submission.title)
        score = '{}'.format(submission.score)
        url = '{}'.format(submission.shortlink)
        rid = '{}'.format(submission.id_from_url(url=url))
        comm = '{}'.format(submission.num_comments)
        timestamp = '{}'.format(submission.created_utc)
        body = '{}'.format(submission.selftext)

        if not submission.stickied:
            print('Title: {}, ups: {}, downs: {}, Have we visited: {}'.format(submission.title,
                                                                            submission.ups,
                                                                            submission.downs,
                                                                            submission.visited))                                                                            
            redcsv.writerow([f'{title}, {score}, {rid}, {url}, {comm}, {timestamp}, {body}'])                                                                                                                                          
            comments = submission.comments
            for comment in comments:
                print(20*'-')
                print(comment.body)
                #doc.write(20*'-')
                #doc.write(comment.body)
                if len(comment.replies)>0:
                    for reply in comment.replies:
                        rbody = '{}'.format(reply.body)
                        print(f'REPLY: {rbody}')
                        #doc.write(f'\nREPLY: {rbody}')
doc.close()