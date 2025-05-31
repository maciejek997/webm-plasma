#!/usr/bin/env python

import os, subprocess

# This gets the path for video that user wants to check
video_path = input("Enter ABSOLUTE path of your video that you want to check: ")

# Define a function that will display total duration of given video and additionally calculate average bitrate 
def probe_video(video):
    # When put in shell, ffprobe will output only duration of source video in seconds
    # Same should happen here
    cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', video]
    # Return the output of cmd variable to subprocess
    ff_out = subprocess.check_output(cmd, text=True).strip()
    # Print duration of a video that user provided this script with
    print("Duration of your video:", ff_out)
    # Quickly convert ff_out to float, for compatibility with coming math equation
    ff_float = float(ff_out)
    # Equation for calculating average bitrate that should be used by ffmpeg/libvpx-vp9 to fit in to Discord's 10 MB file size limit
    abr = (10 * 1024 * 0.99) / ff_float * 8
    # Print calculated average bitrate from earlier equation 
    print("Approximate average bitrate for your video:", abr, "Kb/s")

# This calls the function to display duration of source video and its calculated average bitrate
probe_video(video_path)
