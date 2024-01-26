The primary functionality of the project, which involves collecting news articles from various RSS feeds, categorizing them, and storing them in a database
# NewsFeed Categorizer

## Overview

This application is designed to collect news articles from various RSS feeds, store them in a database, and categorize them into predefined categories. The primary goal is to build a robust system for handling news data, from extraction to categorization.

## Requirements

- **Programming Language:**
  - Python (3.x)
  - NodeJS (JavaScript/TypeScript)

- **Libraries:**
  - Feedparser: For parsing RSS feeds
  - SQLAlchemy: For database interaction (e.g., PostgreSQL)
  - Celery: For managing the task queue
  - Natural Language Processing (NLTK or spaCy) for text classification

- **Database:**
  - Any relational database (e.g., PostgreSQL, MySQL)

## Implementation Details

### 1. Feed Parser and Data Extraction

- Create a script (`main.py`) that reads the provided list of RSS feeds.
- Parse each feed and extract relevant information from each news article, including title, content, publication date, and source URL.
- Ensure handling of duplicate articles from the same feed.

### 2. Database Storage

- Design a database schema to store the extracted news article data.
- Implement logic (`database.py`) to store new articles in the database without duplicates.

### 3. Task Queue and News Processing

- Set up a Celery queue to manage asynchronous processing of new articles.
- Configure the parser script (`main.py`) to send extracted articles to the queue upon arrival.
- Create a Celery worker (`celery_worker.py`) that consumes articles from the queue and performs further processing:
  - Category classification: Utilize NLTK or spaCy to classify each article into the provided categories.
  - Update the database with the assigned category for each article.

### 4. Logging and Error Handling

- Implement proper logging throughout the application to track events and potential errors.
- Handle parsing errors and network connectivity issues gracefully.

## How to Run

1. Install dependencies: `pip install -r requirements.txt`
2. Set up the database: `python database.py`
3. Start the Celery worker: `celery -A main.app worker --loglevel=info`
4. Run the main script to fetch and process news articles: `python main.py`



---

