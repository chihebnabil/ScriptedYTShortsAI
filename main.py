import requests
import json
import base64
from dotenv import load_dotenv
import os
from openai import OpenAI
from moviepy.editor import VideoFileClip, concatenate_videoclips, AudioFileClip, ImageClip
import os
from format_video import reformat_video , merge_audio_video
import sys

# Fix for PIL.Image.ANTIALIAS compatibility issue
try:
    from PIL import Image
    if not hasattr(Image, 'ANTIALIAS'):
        Image.ANTIALIAS = Image.LANCZOS
except ImportError:
    pass
# Load environment variables
load_dotenv()
# Get API keys from environment variables
openai_api_key = os.getenv("OPEN_API_KEY")
fal_api_key = os.getenv("FAL_API_KEY")
elevenlabs_api_key = os.getenv("ELVEN_LABS_API_KEY")
db60_api_key = os.getenv("DB60_API_KEY")
# Which TTS backend to use for the whole run: "elevenlabs" (default) or "60db"
tts_provider = os.getenv("TTS_PROVIDER", "elevenlabs").lower()
# Cache the 60db voice so every scene in a run uses the same voice (consistency)
_db60_voice_id = None
scenes = []


def generate_audio_from_text(text, scene_id):
    """Generate a voiceover MP3 for `text`, dispatching to the configured TTS provider.

    Both backends write the identical `scene_{scene_id}.mp3` so the rest of the
    pipeline does not care which provider produced it. Returns True on success.
    """
    if tts_provider == "60db":
        return generate_audio_60db(text, scene_id)
    return generate_audio_elevenlabs(text, scene_id)


def generate_audio_elevenlabs(text, scene_id, voice_id="21m00Tcm4TlvDq8ikWAM"):
    """ElevenLabs TTS. Returns raw MP3 bytes written straight to disk."""
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

    payload = {
        "model_id": "eleven_multilingual_v2",
        "text": text,
        "voice_settings": {
            "similarity_boost": 0.5,
            "stability": 0.5,
            # "style": 123,            # Example value
            # "use_speaker_boost": True
        }
    }
    headers = {
        "xi-api-key": f"{elevenlabs_api_key}",
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        with open(f"scene_{scene_id}.mp3", "wb") as f:
            f.write(response.content)
        return True
    else:
        print(f"Failed to generate audio (elevenlabs) for scene {scene_id}: {response.text}")
        return False


def get_db60_voice_id():
    """Fetch the account's first available 60db voice once and cache it."""
    global _db60_voice_id
    if _db60_voice_id:
        return _db60_voice_id

    response = requests.get(
        "https://api.60db.ai/myvoices",
        headers={"Authorization": f"Bearer {db60_api_key}"},
    )
    response.raise_for_status()
    voices = response.json().get("data", [])
    if not voices:
        raise RuntimeError("No 60db voices available on this account")

    _db60_voice_id = voices[0]["voice_id"]
    print(f"Using 60db voice: {voices[0].get('name')} ({_db60_voice_id})")
    return _db60_voice_id


def generate_audio_60db(text, scene_id):
    """60db TTS. Returns JSON with base64 audio; settings mirror the ElevenLabs call."""
    url = "https://api.60db.ai/tts-synthesize"

    payload = {
        "text": text,
        "voice_id": get_db60_voice_id(),
        "output_format": "mp3",   # keep output interchangeable with ElevenLabs
        "stability": 50,          # 0.5 on ElevenLabs' 0-1 scale
        "similarity": 50,         # 0.5 on ElevenLabs' 0-1 scale
        "speed": 1.0,
    }
    headers = {
        "Authorization": f"Bearer {db60_api_key}",
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        result = response.json()
        if result.get("success") and result.get("audio_base64"):
            with open(f"scene_{scene_id}.mp3", "wb") as f:
                f.write(base64.b64decode(result["audio_base64"]))
            return True
        print(f"60db returned no audio for scene {scene_id}: {result.get('message')}")
        return False
    else:
        print(f"Failed to generate audio (60db) for scene {scene_id}: {response.text}")
        return False


def generate_images_from_fal(keywords, scene_id):
    """Generate images using Fal API with Flux Schnell model"""
    keywords_list = keywords.split(',')
    generated_images = []
    
    for i, keyword in enumerate(keywords_list):
        keyword = keyword.strip()
        if not keyword:
            continue
            
        # Create a more detailed prompt for better image generation
        prompt = f"High quality, cinematic, professional photograph of {keyword}, detailed, realistic, good lighting"
        
        url = "https://fal.run/fal-ai/flux/schnell"
        
        payload = {
            "prompt": prompt,
            "image_size": "portrait_16_9",
            "num_inference_steps": 4,
            "enable_safety_checker": True
        }
        
        headers = {
            "Authorization": f"Key {fal_api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                if 'images' in result and len(result['images']) > 0:
                    image_url = result['images'][0]['url']
                    
                    # Download the generated image
                    image_response = requests.get(image_url)
                    if image_response.status_code == 200:
                        filename = f'scene_{scene_id}_image_{i}.jpg'
                        with open(filename, 'wb') as f:
                            f.write(image_response.content)
                        generated_images.append(filename)
                        print(f"Generated image for '{keyword}': {filename}")
                    else:
                        print(f"Failed to download image for '{keyword}'")
                else:
                    print(f"No images generated for '{keyword}'")
            else:
                print(f"Failed to generate image for '{keyword}': {response.text}")
                
        except Exception as e:
            print(f"Error generating image for '{keyword}': {str(e)}")
    
    return generated_images


def create_video_from_images(images, scene_id, duration=5):
    """Create a video from generated images"""
    if not images:
        print(f"No images available for scene {scene_id}")
        return None
    
    try:
        video_clips = []
        clip_duration = duration / len(images) if len(images) > 0 else duration
        
        for image_path in images:
            if os.path.exists(image_path):
                clip = ImageClip(image_path, duration=clip_duration)
                clip = clip.resize((1080, 1920))  # Portrait orientation for YouTube Shorts
                video_clips.append(clip)
        
        if video_clips:
            final_clip = concatenate_videoclips(video_clips, method="compose")
            video_filename = f'scene_{scene_id}_video.mp4'
            final_clip.write_videofile(video_filename, codec="libx264", fps=24)
            final_clip.close()
            
            # Clean up image files
            for image_path in images:
                if os.path.exists(image_path):
                    os.remove(image_path)
            
            print(f"Created video from images: {video_filename}")
            return video_filename
        else:
            print(f"No valid images found for scene {scene_id}")
            return None
            
    except Exception as e:
        print(f"Error creating video from images for scene {scene_id}: {str(e)}")
        return None

# Function to generate scenarios using OpenAI API
def generate_scenario(topic):
    # OpenAI API Client setup...
    # ... existing code ...
    client = OpenAI(
    # This is the default and can be omitted
        api_key=openai_api_key
    )

    tools = [
        {
            "name": "get_scenes",
            "description": "Get the scenes for a video voiceover script without scene descriptions",
            "parameters": {
                "type": "object",
                "properties": {
                    "scenes": {
                        "type": "array",
                        "description": "The scenes for the video voiceover script",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "integer"},
                                "script": {"type": "string" , "description": "The script for the scene.MUST include only the text that will be spoken by the narrator"},
                                "keywords": {"type": "string" , "description": "Relevant keywords for image generation using AI, describe visual elements that would complement the narration"},
                            },            
                },
            },
            },
        }
        }
    ]

    try:
        response = client.chat.completions.create(
            model="gpt-4o-2024-05-13",
             messages=[
        {"role": "system", "content": "You are youtube  creator. You are creating a 1mn video script for a given topic"},
        {"role": "user", "content":  topic},
        ],
        functions = tools,
        function_call = {
            "name": "get_scenes",
        },
        )
        # Loading the response as a JSON object
        json_response = json.loads(response.choices[0].message.function_call.arguments)
        return response.choices[0].message.function_call.arguments
    except Exception as e:
        print(e)
        return None


