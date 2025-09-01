import requests
import json
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
scenes = []

def generate_audio_from_text(text, scene_id, voice_id = "21m00Tcm4TlvDq8ikWAM"):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

    payload = {
        "model_id": "eleven_multilingual_v2",
        "voice":"Bella",
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
        # downondld from response.text
        with open(f"scene_{scene_id}.mp3", "wb") as f:
            f.write(response.content)
    else:
        print(f"Failed to generate audio for scene {scene_id}: {response.text}")


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
            
            # Generate audio
            generate_audio_from_text(scene['script'], scene_id)
            
            # Create video from generated images
            video_filename = create_video_from_images(generated_images, scene_id)
            
            if video_filename:
                scenes.append((video_filename, f"scene_{scene_id}.mp3"))
                print(f"Created video for scene {scene_id}: {video_filename}")
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






