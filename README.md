# pop1-auto-editor
This repo can automatically edit videos in the VR game Population One.   It detects kill events and stitches those videos together into a final edited video.  The detection rate for downing an enemy is about 65-70% at the moment.

# How I use this editor.
I typically save recorded video files directly into the 'videos_to_process' folder, at the root of the project (create it if absent).
For a good rule of thumb, if a recorded video is about 1 hour long, it will produce a 3 minute long edited video.
I like to get many, many videos recorded within that folder, and then run the script overnight.

## Installation Instructions

### Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.10** (or higher)
- **pip** (Python package installer)

### Step 1: Clone the Repository

First, clone the repository to your local machine using Git:

```bash
git clone https://github.com/function-x-y-z/pop1-auto-editor.git
cd pop1-auto-editor
```
Step 2: Install Dependencies

Install the required Python packages listed in the requirements.txt file:
```bash
pip install -r requirements.txt
```
Step 3: Run the Script

Once the dependencies are installed, you can run the script to automatically edit the videos. For example:
```bash
python extractDeathTimes.py
```

### Customization:

There is a boolean within the script 'addIntroOuttroAndOverlay = True';  this boolean decides weather to add an intro video, outro, and an overlay image.  You can see how I named those files within the script.
Set this to false to just get the edited kill clips.