from flask import Flask, render_template, request
import googleapiclient.discovery
from textblob import TextBlob

# Initialize Flask application
app = Flask(__name__)

# YouTube API Configuration
api_service_name = "youtube"
api_version = "v3"
DEVELOPER_KEY = "YOUR_API_KEY"


# Function to classify comment sentiment
def classify_sentiment(comment):
    blob = TextBlob(comment)

    polarity = blob.sentiment.polarity

    if polarity < -0.5:
        sentiment = "Toxic"
    elif polarity > 0.5:
        sentiment = "Non-Toxic"
    else:
        sentiment = "Neutral"

    return sentiment, polarity


# Function to fetch YouTube comments
def fetch_comments(video_id):
    youtube = googleapiclient.discovery.build(
        api_service_name,
        api_version,
        developerKey=DEVELOPER_KEY
    )

    request = youtube.commentThreads().list(
        part="snippet",
        videoId=video_id,
        maxResults=10
    )

    response = request.execute()

    comments = []

    for item in response['items']:
        comment = item['snippet']['topLevelComment']['snippet']

        comments.append({
            'author': comment['authorDisplayName'],
            'published_at': comment['publishedAt'],
            'updated_at': comment['updatedAt'],
            'like_count': comment['likeCount'],
            'text': comment['textDisplay']
        })

    return comments


# Home Route
@app.route('/')
def index():
    return render_template('index.html')


# Route to process comments
@app.route('/process', methods=['POST'])
def process_comments():

    video_id = request.form['video_id']

    if not video_id:
        return render_template(
            'index.html',
            error="Please enter a valid YouTube video ID."
        )

    comments_data = fetch_comments(video_id)

    for comment in comments_data:
        data = comment['text']

        sentiment, polarity = classify_sentiment(data)

        comment['sentiment'] = sentiment
        comment['polarity'] = polarity

    return render_template(
        'index.html',
        comments=comments_data,
        video_id=video_id
    )


# Run Flask Application
if __name__ == '__main__':
    app.run(debug=True)
