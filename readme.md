# YouTube Shorts Generator Script Documentation

## Overview
This script automates the creation of YouTube Shorts videos on a given topic. It uses OpenAI's GPT-4 for script generation, ElevenLabs for voiceovers, and Pexels for video footage.

### Key Features:
- **Script Generation:** Leverages GPT-4 to create engaging scripts.
- **Voiceover Creation:** Uses ElevenLabs API for high-quality voiceovers.
- **Video Footage:** Sources relevant video clips from Pexels.
- **Automated Video Assembly:** Combines audio and video clips into a complete YouTube Short.

## Dependencies
- Python 3.x
- `requests`
- `json`
- `python-dotenv`
- `openai`
- `moviepy`

## Setup Instructions
1. **Install Dependencies:** Ensure Python 3.x is installed, then run `pip install requests python-dotenv openai moviepy`.
2. **Environment Variables:** Set up `.env` file with API keys:
   - `OPEN_API_KEY` for OpenAI.
   - `PEXELS_API_KEY` for Pexels.
   - `ELVEN_LABS_API_KEY` for ElevenLabs.

## Usage
Run the script with a topic as an argument: `python main.py "Your Topic"`.

### Script Workflow:
1. **Topic Input:** Accepts a topic for the YouTube Short.
2. **Scenario Generation:** Uses GPT-4 to generate a video script based on the topic.
3. **Video Download:** Fetches related video clips from Pexels.
4. **Audio Generation:** Creates a voiceover using ElevenLabs API.
5. **Video Assembly:** Merges audio and video clips, and outputs the final video.

## Functions Overview
- `generate_audio_from_text(text, scene_id, voice_id)`: Generates a voiceover for a given text.
- `download_videos_from_pexels(keywords)`: Downloads videos from Pexels based on provided keywords.
- `download_video(url, keyword)`: Helper function to download a specific video.
- `generate_scenario(topic)`: Generates the script and scene descriptions using GPT-4.

## Limitations & Notes
- **API Quotas:** Be aware of rate limits and quotas for OpenAI, Pexels, and ElevenLabs APIs.
- **Video Quality:** The quality of the final video depends on the available footage and TTS quality.
- **Error Handling:** The script includes basic error handling, which can be expanded for robustness.

## Future Enhancements
- **Customization Options:** Adding more options for voice and style customization in voiceovers.
- **Improved Error Handling:** Enhance error detection and handling for more stability.
- **User Interface:** Develop a GUI for easier interaction and topic input.

## Contributing
Contributions to improve or extend the script are welcome. Please adhere to standard coding practices and provide documentation for any changes.
