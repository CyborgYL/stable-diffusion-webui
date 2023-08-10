import io
import cv2
import base64
import requests
from pathlib import Path
import os
from PIL import Image
from PIL.PngImagePlugin import PngInfo
# A1111 URL
url = "http://127.0.0.1:7860"
orinial_prompt = "(realistic:1.0),style by pixar,beautiful,masterpiece,best quality, cheerful,<lora:add_detail:1>, <lora:blindbox_v1_mix:0.3> "

rootDir = os.path.dirname(os.path.realpath(__file__))
inputDir = rootDir + "/input/"
fileName = "car.png"
# check if the image ends with png
if (fileName.endswith(".png")):
    tag = Path(fileName).stem
    print(tag)
    # Read Image in RGB order
    img = cv2.imread(inputDir + fileName)
    # Encode into PNG and send to ControlNet
    retval, bytes = cv2.imencode('.png', img)
    encoded_image = base64.b64encode(bytes).decode('utf-8')
    # A1111 payload
    payload = {
        "prompt": "(" + tag + ":1.1)," + orinial_prompt,
        "negative_prompt": "(morbid:1.2),(horror:1.1),(cropped:1.2),blurry,evil,(negative_hand-neg:1.0),(easynegative:0.8),ugly,winkle,extra head,long body,long neck,long finger,out of frame,long face,extra face,terrifying,bad proportion,malformed,nsfw,nude,nudity,blood,violence,weapon,brand,logo,text,trademark,monster,ghost,grumpy",
        "batch_size": 1,
        "sampler_name": "Euler a",
        "steps": 10,
        "width": 384,
        "height": 640,
        "cfg_scale": 7.5,
        "seed":42,
        "save_images": True,
        "enable_hr": True,
        "denoising_strength": 0.7,
        "hr_scale": 1.5,
        "hr_upscaler": "Latent (nearest-exact)",
        "hr_second_pass_steps": 15,
        "alwayson_scripts": {
            "controlnet": {
                "args": [
                    {
                        "input_image": encoded_image,
                        "module": "invert",
                        "model": "control_v11p_sd15_scribble [d4ba51ff]",
                        "weight": 0.8,
                        "resize_mode": "Just Resize",
                        "width": 384,
                        "height": 640,
                        "control_mode":"Balanced"
                    }
                ]
            }
        }
    }
    
    # Trigger Generation
    response = requests.post(url=f'{url}/sdapi/v1/txt2img', json=payload)
    # Read results
    r = response.json()
    result = r['images'][0]
    info = r['info']
    metadata = PngInfo()
    metadata.add_text("parameters", info)
    
    image = Image.open(io.BytesIO(base64.b64decode(result.split(",", 1)[0])))
    image.save(rootDir + "/output/" + tag +".png", pnginfo=metadata)