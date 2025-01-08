import streamlit as st

# Test section
st.title("Test App")
st.write("If you can see this, the app is working!")

# Debug information
import os
st.write("Debug Information:")
st.write(f"Python Version: {os.sys.version}")
st.write(f"Running on Streamlit Cloud: {os.environ.get('STREAMLIT_RUNTIME') == 'cloud'}")

# Add a separator
st.markdown("---")

import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Basic page config
st.set_page_config(page_title='Spotify Analysis', page_icon='🎵')

# Simple title
st.title('Spotify Analysis')
st.write('Connect your Spotify account to see your music insights.')

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# Get credentials and set up OAuth
try:
    if os.environ.get('STREAMLIT_RUNTIME') == 'cloud':
        st.write("Running on Streamlit Cloud")
        CLIENT_ID = st.secrets["CLIENT_ID"]
        CLIENT_SECRET = st.secrets["CLIENT_SECRET"]
        REDIRECT_URI = 'https://yourspotifyanalysis.streamlit.app'
    else:
        st.write("Running locally")
        CLIENT_ID = os.environ.get('CLIENT_ID')
        CLIENT_SECRET = os.environ.get('CLIENT_SECRET')
        REDIRECT_URI = 'http://localhost:8502'
    
    st.write(f"Redirect URI: {REDIRECT_URI}")
    
    auth_manager = SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope="user-top-read",
        show_dialog=True,
        cache_path=None
    )

except Exception as e:
    st.error(f"Setup failed: {e}")
    st.stop()

# Authentication flow
if not st.session_state.authenticated:
    if st.button('Connect to Spotify'):
        try:
            # Get the auth URL
            auth_url = auth_manager.get_authorize_url()
            st.write(f"Auth URL: {auth_url}")
            
            # Redirect to Spotify
            st.markdown(f'<a href="{auth_url}" target="_self">Click here to authenticate with Spotify</a>', unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"Authentication failed: {e}")
else:
    try:
        # Get Spotify client
        sp = spotipy.Spotify(auth_manager=auth_manager)
        
        # Test the connection
        user = sp.current_user()
        st.success(f"Connected as: {user['display_name']}")
        
        # Show some basic user info
        st.write("Your Spotify Account Info:")
        st.write(f"- Email: {user['email']}")
        st.write(f"- Country: {user['country']}")
        st.write(f"- Account type: {user['product']}")
        
    except Exception as e:
        st.error(f"Error getting user data: {e}")
        st.session_state.authenticated = False