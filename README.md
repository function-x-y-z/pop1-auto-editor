# pop1-auto-editor
This repo can automatically edit videos in the VR game Population One.   It detects kill events and stitches those videos together into a final edited video.

My youtube channel videos were all created via this script:  https://www.youtube.com/@function_xyz9676

My workflow is this:
I record playing sessions and save them into a folder 'videos_to_process' at the root of this repo.
Once I've accumulated enough videos, I run 'extractDeathTimes.py';  this will parse all the videos within that folder.



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

### Step 2: Install Dependencies

Install the required Python packages listed in the requirements.txt file:
```bash
pip install -r requirements.txt
```
 ### Step 3: Run the Script

Once the dependencies are installed, you can run the script to automatically edit the videos. For example:

python extractDeathTimes.py

### IMPORTANT

I use a boolean within extractDeathTimes.py named 'addIntroOuttroAndOverlay'; which will add my intro video, outro, and an overlay image to the final movie.
Set this to 'False' if you do not want those added.  
