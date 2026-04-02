# import os
# import re
# import time
# import requests
# import yt_dlp
# from mutagen.mp3 import MP3
# from mutagen.id3 import ID3, APIC, TIT2, TPE1, TALB, TYER, error
# from concurrent.futures import ThreadPoolExecutor

# class YouTubeAudioDownloader:
#     def __init__(self, output_dir="downloads", quality="320"):
#         # Resolve absolute path to avoid issues on macOS
#         self.output_dir = os.path.abspath(output_dir)
#         self.quality = quality
        
#         if not os.path.exists(self.output_dir):
#             os.makedirs(self.output_dir)

#     def sanitize_filename(self, name):
#         return re.sub(r'[\\/*?:"<>|]', "", name)

#     def embed_metadata(self, file_path, metadata):
#         """Embeds ID3 tags and album art into the MP3 file."""
#         # Give the OS a split second to finalize the file write from FFmpeg
#         time.sleep(1) 
        
#         if not os.path.exists(file_path):
#             print(f"  [!] Target file not found for tagging: {file_path}")
#             return False

#         try:
#             audio = MP3(file_path, ID3=ID3)
            
#             try:
#                 audio.add_tags()
#             except error:
#                 pass

#             # Text Tags
#             audio.tags.add(TIT2(encoding=3, text=metadata.get('title', 'Unknown')))
#             audio.tags.add(TPE1(encoding=3, text=metadata.get('artist', 'Unknown')))
#             audio.tags.add(TALB(encoding=3, text=metadata.get('album', 'YouTube')))
            
#             if metadata.get('year'):
#                 audio.tags.add(TYER(encoding=3, text=str(metadata.get('year'))))

#             # Album Art (Thumbnail) logic
#             thumbnail_url = metadata.get('thumbnail')
#             if thumbnail_url:
#                 print(f"  [+] Fetching album art from: {thumbnail_url}")
#                 response = requests.get(thumbnail_url, timeout=10)
#                 if response.status_code == 200:
#                     audio.tags.add(APIC(
#                         encoding=3,
#                         mime='image/jpeg', # Most YT thumbs are JPEG
#                         type=3, 
#                         desc=u'Cover',
#                         data=response.content
#                     ))
            
#             audio.save(v2_version=3) # Force ID3v2.3 for better compatibility
#             return True
#         except Exception as e:
#             print(f"  [!] Metadata error: {e}")
#             return False

#     def download_video(self, url):
#         # yt-dlp options
#         ydl_opts = {
#             'format': 'bestaudio/best',
#             'outtmpl': os.path.join(self.output_dir, '%(title)s.%(ext)s'),
#             'quiet': True,
#             'no_warnings': True,
#             'postprocessors': [{
#                 'key': 'FFmpegExtractAudio',
#                 'preferredcodec': 'mp3',
#                 'preferredquality': self.quality,
#             }],
#         }

#         try:
#             with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#                 # 1. Extract metadata
#                 info = ydl.extract_info(url, download=False)
                
#                 # IMPORTANT: Get the path yt-dlp WILL create
#                 # We use the internal 'prepare_filename' to be 100% sure
#                 temp_filename = ydl.prepare_filename(info)
#                 final_path = os.path.splitext(temp_filename)[0] + ".mp3"

#                 if os.path.exists(final_path):
#                     print(f"  [-] Skipping: {info['title']} (Exists)")
#                     return

#                 print(f"  [+] Downloading: {info['title']}...")
#                 ydl.download([url])

#                 # 2. Prepare metadata
#                 meta_data = {
#                     'title': info.get('title'),
#                     'artist': info.get('uploader'),
#                     'thumbnail': info.get('thumbnail'),
#                     'year': info.get('upload_date')[:4] if info.get('upload_date') else None
#                 }

#                 # 3. Embed
#                 self.embed_metadata(final_path, meta_data)
#                 print(f"  [*] Success: {info['title']}")

#         except Exception as e:
#             print(f"  [x] Failed {url}: {e}")

#     def batch_download(self, urls, max_workers=2):
#         print(f"--- Starting Batch Download ---")
#         with ThreadPoolExecutor(max_workers=max_workers) as executor:
#             executor.map(self.download_video, urls)
#         print("--- All tasks completed ---")

