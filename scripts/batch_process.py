import math
import os
import sys
import traceback
import json
import modules.scripts as scripts
import gradio as gr
from pathlib import Path
from modules.processing import Processed, process_images

class Script(scripts.Script):
    positive_prompt = ""
    def title(self):
        return "Batch Process Inputs"

    def ui(self, is_img2img):
        weight = gr.Textbox(label="prompt_weight")
        return [weight]

    def run(self, p, weight):
        # set working directory to current folder
        rootDir = "D:/git/stable-diffusion-webui/"
        original_prompt = p.prompt
        # get the path/directory to inputs
        input_dir = rootDir + "inputs"
        for image in os.listdir(input_dir):
            # check if the image ends with png
            if (image.endswith(".png")):
                tag = Path(image).stem  
                print(tag)
                p.prompt = "("+ str(tag) +":" + str(weight) + ")," + original_prompt
                p.control_net_weight = 0.8
                
                p.control_net_enabled = True
                p.control_net_model = "control_v11p_sd15_scribble"
                proc = process_images(p)
                image = proc.images
        return Processed(p, image, p.seed, proc.info)
       