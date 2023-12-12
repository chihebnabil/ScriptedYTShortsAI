from moviepy.editor import VideoFileClip, concatenate_videoclips, AudioFileClip , ColorClip , CompositeVideoClip
import os
import math

def reformat_video(video_filename):
    try:
        if not os.path.exists(video_filename):
            print(f"File not found: {video_filename}")
            return None

        clip = VideoFileClip(video_filename)
        clip = clip.without_audio()  # Remove audio

        target_width, target_height = 1080, 1920  # Vertical video resolution
        original_width, original_height = clip.size
        aspect_ratio = target_width / target_height

        # Determine whether to crop horizontally or vertically
        if original_width / original_height > aspect_ratio:
            # Crop horizontally
            new_height = original_height
            new_width = int(new_height * aspect_ratio)
            x1 = (original_width - new_width) // 2
            y1 = 0
        else:
            # Crop vertically
            new_width = original_width
            new_height = int(new_width / aspect_ratio)
            x1 = 0
            y1 = (original_height - new_height) // 2

        x2 = x1 + new_width
        y2 = y1 + new_height

        # Crop and resize the video
        resized_clip = clip.crop(x1=x1, y1=y1, x2=x2, y2=y2).resize((target_width, target_height))
        resized_filename = f"vertical_{video_filename}"
        resized_clip.write_videofile(resized_filename, codec="libx264", audio_codec="aac")
        resized_clip.close()  # Make sure to close the clip
        print(f"Vertical resized video created: {resized_filename}")
        return resized_filename
    except Exception as e:
        print(f"Error processing file {video_filename}: {e}")
        return None

def merge_audio_video(audio_filename, video_filename):
    video_filename = os.path.basename(video_filename)
    video_clip = VideoFileClip(video_filename)
    audio_clip = AudioFileClip(audio_filename)
    # Loop the video clip if it's shorter than the audio clip
    if video_clip.duration < audio_clip.duration:
        loops_required = math.ceil(audio_clip.duration / video_clip.duration)
        video_clip = concatenate_videoclips([video_clip] * loops_required)
    # Set the audio of the video clip to match the audio duration
    video_clip = video_clip.set_audio(audio_clip)
    video_clip = video_clip.subclip(0, audio_clip.duration)

    merged_filename = f"merged_{video_filename}"
    video_clip.write_videofile(merged_filename, codec="libx264", audio_codec="aac")
    return merged_filename

