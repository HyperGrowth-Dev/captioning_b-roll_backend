import ffmpeg
from moviepy.editor import *

probe = ffmpeg.probe('input/input_cdd8ae21-4d16-4b8c-bf80-3181a9ebd62d.mp4')
video_streams = [stream for stream in probe["streams"] if stream["codec_type"] == "video"]

print(video_streams)

video = VideoFileClip('input/input_cdd8ae21-4d16-4b8c-bf80-3181a9ebd62d.mp4')

print(video.size)

print(video.w)

print(video.h)