# Check if the first argument as the topic exists
if len(sys.argv) > 1:
    topic = sys.argv[1]
    response = generate_scenario(topic)
    if response:
        json_response = json.loads(response)
        
        for scene in json_response['scenes']:
            # Get scene ID, handle different possible keys
            scene_id = scene.get('id') or scene.get('scene_id') or len(scenes) + 1
            
            # Generate images using Fal API
            generated_images = generate_images_from_fal(scene['keywords'], scene_id)

            # Generate audio (ElevenLabs or 60db, per TTS_PROVIDER)
            audio_ok = generate_audio_from_text(scene['script'], scene_id)

            # Create video from generated images
            video_filename = create_video_from_images(generated_images, scene_id)

            if video_filename and audio_ok:
                scenes.append((video_filename, f"scene_{scene_id}.mp3"))
                print(f"Created video for scene {scene_id}: {video_filename}")
            elif not audio_ok:
                print(f"Skipping scene {scene_id}: audio generation failed")
            else:
                print(f"Could not create video for scene {scene_id}")
        
        merged_clips = []
        for video_filename, audio_filename in scenes:
            resized_video = reformat_video(video_filename)
            merged_clip = merge_audio_video(audio_filename, resized_video)
            merged_clips.append(VideoFileClip(merged_clip))

        # Concatenate all the clips
        final_clip = concatenate_videoclips(merged_clips, method="compose")
        final_clip.write_videofile("final_youtube_short.mp4", codec="libx264", audio_codec="aac")

        # Clean up
        for clip in merged_clips:
            os.remove(clip.filename)
else:
    print("Please provide a topic as an argument")