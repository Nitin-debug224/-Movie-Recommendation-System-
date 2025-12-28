import pandas as pd
import hashlib
import os

USERS_FILE = 'users.csv'

def init_users_file():
    if not os.path.exists(USERS_FILE):
        df = pd.DataFrame(columns=['username', 'password', 'age', 'gender'])
        df.to_csv(USERS_FILE, index=False)
    else:
        # Ensure columns exist if file exists but was created before
        df = pd.read_csv(USERS_FILE)
        if 'age' not in df.columns:
            df['age'] = None
        if 'gender' not in df.columns:
            df['gender'] = None
        df.to_csv(USERS_FILE, index=False)

def hash_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def signup(username, password):
    init_users_file()
    df = pd.read_csv(USERS_FILE)
    if username in df['username'].values:
        return False, "Username already exists"
    
    new_user = pd.DataFrame({
        'username': [username], 
        'password': [hash_password(password)],
        'age': [None],
        'gender': [None]
    })
    df = pd.concat([df, new_user], ignore_index=True)
    df.to_csv(USERS_FILE, index=False)
    return True, "Account created successfully"

def update_user_profile(username, age, gender):
    init_users_file()
    df = pd.read_csv(USERS_FILE)
    
    if username in df['username'].values:
        df.loc[df['username'] == username, 'age'] = age
        df.loc[df['username'] == username, 'gender'] = gender
        df.to_csv(USERS_FILE, index=False)
        return True
    return False

def login(username, password):
    init_users_file()
    df = pd.read_csv(USERS_FILE)
    hashed_pw = hash_password(password)
    
    user = df[(df['username'] == username) & (df['password'] == hashed_pw)]
    if not user.empty:
        return True, "Login successful"
    return False, "Invalid username or password"

def get_user_info(username):
    init_users_file()
    df = pd.read_csv(USERS_FILE)
    user = df[df['username'] == username]
    if not user.empty:
        return user.iloc[0].to_dict()
    return {}
