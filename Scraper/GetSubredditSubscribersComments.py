# NOTES
#
#  * Should add associated subreddit to user entry.
#  * Users should get inserted as they're scraped. Maybe use database
#    to hold users instead of a dict? Or enter users into db as they're
#    entered in the dict

import time
import csv
import datetime
import os

from sqlalchemy.orm import Session

import praw
from sqlalchemy import distinct

from scraper.GetSubredditSubscribers import SubredditScraper
from scraper.datamodel import User, Comment, init_db
import scraper.database as db

post_limit = 1000
comment_limit = 1000
list_of_subreddits = ["funny","AskReddit","announcements","pics","todayilearned","worldnews","science","IAmA","blog","videos","gaming","movies","Music","aww","news","gifs","askscience","explainlikeimfive","technology","EarthPorn","books","bestof","television","WTF","AdviceAnimals","LifeProTips","sports","mildlyinteresting","DIY","Fitness","Showerthoughts","space","tifu","Jokes","food","photoshopbattles","InternetIsBeautiful","GetMotivated","history","gadgets","nottheonion","dataisbeautiful","Futurology","politics","Documentaries","listentothis","personalfinance","philosophy","nosleep","Art","OldSchoolCool","creepy","UpliftingNews","WritingPrompts","TwoXChromosomes","atheism","reddit.com","woahdude","gonewild","trees","leagueoflegends","chan","programming","Games","fffffffuuuuuuuuuuuu","sex","nsfw","Android","reactiongifs","cringepics","gameofthrones","malefashionadvice","Frugal","YouShouldKnow","ImGoingToHellForThis","pokemon","interestingasfuck","HistoryPorn","RealGirls","Minecraft","comics","AskHistorians","lifehacks","pcmasterrace","tattoos","Unexpected","JusticePorn","nfl","NSFW_GIF","FoodPorn","BlackPeopleTwitter","facepalm","soccer","wheredidthesodago","europe","wallpapers","cringe","TrueReddit","gentlemanboners","freebies"]
starttime = time.time()

init_db()
s = SubredditScraper()


start = time.time()

for subreddit in list_of_subreddits:
    s.scrapeSubredditUsers(target_subreddit= subreddit, nposts=post_limit)
end = time.time()

print("Time elapsed to scrape %d posts: %d seconds" % (comment_limit, int(end-start)))
print("# Unique subreddit users found: %d" % len(s.authors))

session = Session() # Aaaaaand this -- RMD

for username in s.authors:
    try:
        found_users = session.query(User).filter(User.username == username).count()
        if found_users:
            pass
        else:
            session.add(User(username))
            session.commit()
    except Exception as err:
        # TODO: determine exact SQLAlchemy error thrown here
        print("could not save user %s: %s" % (username, err))

session = Session()

allusers = session.query(User.username).all()
scraped = session.query(distinct(Comment.author)).all()
unscraped = [user for user in allusers if user not in scraped]
# create a function for the try/except, then run the try block on the function
# add getting comments into the scraper

r=praw.Reddit(user_agent="u/tooproudtopose reddit-scraper")
path = os.path.expanduser('~/Data/LDA/Usertext/')

for result in unscraped:
    username = result[0]
    basename = '%s.user.csv' % username
    start = time.time()
    comments = []

    try:
        comments = r.get_redditor(username).get_comments(limit=comment_limit)
    except Exception as e:
        print("Could not find user %s" %username)

    lc = 0

    with open(path + basename, "w") as f:
        writer = csv.writer(f, lineterminator = "\n")

        for comment in comments:
            writer.writerow((comment.body, comment.author, comment.subreddit.display_name, datetime.datetime.fromtimestamp(comment.created_utc)))
            lc += 1
            db_comment = Comment(comment)
            try:
                session.add(db_comment)
                session.commit()
            except Exception as e:
                print("could not write comment to db: %s" % e)

    end = time.time()

    print( "        %s: %d comments downloaded in %d seconds." % (username, lc, int(end-start)))