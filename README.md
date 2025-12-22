# Wplace AI Vtuber

This is a LLM (large language model) that comments on random user drawings on the website wplace.live. The LLM behaves
like a live streamer.
However, to start a real stream or record a video, you need to use third-party tools. Also note that requests to the LLM
model are sent through the Cloudflare API

### Demonstration of work

<video src="https://github.com/user-attachments/assets/edb038f6-cd38-4eba-bc8d-7f1f56a63dd2" width="480" height="270" controls></video>

### Features

* Imitating streamer behavior. The LLM greets viewers, says goodbye to them, and comments on random drawings on the
  website wplace.live
* Voice-over of text received from LLM using TTS (text to speech) model
* Simulating a webcam using an image overlay on a website. The images change depending on the LLM responses,
  simulating different moods.

### Used technology

* Python 3.12
* [Silero TTS](https://github.com/snakers4/silero-models) (Voice generation)
* Selenium (Opening and interacting with a browser window)
* PyAudio (Sound output)
* [Cloudflare Workers AI](https://developers.cloudflare.com/workers-ai/) (API to access the LLM model. Has a free plan)
* FastAPI (server for accessing local files through the website)

### Installation

* Make sure ffmpeg is installed on your computer
* Replace the images in the `static` folder with your own with the same file names
* Edit file `example.env` and fill it with your data, then rename it to `.env`. This is a file with all the configs
* Edit file `prompts.py` and fill it with your data. This file contains templates of all prompts that are sent via the
  Cloudflare API
* Run the python script with the following commands:  
  `pip install -r requirements.txt`  
  `python -m app.main`
* After launching, wait for the message in the console "Press enter to start"