#!/usr/bin/env python

import os, subprocess, re

# This gets the path for video that user wants to check
video_path = input("Enter ABSOLUTE path of your video that you want to check: ")
webm_video_path = re.sub(r'\.mp4', '.webm', video_path)

# Define a function that will display total duration of given video and additionally calculate average bitrate 
def probe_video(video):
    # When put in shell, ffprobe will output only duration of source video in seconds
    # Same should happen here
    dur = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', video]
    # Return the output of cmd variable to subprocess
    ff_dur = str(float(subprocess.check_output(dur, text=True).strip()))
    # Print duration of a video that user provided this script with
    print('\n' + "Duration of your video:", ff_dur, "s")
    # Source video framerate output
    fps = ['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=avg_frame_rate', '-of', 'default=noprint_wrappers=1:nokey=1', video]

    str_ff_fps = subprocess.check_output(fps, text=True).strip()

    numerator, denominator = str_ff_fps.split("/")
    numerator = int(numerator)
    denominator = int(denominator)

    ff_fps = numerator / denominator

    print('\n' + f"Framerate of your video: {ff_fps:.2f} fps")
    # Quickly convert ff_dur to float, for compatibility with coming math equation
    ff_dur_float = float(ff_dur)
    # Equation for calculating average bitrate that should be used by ffmpeg/libvpx-vp9 to fit in to Discord's 10 MB file size limit
    global abr
    abr = str(round((10 * 1024 * 0.99) / ff_dur_float * 8))
    # Print calculated average bitrate from earlier equation 
    print('\n' + "Approximate average bitrate for your video:", abr, "Kb/s")
    # Calculate keyframe interval
    global g_fps
    g_fps = round((ff_fps * 5))
    print('\n' + "Approximate keyframe interval based on your video's framerate:", g_fps, "frames")

# This calls the function to display duration of source video and its calculated average bitrate
probe_video(video_path)

print('\n' + "FFmpeg syntax for first pass:" + '\n', 
      "ffmpeg -hwaccel vaapi -hwaccel_output_format vaapi -i", video_path, "-c:v libvpx-vp9 -pass 1 -b:v " + abr + 'k', "-row-mt 1 -cpu-used 0 -deadline best -g", g_fps, "-enable-tpl 1 -auto-alt-ref 1 -arnr-maxframes 7 -arnr-strength 4 -lag-in-frames 25 -an -sn -f null -")
print('\n' + "FFmpeg syntax for second pass:" + '\n', 
      "ffmpeg -hwaccel vaapi -hwaccel_output_format vaapi -i", video_path, "-c:v libvpx-vp9 -pass 2 -b:v " + abr + 'k', "-row-mt 1 -cpu-used 3 -deadline good -g", g_fps, "-enable-tpl 1 -auto-alt-ref 1 -arnr-maxframes 7 -arnr-strength 4 -lag-in-frames 25 -c:a copy -sn -f webm", webm_video_path)
