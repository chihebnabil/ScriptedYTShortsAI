import requests
import json
from dotenv import load_dotenv
import os
from openai import OpenAI
from moviepy.editor import VideoFileClip, concatenate_videoclips, AudioFileClip
import os
from format_video import reformat_video , merge_audio_video
import sys
# Load environment variables
load_dotenv()
# Get API keys from environment variables
openai_api_key = os.getenv("OPEN_API_KEY")
pexels_api_key = os.getenv("PEXELS_API_KEY")
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


def download_videos_from_pexels(keywords):
    keywords = keywords.split(',')
    for keyword in keywords:
        video_filename = f'{keyword}.mp4'
        # Check if the video already exists locally
        if os.path.exists(video_filename):
            print(f"Video for '{keyword}' already exists.")
            return video_filename
        # Make a request to the Pexels API
        url = f'https://api.pexels.com/videos/search?query={keyword}&per_page=1'
        headers = {'Authorization': pexels_api_key}
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            videos = data.get('videos', [])

            if videos:
                video_url = videos[0]['video_files'][0]['link']
                return download_video(video_url, keyword)
            else:
                print(f"No videos found for keyword: {keyword}")
        else:
            print(f"Failed to get videos for keyword: {keyword}")
    return None

# Function to download the video
def download_video(url, keyword):
    video_data = requests.get(url)
    print(f"Downloading video for keyword: {keyword}")
    filename = f'{keyword}.mp4'
    with open(filename, 'wb') as file:
        file.write(video_data.content)
    return filename

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
                                "keywords": {"type": "string" , "description": "Relevant keywords for the video audiance which will be used to find a video on pexels , avoid words like 'inroduction' or 'conclusion'"},
                            },            
                },
            },
            },
        }
        }
    ]

    try:
        response = client.chat.completions.create(
            model="gpt-4",
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
            video_filename = download_videos_from_pexels(scene['keywords'])
            generate_audio_from_text(scene['script'], scene['id'])
            if video_filename:
                scenes.append((video_filename, f"scene_{scene['id']}.mp3"))
                print(f"Downloaded video for scene {scene['id']}: {video_filename}")
            else:
                print(f"Could not download video for scene {scene['id']}")
        
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