# def main():
#     # urls = [
#     #     "https://youtu.be/b68HETiNO98?si=uktLBYhtxGO_i-Dm",
#     #     "https://youtu.be/vVDp1ulBKIk?si=oauvcUG8zLT1ey3_",
#     #     "https://youtu.be/DMD2uthghWE?si=T52sHUKuDxPft0vp",
#     # ]

#     if os.path.exists("urls.txt"):
#         with open("urls.txt", "r") as f:
#             DOWNLOAD_LIST = [line.strip() for line in f if line.strip()]
    
#     downloader = YouTubeAudioDownloader(quality="320")
#     downloader.batch_download(urls)

# if __name__ == "__main__":
#     main()
import os
import re
import time
import requests
import yt_dlp
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, TIT2, TPE1, TALB, TYER, error
from concurrent.futures import ThreadPoolExecutor

class YouTubeAudioDownloader:
    def __init__(self, output_dir="downloads", quality="320"):
        # Resolve absolute path to avoid issues on macOS
        self.output_dir = os.path.abspath(output_dir)
        self.quality = quality
        
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def sanitize_filename(self, name):
        return re.sub(r'[\\/*?:"<>|]', "", name)

    def embed_metadata(self, file_path, metadata):
        """Embeds ID3 tags and album art into the MP3 file."""
        # Give the OS a split second to finalize the file write from FFmpeg
        time.sleep(1.5) 
        
        if not os.path.exists(file_path):
            print(f"  [!] Target file not found for tagging: {file_path}")
            return False

        try:
            audio = MP3(file_path, ID3=ID3)
            
            try:
                audio.add_tags()
            except error:
                pass

            # Text Tags
            audio.tags.add(TIT2(encoding=3, text=metadata.get('title', 'Unknown')))
            audio.tags.add(TPE1(encoding=3, text=metadata.get('artist', 'Unknown')))
            audio.tags.add(TALB(encoding=3, text=metadata.get('album', 'YouTube')))
            
            if metadata.get('year'):
                audio.tags.add(TYER(encoding=3, text=str(metadata.get('year'))))

            # Album Art (Thumbnail) logic
            thumbnail_url = metadata.get('thumbnail')
            if thumbnail_url:
                response = requests.get(thumbnail_url, timeout=10)
                if response.status_code == 200:
                    audio.tags.add(APIC(
                        encoding=3,
                        mime='image/jpeg',
                        type=3, 
                        desc=u'Cover',
                        data=response.content
                    ))
            
            audio.save(v2_version=3)
            return True
        except Exception as e:
            print(f"  [!] Metadata error: {e}")
            return False

    def download_video(self, url):
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(self.output_dir, '%(title)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': self.quality,
            }],
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                temp_filename = ydl.prepare_filename(info)
                final_path = os.path.splitext(temp_filename)[0] + ".mp3"

                if os.path.exists(final_path):
                    print(f"  [-] Skipping: {info['title']} (Exists)")
                    return

                print(f"  [+] Downloading: {info['title']}...")
                ydl.download([url])

                meta_data = {
                    'title': info.get('title'),
                    'artist': info.get('uploader'),
                    'thumbnail': info.get('thumbnail'),
                    'year': info.get('upload_date')[:4] if info.get('upload_date') else None
                }

                self.embed_metadata(final_path, meta_data)
                print(f"  [*] Success: {info['title']}")

        except Exception as e:
            print(f"  [x] Failed {url}: {e}")

    def batch_download(self, urls, max_workers=2):
        if not urls:
            print("[!] No URLs provided. Please add links to urls.txt")
            return
            
        print(f"--- Starting Batch Download ({len(urls)} items) ---")
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            executor.map(self.download_video, urls)
        print("--- All tasks completed ---")

def main():
    # 1. Initialize an empty list
    urls_to_download = []

    # 2. Check if the file exists and load it
    if os.path.exists("urls.txt"):
        with open("urls.txt", "r") as f:
            # strip() removes extra whitespace and newlines
            urls_to_download = [line.strip() for line in f if line.strip()]
    else:
        print("[!] urls.txt not found. Please create it in this folder.")
        # Fallback list for testing if file is missing
        # urls_to_download = ["https://www.youtube.com/watch?v=dQw4w9WgXcQ"]

    # 3. Pass the CORRECT variable name to the downloader
    downloader = YouTubeAudioDownloader(quality="320")
    downloader.batch_download(urls_to_download)

if __name__ == "__main__":
    main()