import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
import os

# Check if we're running on Streamlit Cloud
is_streamlit_cloud = os.environ.get('STREAMLIT_RUNTIME') == 'cloud'

st.set_page_config(page_title='Your Spotify Analysis', page_icon=':musical_note:')

# Get credentials from environment or Streamlit secrets
if is_streamlit_cloud:
    CLIENT_ID = st.secrets["CLIENT_ID"]
    CLIENT_SECRET = st.secrets["CLIENT_SECRET"]
else:
    # For local development, try to load from .env file
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    CLIENT_ID = os.environ.get('CLIENT_ID')
    CLIENT_SECRET = os.environ.get('CLIENT_SECRET')

REDIRECT_URI = 'https://yourspotifyanalysis.streamlit.app'

SCOPE = "user-library-read user-top-read user-read-private user-read-email"

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

st.title('Your Spotify Analysis')
st.write('Insights about your music listening habits.')

def create_spotify_oauth():
    return SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=SCOPE,
        cache_path='.spotify_cache',
        show_dialog=True
    )

if not st.session_state.authenticated:
    if st.button('Connect to Spotify'):
        try:
            auth_manager = create_spotify_oauth()
            token_info = auth_manager.get_access_token(as_dict=True)
            sp = spotipy.Spotify(auth=token_info['access_token'])
            
            user = sp.current_user()
            st.session_state.token_info = token_info
            st.session_state.authenticated = True
            st.experimental_rerun()
        except Exception as e:
            st.error(f"Authentication failed: {str(e)}")
else:
    try:
        auth_manager = create_spotify_oauth()
        token_info = auth_manager.get_access_token(as_dict=True)
        sp = spotipy.Spotify(auth=token_info['access_token'])
        
        # Verify connection
        user = sp.current_user()
        st.success(f"Connected as: {user['display_name']}")
        
        with st.spinner('Fetching your top tracks...'):
            # Get top tracks
            results = sp.current_user_top_tracks(limit=50)
            
            if not results['items']:
                st.error("No tracks found")
                st.stop()
            
            # Create a list of track information
            tracks_info = []
            for track in results['items']:
                track_info = {
                    'name': track['name'],
                    'artist': track['artists'][0]['name'],
                    'popularity': track['popularity'] / 100,
                    'duration_min': round(track['duration_ms'] / 60000, 2),
                    'explicit': 1 if track['explicit'] else 0
                }
                tracks_info.append(track_info)
            
            if tracks_info:
                df = pd.DataFrame(tracks_info)
                
                # Display track list
                st.subheader('Your Top Tracks')
                for idx, track in enumerate(tracks_info, 1):
                    st.write(f"{idx}. {track['name']} by {track['artist']}")
                
                # Create visualization of track popularity
                st.subheader('Track Popularity')
                popularity_df = pd.DataFrame({
                    'Track': [t['name'] for t in tracks_info],
                    'Popularity': [t['popularity'] for t in tracks_info]
                }).set_index('Track')
                
                st.bar_chart(popularity_df)
                
                # Show raw data
                st.subheader('Track Details')
                st.dataframe(df)
                
            else:
                st.error("No track data could be retrieved")

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.session_state.authenticated = False