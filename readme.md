# YouTube Shorts Generator Script Documentation

## Overview
This script automates the creation of YouTube Shorts videos on a given topic. It uses OpenAI's GPT-4o for script generation, ElevenLabs **or 60db** for voiceovers, and Fal AI with Flux Schnell for image generation.

### Key Features:
- **Script Generation:** Leverages GPT-4o-2024-05-13 to create engaging scripts.
- **Voiceover Creation:** Pluggable TTS — choose **ElevenLabs** or **60db** via a single env var. Both write the same output, so the rest of the pipeline is identical regardless of provider.
- **Image Generation:** Uses Fal AI with Flux Schnell model for generating relevant images.
- **Automated Video Assembly:** Combines audio and generated images into a complete YouTube Short.

## Voiceover Providers (TTS)
The voiceover backend is selected at runtime by the `TTS_PROVIDER` environment variable:

| `TTS_PROVIDER` | Backend | API key | Notes |
|----------------|---------|---------|-------|
| `elevenlabs` (default) | ElevenLabs `eleven_multilingual_v2` | `ELVEN_LABS_API_KEY` | Returns raw MP3 bytes. Voice: Rachel (`21m00Tcm4TlvDq8ikWAM`). |
| `60db` | 60db `/tts-synthesize` | `DB60_API_KEY` | Returns JSON with base64 MP3. Voice is auto-fetched once from `/myvoices` and cached for the whole run. |

Both providers write an identical `scene_{id}.mp3` for each scene, so image generation, reformatting, and final assembly are unchanged across providers. Settings are kept consistent: both force `mp3` output, and 60db's `stability:50 / similarity:50` mirror ElevenLabs' `0.5 / 0.5`.

## Dependencies
- Python 3.x
- `requests`
- `json`
- `python-dotenv`
- `openai`
- `moviepy`

## Setup Instructions

### Option 1: Quick Setup (Recommended)
Run the installation script:
```bash
./install.sh
```

### Option 2: Manual Setup
1. **Install Dependencies:** Ensure Python 3.x is installed, then run:
   ```bash
   pip install -r requirements.txt
   ```
   
   *Note: We use locked versions to ensure compatibility. The `requirements.txt` includes specific versions that have been tested and confirmed working together.*

2. **Environment Variables:** Set up `.env` file with API keys:
   - `OPEN_API_KEY` for OpenAI.
   - `FAL_API_KEY` for Fal AI.
   - `ELVEN_LABS_API_KEY` for ElevenLabs.
   - `DB60_API_KEY` for 60db (only required if `TTS_PROVIDER=60db`).
   - `TTS_PROVIDER` to pick the voiceover backend: `elevenlabs` (default) or `60db`.

## Usage
Run the script with a topic as an argument: `python main.py "Your Topic"`.

Select the voiceover provider via `.env` before running:
```bash
# ElevenLabs (default)
TTS_PROVIDER="elevenlabs"
python main.py "Your Topic"

# 60db
TTS_PROVIDER="60db"
DB60_API_KEY="your-60db-key"
python main.py "Your Topic"
```

### Script Workflow:
1. **Topic Input:** Accepts a topic for the YouTube Short.
2. **Scenario Generation:** Uses GPT-4o-2024-05-13 to generate a video script based on the topic.
3. **Image Generation:** Creates relevant images using Fal AI with Flux Schnell model.
4. **Audio Generation:** Creates a voiceover using ElevenLabs API.
5. **Video Assembly:** Merges audio and generated images into video clips, and outputs the final video.

## Functions Overview
- `generate_audio_from_text(text, scene_id)`: Dispatcher — generates a voiceover by routing to the provider set in `TTS_PROVIDER`. Returns `True` on success.
- `generate_audio_elevenlabs(text, scene_id, voice_id)`: ElevenLabs TTS backend (raw MP3 bytes).
- `generate_audio_60db(text, scene_id)`: 60db TTS backend (base64 MP3 from JSON).
- `get_db60_voice_id()`: Fetches the account's first 60db voice from `/myvoices` once and caches it.
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
- **✅ Added 60db as a second TTS provider** alongside ElevenLabs, switchable via `TTS_PROVIDER`
- **✅ Refactored voiceover into a provider abstraction** with consistent MP3 output and settings across backends
- **✅ Audio failures now skip the scene** instead of crashing final assembly
- **✅ Updated to GPT-4o-2024-05-13** for improved script generation
- **✅ Replaced Pexels with Fal AI + Flux Schnell** for high-quality image generation
- **✅ Added automatic video creation** from generated images  
- **✅ Fixed compatibility issues** between MoviePy and newer Pillow versions
- **✅ Locked dependency versions** in `requirements.txt` to prevent compatibility issues

## Important Notes
- **Dependency Versions:** This project uses specific library versions (see `requirements.txt`) that have been tested for compatibility. Using different versions may cause issues, particularly with MoviePy and Pillow.
- **PIL Compatibility:** The code includes a compatibility fix for newer Pillow versions with older MoviePy.
- **System Dependencies:** Make sure you have the required system libraries for image processing (automatically installed in most environments).

## Contributing
Contributions to improve or extend the script are welcome. Please adhere to standard coding practices and provide documentation for any changes.
