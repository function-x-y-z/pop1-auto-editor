# pop1-auto-editor
This repo can automatically edit videos in the VR game Population One.   It detects kill events and stitches those videos together into a final edited video.

My youtube channel videos were all created via this script:  https://www.youtube.com/@function_xyz9676

My workflow is this:
I record playing sessions and save them into a folder 'videos_to_process' at the root of this repo.
Once I've accumulated enough videos, I run 'extractDeathTimes.py';  this will parse all the videos within that folder.

