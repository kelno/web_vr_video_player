def is_video_file(filename):
    video_extensions = ('.mp4', '.mkv', '.avi', '.mov', '.webm')
    return filename.lower().endswith(video_extensions)
