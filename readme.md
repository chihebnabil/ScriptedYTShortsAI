# YouTube Shorts Generator Script Documentation

## Overview
This script automates the creation of YouTube Shorts videos on a given topic. It uses OpenAI's GPT-4o for script generation, ElevenLabs for voiceovers, and Fal AI with Flux Schnell for image generation.

### Key Features:
- **Script Generation:** Leverages GPT-4o-2024-05-13 to create engaging scripts.
- **Voiceover Creation:** Uses ElevenLabs API for high-quality voiceovers.
- **Image Generation:** Uses Fal AI with Flux Schnell model for generating relevant images.
- **Automated Video Assembly:** Combines audio and generated images into a complete YouTube Short.

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
   - `FAL_API_KEY` for Fal AI.
   - `ELVEN_LABS_API_KEY` for ElevenLabs.

## Usage
Run the script with a topic as an argument: `python main.py "Your Topic"`.

### Script Workflow:
1. **Topic Input:** Accepts a topic for the YouTube Short.
2. **Scenario Generation:** Uses GPT-4o-2024-05-13 to generate a video script based on the topic.
3. **Image Generation:** Creates relevant images using Fal AI with Flux Schnell model.
4. **Audio Generation:** Creates a voiceover using ElevenLabs API.
5. **Video Assembly:** Merges audio and generated images into video clips, and outputs the final video.

## Functions Overview
- `generate_audio_from_text(text, scene_id, voice_id)`: Generates a voiceover for a given text.
- `generate_images_from_fal(keywords, scene_id)`: Generates images using Fal AI with Flux Schnell model based on provided keywords.
- `create_video_from_images(images, scene_id, duration)`: Creates a video from generated images.
- `generate_scenario(topic)`: Generates the script and scene descriptions using GPT-4o-2024-05-13.

## Limitations & Notes
- **API Quotas:** Be aware of rate limits and quotas for OpenAI, Fal AI, and ElevenLabs APIs.
- **Image Quality:** The quality of the final video depends on the generated images and TTS quality.
- **Error Handling:** The script includes basic error handling, which can be expanded for robustness.

## Future Enhancements
- **Customization Options:** Adding more options for voice and style customization in voiceovers.
- **Improved Error Handling:** Enhance error detection and handling for more stability.
- **User Interface:** Develop a GUI for easier interaction and topic input.
- **Image Style Control:** Add options to control the style and theme of generated images.

## Recent Updates
- **✅ Updated to GPT-4o-2024-05-13** for improved script generation
- **✅ Replaced Pexels with Fal AI + Flux Schnell** for high-quality image generation
- **✅ Added automatic video creation** from generated images  
- **✅ Fixed compatibility issues** between MoviePy and newer Pillow versions

## Contributing
Contributions to improve or extend the script are welcome. Please adhere to standard coding practices and provide documentation for any changes.
