# main.py
from celery import Celery
from sqlalchemy import create_engine, Column, String, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from celery.utils.log import get_task_logger
import feedparser
from datetime import datetime
from nltk import classify
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.sentiment import SentimentIntensityAnalyzer

# Configure SQLAlchemy database connection
engine = create_engine('postgresql://root:root@localhost/news')
Base = declarative_base()
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

# Configure Celery
app = Celery('news_app', broker='pyamqp://guest:guest@localhost:5672//')
logger = get_task_logger(__name__)

# Define NLTK text classification functions
def get_features(text):
    words = word_tokenize(text)
    stop_words = set(stopwords.words('english'))
    features = {}
    for word in words:
        if word.lower() not in stop_words:
            features[word.lower()] = True
    return features

def classify_category(text):
    # Placeholder: Basic sentiment analysis as an example
    sid = SentimentIntensityAnalyzer()
    sentiment_score = sid.polarity_scores(text)['compound']

    if sentiment_score >= 0.05:
        return "Positive/Uplifting"
    elif sentiment_score <= -0.05:
        return "Terrorism/Protest/Political Unrest/Riot"
    else:
        return "Others"
    
# Define the database model
class NewsArticle(Base):
    __tablename__ = 'news_articles'

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    pub_date = Column(DateTime, nullable=False)
    source_url = Column(String, nullable=False)
    category = Column(String, nullable=True)

# Celery task for processing news articles
@app.task
def process_news_article(article_data):
    try:
        # Parse article data
        title = article_data['title']
        content = article_data['content']
        pub_date = article_data['pub_date']
        source_url = article_data['source_url']

        # Check for duplicate articles
        if not session.query(NewsArticle).filter_by(title=title, source_url=source_url).first():
            # Store article in the database
            article = NewsArticle(title=title, content=content, pub_date=pub_date, source_url=source_url)
            session.add(article)
            session.commit()

            # Classify and update category
            category = classify_category(content)
            article.category = category
            session.commit()

            logger.info(f"Article processed successfully: {title}")
        else:
            logger.info(f"Duplicate article found: {title}")

    except Exception as e:
        logger.error(f"Error processing article: {e}")

# Script to read RSS feeds and send articles to Celery queue
def read_rss_feeds():
    rss_feeds = [
        "http://rss.cnn.com/rss/cnn_topstories.rss",
        "http://qz.com/feed",
        "http://feeds.foxnews.com/foxnews/politics",
        "http://feeds.reuters.com/reuters/businessNews",
        "http://feeds.feedburner.com/NewshourWorld",
        "https://feeds.bbci.co.uk/news/world/asia/india/rss.xml"
    ]

    for feed_url in rss_feeds:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries:
            article_data = {
                'title': entry.title,
                'content': entry.get('summary', '') or entry.get('description', ''),  # Use 'description' if 'summary' is not present
                'pub_date': entry.get('published', ''),
                'source_url': entry.link
            }
            process_news_article.delay(article_data)

if __name__ == '__main__':
    read_rss_feeds()