# MP3-Download

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![Platform](https://img.shields.io/badge/platform-macOS-lightgrey)
![yt-dlp](https://img.shields.io/badge/yt--dlp-latest-red?logo=youtube&logoColor=white)

A command-line tool that batch-downloads YouTube videos as high-quality MP3 files with full ID3 metadata and embedded album art.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Features

| Feature                | Description                                                 |
| ---------------------- | ----------------------------------------------------------- |
| **320kbps MP3**        | Downloads audio at the highest MP3 bitrate                  |
| **ID3 Metadata**       | Embeds title, artist, album, and year tags                  |
| **Album Art**          | Fetches and embeds the YouTube thumbnail as cover art       |
| **Batch Download**     | Process multiple URLs from a text file                      |
| **Concurrent Workers** | Parallel downloads using `ThreadPoolExecutor`               |
| **Skip Existing**      | Automatically skips files that have already been downloaded |

## Prerequisites

- **Python 3.11+**
- **FFmpeg** — required by `yt-dlp` for audio extraction and conversion

Install FFmpeg on macOS via Homebrew:

```bash
brew install ffmpeg
```

## Installation

```bash
# Clone the repository
git clone <repo-url>
cd Mp3-Download

# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

### Dependencies

| Package                                           | Purpose                              |
| ------------------------------------------------- | ------------------------------------ |
| [`yt-dlp`](https://github.com/yt-dlp/yt-dlp)      | YouTube video/audio downloading      |
| [`mutagen`](https://github.com/quodlibet/mutagen) | ID3 tag reading and writing          |
| [`requests`](https://docs.python-requests.org/)   | HTTP requests for thumbnail fetching |

## Usage

1. Add YouTube URLs to `urls.txt` — one URL per line:

   ```text
   https://www.youtube.com/watch?v=VIDEO_ID_1
   https://www.youtube.com/watch?v=VIDEO_ID_2
   https://youtu.be/VIDEO_ID_3
   ```

2. Run the downloader:

   ```bash
   python mp3.py
   ```

3. Downloaded MP3 files appear in the `downloads/` directory.

### Example Output

```
--- Starting Batch Download (3 items) ---
  [+] Downloading: Song Title...
  [*] Success: Song Title
  [+] Downloading: Another Song...
  [*] Success: Another Song
  [-] Skipping: Already Downloaded (Exists)
--- All tasks completed ---
```

## Project Structure

```
Mp3-Download/
├── mp3.py              # Main entry point
├── urls.txt            # Input: YouTube URLs (one per line)
├── requirements.txt    # Python dependencies
├── downloads/          # Output: downloaded MP3 files
└── .venv/              # Python virtual environment
```

## Configuration

Edit the constants in `mp3.py` to customize behavior:

| Parameter     | Default       | Description                                       |
| ------------- | ------------- | ------------------------------------------------- |
| `output_dir`  | `"downloads"` | Directory where MP3 files are saved               |
| `quality`     | `"320"`       | Audio bitrate in kbps (e.g., `128`, `192`, `320`) |
| `max_workers` | `2`           | Number of concurrent download threads             |

## Contributing

Contributions are welcome. To contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Commit your changes (`git commit -m "Add my feature"`)
4. Push to the branch (`git push origin feature/my-feature`)
5. Open a Pull Request

Please ensure your code follows the existing style and includes appropriate error handling.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

**RAHUL KP KURUP** — https://github.com/hellorahulkp
