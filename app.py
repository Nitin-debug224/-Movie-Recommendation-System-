import streamlit as st
import auth
import tmdb_client
import data_manager
import pandas as pd

# --- Page Config ---
st.set_page_config(
    page_title="CineMatchPlus",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Custom CSS for Netflix-like Look ---
st.markdown("""
    <style>
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Roboto:wght@300;400;700&display=swap');

    /* Main Background with Overlay */
    .stApp {
        background-image: linear-gradient(rgba(0, 0, 0, 0.75), rgba(0, 0, 0, 0.75)), url('https://assets.nflxext.com/ffe/siteui/vlv3/c38a2d52-138e-48a3-ab68-36787ece46b3/eeb03fc9-99c6-438e-824d-32917ce55783/IN-en-20240101-popsignuptwoweeks-perspective_alpha_website_large.jpg');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        color: #ffffff;
        font-family: 'Roboto', sans-serif;
        overflow: hidden; /* Prevent scrolling */
    }
    
    /* Hide default header/footer if possible or blend them */
    header {visibility: hidden;}
    footer {visibility: hidden;}

    /* Headers */
    h1 {
        font-family: 'Bebas Neue', sans-serif;
        font-size: 3.5rem !important;
        text-align: center;
        margin-bottom: 0.5rem;
        color: white !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }
    
    h2, h3 {
        font-family: 'Roboto', sans-serif;
        font-weight: 400;
        text-align: center;
        color: white !important;
    }

    /* Custom Container for Forms */
    .login-container {
        background-color: transparent;
        padding: 60px;
        border-radius: 4px;
        max-width: 450px;
        margin: 0 auto;
        margin-top: 10px;
    }

    /* Hide Scrollbar and Fix Page */
    ::-webkit-scrollbar {
        display: none;
    }

    .stTextInput>div>div>input {
        background-color: #333;
        color: white;
        border: none;
        border-radius: 4px;
        padding: 10px;
    }
    .stTextInput>div>div>input:focus {
        background-color: #454545;
        border-bottom: 2px solid #e50914;
    }
    
    /* Primary Button (Red) */
    .stButton > button[kind="primary"] {
        background-color: #e50914;
        color: white;
        border: none;
        border-radius: 4px;
        font-weight: bold;
        font-size: 1rem;
        padding: 0.5rem 1rem;
        width: 100%;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #f40612;
    }
    
    /* Secondary Button */
    .stButton > button:not([kind="primary"]) {
        background-color: transparent;
        color: white;
        border: 1px solid #555;
    }
    
    /* Tabs styling to blend in */
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
        justify-content: center;
    }
    .stTabs [data-baseweb="tab"] {
        color: #aaa;
    }
    .stTabs [aria-selected="true"] {
        color: white;
        background-color: transparent;
        border-bottom: 2px solid #e50914;
    }

    /* Hero Text Styling */
    .hero-main {
        font-size: 3rem;
        font-weight: 900;
        text-align: center;
        margin-bottom: 1rem;
        line-height: 1.1;
    }
    .hero-sub {
        font-size: 1.5rem;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 400;
    }
    
    /* Navbar placeholder */
    .navbar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 20px 50px;
    }
    .netflix-logo {
        color: #e50914;
        font-family: 'Bebas Neue', sans-serif;
        font-size: 2.5rem;
        text-decoration: none;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Session State Initialization ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'survey_done' not in st.session_state:
    st.session_state.survey_done = False


# --- Helper Functions ---
def display_movie_row(title, movies):
    st.markdown(f"### {title}")
    if not movies:
        st.info("No movies found.")
        return

    cols = st.columns(5)
    for i, movie in enumerate(movies[:5]): # Show top 5
        with cols[i]:
            poster_path = movie.get('poster_path')
            img_url = tmdb_client.get_image_url(poster_path)
            st.image(img_url, use_container_width=True)
            st.caption(f"**{movie.get('title')}**")
            
            # Like/Dislike Buttons
            c1, c2 = st.columns(2)
            with c1:
                if st.button("❤️", key=f"like_{movie['id']}_{title}"):
                    data_manager.log_feedback(
                        st.session_state.username, 
                        movie['id'], 
                        movie['title'], 
                        'like', 
                        movie.get('genre_ids', [])
                    )
                    st.toast(f"Liked {movie['title']}!")
            with c2:
                if st.button("👎🏻", key=f"dislike_{movie['id']}_{title}"):
                    data_manager.log_feedback(
                        st.session_state.username, 
                        movie['id'], 
                        movie['title'], 
                        'dislike', 
                        movie.get('genre_ids', [])
                    )
                    st.toast(f"Disliked {movie['title']}!")

# --- Pages ---

def login_page():
    # Navbar
    st.markdown("""
        <div class="navbar">
            <div class="netflix-logo">CineMatch</div>
        </div>
    """, unsafe_allow_html=True)

    # Hero Text
    st.markdown("""
        <div style="padding: 0px; text-align: center;">
            <div class="hero-main">Your next favorite movie, found !!!</div>
        </div>
    """, unsafe_allow_html=True)

    # Centered Form
    col1, col2, col3 = st.columns([1, 1, 1]) # Adjust ratio to center
    with col2:
        with st.container():
            st.markdown('<div class="login-container">', unsafe_allow_html=True)
            
            tab1, tab2 = st.tabs(["Sign In", "Sign Up"])
            
            with tab1:
                username = st.text_input("Email or mobile number", key="login_user")
                password = st.text_input("Password", type="password", key="login_pass")
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Sign In", type="primary", use_container_width=True):
                    success, msg = auth.login(username, password)
                    if success:
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        
                        # Load user info
                        user_info = auth.get_user_info(username)
                        # Initialize preferences with stored data
                        st.session_state.user_preferences = {
                            'age': user_info.get('age') if pd.notna(user_info.get('age')) else None,
                            'gender': user_info.get('gender') if pd.notna(user_info.get('gender')) else None
                        }
                        
                        st.rerun()
                    else:
                        st.error(msg)
                        
            with tab2:
                new_user = st.text_input("Email address", key="signup_user")
                new_pass = st.text_input("Add a password", type="password", key="signup_pass")
                
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Get Started", type="primary", use_container_width=True):
                    success, msg = auth.signup(new_user, new_pass)
                    if success:
                        st.success(msg)
                    else:
                        st.error(msg)
            
            st.markdown('</div>', unsafe_allow_html=True)

def survey_page():
    # Navbar
    st.markdown("""
        <div class="navbar">
            <div class="netflix-logo">CineMatch</div>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.container():
            st.markdown('<div class="login-container" style="max-width: 600px;">', unsafe_allow_html=True)
            st.markdown("<h2>Finish setting up your account</h2>", unsafe_allow_html=True)
            st.write("We need a few details to personalize your experience.")
            
            # Check if we already have age/gender from login
            existing_prefs = st.session_state.get('user_preferences', {})
            existing_age = existing_prefs.get('age')
            existing_gender = existing_prefs.get('gender')
            
            if existing_age:
                age = existing_age
            else:
                age = st.number_input("Age", min_value=1, max_value=120, value=25)
                
            if existing_gender:
                gender = existing_gender
            else:
                gender = st.selectbox("Gender", ["Male", "Female", "Non-binary", "Other"])
            
            # Fetch genres for multiselect
            genres_map = tmdb_client.get_genres()
            if genres_map:
                selected_genres = st.multiselect("Favorite Genres", options=list(genres_map.values()))
            else:
                st.warning("Could not fetch genres. Check API Key.")
                selected_genres = []
            
            movie_length = st.selectbox("Preferred Movie Length", ["Short (< 90 mins)", "Medium (90-120 mins)", "Long (> 120 mins)"])
            moods = st.multiselect("Mood-Based Preferences", ["Happy", "Sad", "Adventurous", "Relaxed", "Thrilled", "Romantic", "Mystery"])

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Start Watching", type="primary", use_container_width=True):
                # Save age and gender to persistent storage
                auth.update_user_profile(st.session_state.username, age, gender)
                
                st.session_state.survey_done = True
                st.session_state.user_preferences = {
                    'age': age,
                    'gender': gender,
                    'genres': selected_genres,
                    'movie_length': movie_length,
                    'moods': moods
                }
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

def dashboard_page():
    # Get user's history to filter recommendations
    interacted_ids = data_manager.get_user_interacted_movies(st.session_state.username)

    # --- Parse Preferences Early ---
    runtime_min, runtime_max = None, None
    selected_genre_ids = []
    
    if 'user_preferences' in st.session_state:
        prefs = st.session_state.user_preferences
        movie_length_str = prefs.get('movie_length', "Medium (90-120 mins)")
        
        # Parse Runtime
        if "Short" in movie_length_str:
            runtime_max = 90
        elif "Medium" in movie_length_str:
            runtime_min = 90
            runtime_max = 120
        elif "Long" in movie_length_str:
            runtime_min = 120
            
        # Parse Genres
        selected_genre_names = prefs.get('genres', [])
        genres_map = tmdb_client.get_genres()
        name_to_id = {name: id for id, name in genres_map.items()}
        selected_genre_ids = [name_to_id[name] for name in selected_genre_names if name in name_to_id]

    # --- Hero Section ---
    hero_movie = None
    
    # Try to get a genre-based hero movie first
    if selected_genre_ids:
        # Focus on the first selected genre to ensure strong relevance
        primary_genre_id = selected_genre_ids[0]
        
        # Get highly rated movies in this SPECIFIC genre WITH RUNTIME FILTER
        genre_top_rated = tmdb_client.get_movies_by_genre(
            [primary_genre_id], 
            sort_by='vote_average.desc', 
            min_vote_count=1000,
            runtime_min=runtime_min,
            runtime_max=runtime_max
        )
        # Filter out watched
        genre_top_rated = [m for m in genre_top_rated if m['id'] not in interacted_ids]
        
        if genre_top_rated:
            hero_movie = genre_top_rated[0]

    # Fallback to global trending if no genre-based movie found (or if it didn't match runtime)
    if not hero_movie:
        # Note: get_trending_movies doesn't support runtime filter easily without fetching details for all.
        # We can try to fetch popular movies with runtime filter instead if trending fails.
        trending_now = tmdb_client.get_trending_movies()
        # Filter out watched
        trending_now = [m for m in trending_now if m['id'] not in interacted_ids]
        
        if trending_now:
            hero_movie = trending_now[0]

    if hero_movie:
        backdrop_path = hero_movie.get('backdrop_path')
        if backdrop_path:
            backdrop_url = f"https://image.tmdb.org/t/p/original{backdrop_path}"
            st.markdown(f"""
            <div style="
                background-image: linear-gradient(to top, #141414, rgba(20,20,20,0.5)), url('{backdrop_url}');
                background-size: cover;
                background-position: center;
                height: 60vh;
                display: flex;
                flex-direction: column;
                justify-content: flex-end;
                padding: 4rem;
                border-radius: 8px;
                margin-bottom: 2rem;
            ">
                <div class="hero-title">{hero_movie.get('title')}</div>
                <div class="hero-desc">{hero_movie.get('overview', '')[:200]}...</div>
                <div>
                    <button style="
                        background-color: white; color: black; border: none; padding: 10px 25px; 
                        font-size: 1.2rem; font-weight: bold; border-radius: 4px; cursor: pointer; margin-right: 10px;
                    ">▶ Play</button>
                    <button style="
                        background-color: rgba(109, 109, 110, 0.7); color: white; border: none; padding: 10px 25px; 
                        font-size: 1.2rem; font-weight: bold; border-radius: 4px; cursor: pointer;
                    ">ℹ More Info</button>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.title(f"Welcome, {st.session_state.username}")
    
    # Search
    search_query = st.text_input("Search for a movie...", placeholder="Inception, The Matrix...")
    if search_query:
        results = tmdb_client.search_movies(search_query)
        st.subheader(f"Results for '{search_query}'")
        
        if not results:
            st.info("No movies found.")
        else:
            # Display in grid
            cols = st.columns(5)
            for i, movie in enumerate(results):
                col = cols[i % 5]
                with col:
                    poster_path = movie.get('poster_path')
                    img_url = tmdb_client.get_image_url(poster_path)
                    st.image(img_url, use_container_width=True)
                    st.caption(f"**{movie.get('title')}** ({movie.get('release_date', '')[:4]})")
                    
                    # Like/Dislike Buttons
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("❤️", key=f"like_{movie['id']}_search"):
                            data_manager.log_feedback(
                                st.session_state.username, 
                                movie['id'], 
                                movie['title'], 
                                'like', 
                                movie.get('genre_ids', [])
                            )
                            st.toast(f"Liked {movie['title']}!")
                    with c2:
                        if st.button("👎🏻", key=f"dislike_{movie['id']}_search"):
                            data_manager.log_feedback(
                                st.session_state.username, 
                                movie['id'], 
                                movie['title'], 
                                'dislike', 
                                movie.get('genre_ids', [])
                            )
                            st.toast(f"Disliked {movie['title']}!")
    
    # Personalised Recommendations
    if 'user_preferences' in st.session_state:
        prefs = st.session_state.user_preferences
        selected_moods = prefs.get('moods', [])
            
        # 2. Parse Moods to Genres
        # Map moods to TMDB Genre IDs
        mood_genre_map = {
            "Happy": [35, 10751],       # Comedy, Family
            "Sad": [18],                # Drama
            "Adventurous": [12, 28],    # Adventure, Action
            "Relaxed": [10402, 99],     # Music, Documentary
            "Thrilled": [53, 27],       # Thriller, Horror
            "Romantic": [10749],        # Romance
            "Mystery": [9648]           # Mystery
        }
        
        mood_genre_ids = []
        for mood in selected_moods:
            mood_genre_ids.extend(mood_genre_map.get(mood, []))
            
        # Combine explicit genres and mood genres
        # We use a set to avoid duplicates, then convert back to list
        # selected_genre_ids is already available from top of function
        combined_genre_ids = list(set(selected_genre_ids + mood_genre_ids))
        
        if combined_genre_ids:
            # 1. Top Rated (Quality)
            top_rated = tmdb_client.get_movies_by_genre(
                combined_genre_ids, 
                sort_by='vote_average.desc', 
                min_vote_count=300,
                runtime_min=runtime_min,
                runtime_max=runtime_max
            )
            top_rated = [m for m in top_rated if m['id'] not in interacted_ids]
            display_movie_row("Top Rated for You", top_rated)

            # 2. Trending (Popularity)
            trending = tmdb_client.get_movies_by_genre(
                combined_genre_ids, 
                sort_by='popularity.desc',
                runtime_min=runtime_min,
                runtime_max=runtime_max
            )
            trending = [m for m in trending if m['id'] not in interacted_ids]
            display_movie_row("Trending in Your Genres & Moods", trending)

            # 3. Box Office (Revenue)
            box_office = tmdb_client.get_movies_by_genre(
                combined_genre_ids, 
                sort_by='revenue.desc',
                runtime_min=runtime_min,
                runtime_max=runtime_max
            )
            box_office = [m for m in box_office if m['id'] not in interacted_ids]
            display_movie_row("Box Office Hits in Your Genres & Moods", box_office)
    else:
        # Fallback if no genres selected
        trending = tmdb_client.get_trending_movies()
        trending = [m for m in trending if m['id'] not in interacted_ids]
        display_movie_row("Trending Now", trending)
        
        popular = tmdb_client.get_popular_movies()
        popular = [m for m in popular if m['id'] not in interacted_ids]
        display_movie_row("Popular on Netflix", popular)
    
    # Actor Based
    st.markdown("### Recommend by Actor")
    actor_name = st.text_input("Enter an actor's name", placeholder="Leonardo DiCaprio")
    if actor_name:
        # Use the same preferences calculated above if available
        # We need to re-calculate or access the variables if they are in scope.
        # Since 'combined_genre_ids', 'runtime_min', 'runtime_max' are inside the if block, we should initialize them outside or re-fetch.
        
        # Safe fetch of preferences for actor search
        actor_genre_ids = None
        actor_runtime_min = None
        actor_runtime_max = None
        
        if 'user_preferences' in st.session_state:
            prefs = st.session_state.user_preferences
            
            # Runtime
            length_pref = prefs.get('movie_length', "Medium")
            if "Short" in length_pref:
                actor_runtime_max = 90
            elif "Medium" in length_pref:
                actor_runtime_min = 90
                actor_runtime_max = 120
            elif "Long" in length_pref:
                actor_runtime_min = 120
                
            # Genres (Explicit + Mood)
            # Re-using logic briefly to ensure scope availability
            sel_genres = prefs.get('genres', [])
            sel_moods = prefs.get('moods', [])
            
            # Map moods
            mood_map = {
                "Happy": [35, 10751], "Sad": [18], "Adventurous": [12, 28],
                "Relaxed": [10402, 99], "Thrilled": [53, 27], "Romantic": [10749], "Mystery": [9648]
            }
            m_ids = []
            for m in sel_moods:
                m_ids.extend(mood_map.get(m, []))
                
            # Map names
            g_map = tmdb_client.get_genres()
            n_to_id = {n: i for i, n in g_map.items()}
            g_ids = [n_to_id[n] for n in sel_genres if n in n_to_id]
            
            actor_genre_ids = list(set(g_ids + m_ids))

        actor_movies = tmdb_client.get_movies_by_actor(
            actor_name, 
            genre_ids=actor_genre_ids,
            runtime_min=actor_runtime_min,
            runtime_max=actor_runtime_max
        )
        
        actor_movies = [m for m in actor_movies if m['id'] not in interacted_ids]
        
        if not actor_movies:
            st.info(f"No movies found for {actor_name} matching your preferences.")
        else:
            display_movie_row(f"Movies starring {actor_name} (Personalized)", actor_movies)

    # Logout
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.survey_done = False
        st.rerun()

# --- Main App Logic ---
try:
    if not st.session_state.logged_in:
        login_page()
    elif not st.session_state.survey_done:
        survey_page()
    else:
        dashboard_page()
except Exception as e:
    st.error(f"An error occurred: {e}")
    st.exception(e)
