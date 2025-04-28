import streamlit as st
import os
import yt_dlp
import subprocess

def get_short_links(channel_url):
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'playlist_end': 100,
    }

    if '/@' in channel_url:
        channel_username = channel_url.split('/@')[1].split('/')[0]
        channel_url = f'https://www.youtube.com/@{channel_username}/shorts'
    else:
        channel_url = channel_url.split('/about')[0]
        channel_url = channel_url.split('/community')[0]
        channel_url = channel_url.split('/playlist')[0]
        channel_url = channel_url.split('/playlists')[0]
        channel_url = channel_url.split('/streams')[0]
        channel_url = channel_url.split('/featured')[0]
        channel_url = channel_url.split('/videos')[0]
        channel_url += '/shorts'

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(channel_url, download=False)
        if 'entries' in result:
            video_ids = [entry['id'] for entry in result['entries']]
            return [f'https://www.youtube.com/shorts/{vid}' for vid in video_ids]
        else:
            st.warning("No videos found.")
            return []

def download_videos(links, output_path):
    total = len(links)
    for idx, link in enumerate(links, 1):
        try:
            subprocess.run(['yt-dlp', '--quiet', '--output',
                            os.path.join(output_path, '%(title)s.%(ext)s'),
                            link], check=True)
            st.info(f"Downloaded {idx}/{total}: {link}")
        except subprocess.CalledProcessError as e:
            st.error(f"Failed {idx}/{total}: {link} - {e}")
        st.progress(idx / total)

# ---- Streamlit UI ----

st.title("📥 Shorts Bulk Downloader")
st.markdown("Download multiple YouTube Shorts from a channel at once.")

channel_url = st.text_input("🔗 Enter YouTube channel URL:")
folder_name = st.text_input("📁 Folder name to save videos (inside ./downloads):", value="default_folder")

if st.button("Start Download"):
    if not channel_url.strip():
        st.warning("Please enter a valid channel URL.")
    else:
        download_dir = os.path.join("downloads", folder_name)
        os.makedirs(download_dir, exist_ok=True)

        st.write("🔍 Extracting short links...")
        short_links = get_short_links(channel_url)

        if short_links:
            st.success(f"Found {len(short_links)} videos. Starting download...")
            download_videos(short_links, download_dir)
        else:
            st.error("No shorts found or failed to extract links.")
