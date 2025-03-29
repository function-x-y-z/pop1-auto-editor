import os
import subprocess
import numpy as np
import librosa
from moviepy.editor import *
import moviepy.editor as mp
import math
import shutil
from art import text2art
from tqdm import tqdm


# build command:  
#  venv\Scripts\activate
#  pyinstaller --onefile --console --add-data "ding.wav;." --add-data "Hitsound_SquadElimination.wav;." pop1-auto-editor.py

def strip_audio_from_mkv(mkv_file, output_filename="audio.wav"):
    print("Processing file: "+mkv_file)
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

    def check_correlation(correlation, correlation1):
        if correlation > correlationThreshould and correlation != correlation1:
            tqdm.write(f"Squad kill sound detected: {correlation},but kill sound correlation not met: {correlation1}")
        if correlation > correlationThreshould and correlation1 > 0.25:
            time_in_samples = i * hop_length
            time_in_seconds = math.floor(time_in_samples / sr_audio)
            if time_in_seconds not in time_array:
                time_array.append(time_in_seconds)
                minutes = int(time_in_seconds // 60)
                seconds = int(time_in_seconds % 60)
                tqdm.write(f"Kill detected with correlation: {correlation} @ {minutes,seconds}")

    time_array = []
    # Traverse audio spectrogram
    loop_range = range(audio_spectrogram.shape[1] - max(pattern1_shape[1], pattern2_shape[1]))
    for i in tqdm(loop_range, desc="Processing", unit="step"):
        correlation1 = np.corrcoef(pattern1_spectrogram.flatten(), audio_spectrogram[:, i:i + pattern1_shape[1]].flatten())[0, 1]
        correlation2 = np.corrcoef(pattern2_spectrogram.flatten(), audio_spectrogram[:, i:i + pattern2_shape[1]].flatten())[0, 1]
        
        check_correlation(correlation1, correlation1)
        check_correlation(correlation2, correlation1)

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
    if addIntroAndOverlay:
        intro = mp.VideoFileClip(introVideo)
        music = mp.AudioFileClip(introMusic)
        outro = mp.VideoFileClip(outroVideo)
    merged_times = []

    # Merge consecutive times
    i = 0
    while i < len(times):
        start_time = times[i] - timeBeforeKill
        end_time = times[i] + timeAfterKill
        while i + 1 < len(times) and times[i + 1] - times[i] <= timeBeforeKill:
            end_time = times[i + 1] + timeAfterKill
            i += 1
        merged_times.append((start_time, end_time))
        i += 1

    final_clip = []  
    if addIntroAndOverlay:
        overlay = mp.ImageClip(overlayImage)
        intro_with_music = intro.set_audio(music)
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

def get_resource_path(filename):
    """Get the correct path for bundled files when running as an .exe."""
    if getattr(sys, 'frozen', False):  # Check if running as a bundled executable
        base_path = sys._MEIPASS  # Temporary folder used by PyInstaller
    else:
        base_path = os.path.dirname(__file__)  # Normal script execution
    return os.path.join(base_path, filename)

def copy_media_files_to_dir():
    """Copy bundled files to the current working directory if they don’t exist."""
    files_to_copy = ["ding.wav", "Hitsound_SquadElimination.wav"]  # List your files here
    for file in files_to_copy:
        source_path = get_resource_path(file)
        destination_path = os.path.join(os.getcwd(), file)  # Copy to execution dir

        if not os.path.exists(destination_path):  # Avoid overwriting existing files
            shutil.copy(source_path, destination_path)
            print(f"Copied {file} to {destination_path}")

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
correlationThreshould = 0.66

print("Population One auto video editor was created by: ")
print("_________________________________________________")
print(text2art("f(x,y,z)", font="slant"))
print("_________________________________________________")

for directory in [inputVideosDir, outputVideosDir, processedOriginalVideos]:
    os.makedirs(directory, exist_ok=True)

copy_media_files_to_dir()
# Get video file paths from the directory
inputVideos = [
    os.path.join(inputVideosDir, file)
    for file in os.listdir(inputVideosDir)
    if file.endswith((".mkv", ".mp4"))  # Filter for video files
]

try:
    # Check file existence for all videos and other files
    if addIntroOuttroAndOverlay:
        if not all(os.path.exists(file) for file in [overlayImage, introVideo, introMusic]):
            raise FileNotFoundError("Exiting script: addIntroOuttroAndOverlay is True, but not all of the files were found!")

    if not inputVideos:  # Check if the list is empty
        raise FileNotFoundError("Error: No video files found in the 'videos_to_process' directory.")

except Exception as e:
    print(f"\n An error occurred: {e}")
    input("\n Press Enter key to exit...")
    sys.exit(1)



# Iterate through each input video
for inputVideo in inputVideos:
    removeTempFiles()  # Reinitialize for each video
    extracted_audio_file = strip_audio_from_mkv(inputVideo, outputAudio)
    time_occurrences = find_killsound_audio_pattern("ding.wav", "Hitsound_SquadElimination.wav", extracted_audio_file)
    stitchVideosTogether(time_occurrences, inputVideo,overlayImage, outtroVideo, addIntroOuttroAndOverlay)