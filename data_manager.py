import pandas as pd
import os
from datetime import datetime

FEEDBACK_FILE = 'feedback.csv'

def init_feedback_file():
    if not os.path.exists(FEEDBACK_FILE):
        df = pd.DataFrame(columns=['timestamp', 'username', 'movie_id', 'movie_title', 'action', 'genre_ids'])
        df.to_csv(FEEDBACK_FILE, index=False)

def log_feedback(username, movie_id, movie_title, action, genre_ids):
    init_feedback_file()
    df = pd.read_csv(FEEDBACK_FILE)
    
    new_entry = {
        'timestamp': datetime.now(),
        'username': username,
        'movie_id': movie_id,
        'movie_title': movie_title,
        'action': action, # 'like' or 'dislike'
        'genre_ids': str(genre_ids)
    }
    
    new_df = pd.DataFrame([new_entry])
    df = pd.concat([df, new_df], ignore_index=True)
    df.to_csv(FEEDBACK_FILE, index=False)

def get_user_interacted_movies(username):
    init_feedback_file()
    df = pd.read_csv(FEEDBACK_FILE)
    if df.empty:
        return set()
    
    # Filter by username
    user_df = df[df['username'] == username]
    return set(user_df['movie_id'].unique())
