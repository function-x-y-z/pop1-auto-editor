import os
import subprocess
from librosa import load, core
import numpy as np
import librosa
from moviepy.editor import *
from moviepy.editor import VideoFileClip
import moviepy.editor as mp
import math
import shutil
from art import text2art


def strip_audio_from_mkv(mkv_file, output_filename="audio.wav"):
    print("stripping audio from "+mkv_file)
    try:
        shutil.move(mkv_file, os.path.join(processedOriginalVideos, os.path.basename(mkv_file)))
        mkv_file = os.path.join(processedOriginalVideos, os.path.basename(mkv_file))
    except PermissionError:
        print(f"Error: Could not move {inputVideo}. File might be in use.")
    command = ["ffmpeg", "-i", mkv_file, "-vn", "-acodec", "pcm_s16le", output_filename]
    process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    process.communicate()
    process.stdin.close()
    process.stdout.close()
    process.stderr.close()
    process.wait()
    return output_filename

def find_squad_win_audio_pattern(pattern_file, audio_file, correlationThreshold=0.5):
    """Finds occurrences of a pattern within an audio file."""
    print(text2art(f"Scanning audio", font="slant"))
    print(f"Searching for squad win occurences: {pattern_file}")
    hop_length = 2048
    window_length = hop_length

    if not os.path.exists(audio_file):
        print(f"Error: File {audio_file} does not exist.")
        return []

    pattern, sr_pattern = librosa.load(pattern_file, sr=None)
    audio, sr_audio = librosa.load(audio_file, sr=None)

    # Resample pattern if necessary
    if sr_pattern != sr_audio:
        pattern = librosa.resample(pattern, orig_sr=sr_pattern, target_sr=sr_audio)

    # Calculate spectrograms
    pattern_spectrogram = np.abs(librosa.stft(pattern, win_length=window_length, hop_length=hop_length))
    audio_spectrogram = np.abs(librosa.stft(audio, win_length=window_length, hop_length=hop_length))

    pattern_shape = pattern_spectrogram.shape

    def check_correlation(correlation, pattern_file):
        if correlation > correlationThreshold:
            time_in_samples = i * hop_length
            time_in_seconds = math.floor(time_in_samples / sr_audio)
            if time_in_seconds not in time_array:
                time_array.append(time_in_seconds)
                minutes = int(time_in_seconds // 60)
                seconds = int(time_in_seconds % 60)
                print(f"Pattern {pattern_file} detected at: {minutes}:{seconds}, Correlation: {correlation}")

    time_array = []
    # Traverse audio spectrogram
    for i in range(audio_spectrogram.shape[1] - pattern_shape[1]):
        correlation = np.corrcoef(pattern_spectrogram.flatten(), audio_spectrogram[:, i:i + pattern_shape[1]].flatten())[0, 1]
        check_correlation(correlation, pattern_file)

    print(f"time array: {time_array}")
    return time_array

def find_killsound_audio_pattern(pattern_file1, pattern_file2, audio_file):
    """Finds occurrences of a pattern within an audio file."""
    print(text2art(f"Scanning audio", font="slant"))
    hop_length = 512
    window_length = hop_length
    
    if not os.path.exists(audio_file):
        print(f"Error: File {audio_file} does not exist.")
        return
    pattern1, sr_pattern1 = librosa.load(pattern_file1, sr=None)
    pattern2, sr_pattern2 = librosa.load(pattern_file2, sr=None)
    audio, sr_audio = librosa.load(audio_file, sr=None)

    # Resample patterns if necessary
    if sr_pattern1 != sr_audio:
        pattern1 = librosa.resample(pattern1, orig_sr=sr_pattern1, target_sr=sr_audio)
    if sr_pattern2 != sr_audio:
        pattern2 = librosa.resample(pattern2, orig_sr=sr_pattern2, target_sr=sr_audio)

    # Calculate spectrograms
    pattern1_spectrogram = np.abs(librosa.stft(pattern1, win_length=window_length, hop_length=hop_length))
    pattern2_spectrogram = np.abs(librosa.stft(pattern2, win_length=window_length, hop_length=hop_length))
    audio_spectrogram = np.abs(librosa.stft(audio, win_length=window_length, hop_length=hop_length))

    pattern1_shape = pattern1_spectrogram.shape
    pattern2_shape = pattern2_spectrogram.shape

    def check_correlation(correlation, pattern_file, correlation1):
        if correlation > correlationThreshould and correlation != correlation1:
            print(f"Squad kill sound detected: {correlation}, kill sound correlation not met: {correlation1}")
        if correlation > correlationThreshould and correlation1 > 0.25:
            time_in_samples = i * hop_length
            time_in_seconds = math.floor(time_in_samples / sr_audio)
            if time_in_seconds not in time_array:
                time_array.append(time_in_seconds)
                minutes = int(time_in_seconds // 60)
                seconds = int(time_in_seconds % 60)
                print(f"Appending: {pattern_file}, Correlation: {correlation}, Time: {minutes,seconds}")

    time_array = []
    # Traverse audio spectrogram
    for i in range(audio_spectrogram.shape[1] - max(pattern1_shape[1], pattern2_shape[1])):
        correlation1 = np.corrcoef(pattern1_spectrogram.flatten(), audio_spectrogram[:, i:i + pattern1_shape[1]].flatten())[0, 1]
        correlation2 = np.corrcoef(pattern2_spectrogram.flatten(), audio_spectrogram[:, i:i + pattern2_shape[1]].flatten())[0, 1]
        
        check_correlation(correlation1, pattern_file1, correlation1)
        check_correlation(correlation2, pattern_file2, correlation1)

    print(f"time array: {time_array}")
    return time_array

def stitchVideosTogether(times, inputVideo, overlayImage, outroVideo , addIntroAndOverlay):
    """Stitches video clips together, adding an overlay image except for the intro.

    Args:
        times (list): List of timestamps for video clip segments.
        inputVideo (str): Path to the main video file.
        overlayImage (str): Path to the overlay image file.
        addIntroAndOverlay (bool): Whether to add intro and overlay to the video.
    """
    if len(times) == 0: 
        print("No time matches, skipping file")
        return
    print(text2art(f"Stitching videos!", font="slant"))
    print(text2art(f"{len(times)}"))
    inputVideo = inputVideo.replace(inputVideosDir,processedOriginalVideos)
    video = mp.VideoFileClip(inputVideo)
    intro = mp.VideoFileClip(introVideo)
    music = mp.AudioFileClip(introMusic)
    outro = mp.VideoFileClip(outroVideo)
    merged_times = []

    # Merge consecutive times (unchanged)
    i = 0
    while i < len(times):
        start_time = times[i] - timeBeforeKill
        end_time = times[i] + timeAfterKill
        while i + 1 < len(times) and times[i + 1] - times[i] <= timeBeforeKill:
            end_time = times[i + 1] + timeAfterKill
            i += 1
        merged_times.append((start_time, end_time))
        i += 1

    # Load overlay image
    overlay = mp.ImageClip(overlayImage)

    # Create intro clip with music
    intro_with_music = intro.set_audio(music)

    final_clip = []  
    if addIntroAndOverlay:
        final_clip.append(intro_with_music)

    # Overlay logic for remaining clips
    for start_time, end_time in merged_times[0:]:
        clip = video.subclip(start_time, end_time)
        if clip is None:
            print(f"Warning: Subclip creation failed for start_time {start_time} and end_time {end_time}")
            continue  # Skip to the next iteration
        if addIntroAndOverlay:
            # Create a subclip of the overlay limited to the clip duration (unchanged)
            overlay_clip = overlay.subclip(0, clip.duration)

            # Create a composed clip with the current clip and the limited overlay
            composed_clip = mp.CompositeVideoClip([clip, overlay_clip])
            final_clip.append(composed_clip)
        else:
            final_clip.append(clip)

    # Add the outro video at the end of the final clip
    if addIntroAndOverlay:
        final_clip.append(outro)
        #final_clip = mp.concatenate_videoclips([final_clip, outro])
    final_clip = mp.concatenate_videoclips(final_clip)
    # Check final clip duration and adjust resolution if less than a minute
    #if final_clip.duration < 60:
        #print("Final clip duration is less than a minute. Adjusting resolution.")
        #final_clip = final_clip.resize(width=1080, height=1920, resample=PIL.Image.LANCZOS)
    # Write the final video
    final_clip_name = os.path.basename(inputVideo) + "_edited.mp4"
    try:
        final_clip.write_videofile(os.path.join(outputVideosDir, final_clip_name))
    finally:
        final_clip.close()
        video.close()
        print(f"Done writing file: {os.path.join(outputVideosDir, final_clip_name)}")


def removeTempFiles():
    file_path = outputAudio
    if os.path.exists(file_path):
        os.remove(file_path)

def check_file_existence(inputVideo, overlayImage, introVideo, introMusic):
    if not os.path.exists(inputVideo):
        print(f"Error: {inputVideo} does not exist.")
        return False
    if not os.path.exists(overlayImage):
        print(f"Error: {overlayImage} does not exist.")
        return False
    if not os.path.exists(introVideo):
        print(f"Error: {introVideo} does not exist.")
        return False
    if not os.path.exists(introMusic):
        print(f"Error: {introMusic} does not exist.")
        return False
    return True


# Directory path to retrieve videos from
inputVideosDir = "videos_to_process"
outputVideosDir = "processed_videos"
processedOriginalVideos = "processed_original_videos"
outputAudio = "extracted_audio.wav"
overlayImage = "overlay.png"
introVideo = 'intro.mkv'
introMusic = 'intro.wav'
outtroVideo = 'outtro.mp4'

addIntroOuttroAndOverlay = False
timeBeforeKill = 5
timeAfterKill = 2
correlationThreshould = 0.63

print("Population One auto video editor was created by: ")
print("_________________________________________________")
print(text2art("f(x,y,z)"))
print("_________________________________________________")

for directory in [inputVideosDir, outputVideosDir, processedOriginalVideos]:
    os.makedirs(directory, exist_ok=True)

# Get video file paths from the directory
inputVideos = [
    os.path.join(inputVideosDir, file)
    for file in os.listdir(inputVideosDir)
    if file.endswith((".mkv", ".mp4"))  # Filter for video files
]

# Check file existence for all videos and other files
if addIntroOuttroAndOverlay:
    if not all(os.path.exists(file) for file in [overlayImage, introVideo, introMusic]):
        print("Exiting script: addIntroOuttroAndOverlay is True, but not all of the files were found!")
        exit()

if not inputVideos:  # Check if the list is empty
    print("Error: No video files found in the 'videos_to_process' directory.")
    exit()



# Iterate through each input video
for inputVideo in inputVideos:
    removeTempFiles()  # Reinitialize for each video
    extracted_audio_file = strip_audio_from_mkv(inputVideo, outputAudio)
    time_occurrences = find_killsound_audio_pattern("ding.wav", "Hitsound_SquadElimination.wav", extracted_audio_file)
    stitchVideosTogether(time_occurrences, inputVideo,overlayImage, outtroVideo, addIntroOuttroAndOverlay)