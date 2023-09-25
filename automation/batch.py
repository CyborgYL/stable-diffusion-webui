import io
import shutil
import cv2
import base64
import requests
from pathlib import Path
import os
from PIL import Image
from PIL.PngImagePlugin import PngInfo
import json
import utility
    
# A1111 URL
url = "http://127.0.0.1:7862"

rootDir = os.path.dirname(os.path.realpath(__file__))
model = 'ToonMe'
runID = '0918'

inputDir = f"{rootDir}/input/test"
outputDir = f"{rootDir}/output/{model}_{runID}/caption"
promptDir = f"{rootDir}/prompt"
if not os.path.exists(outputDir):
    os.makedirs(outputDir)
category_data = utility.loadCategory(f"{promptDir}/prompt.xlsx", model)

for image in os.listdir(inputDir):
    # check if the image ends with png
    if (image.endswith('.png') or image.endswith('.jpg') or image.endswith('.PNG') or image.endswith('.JPG')):
       
        imageName = Path(image).stem
        index = imageName.split('_')[0]
        blip = imageName.split('_')[1]
        fixedBlip = utility.fixTag(blip)
        category, tag = utility.detectCategory(category_data, fixedBlip)
        prompt_tag = fixedBlip
        if os.path.isfile(f'{outputDir}/all/{index}_{category}_{prompt_tag}.png'):
            print(f'File "{index}_{category}_{prompt_tag}" exists, skip...')
            continue
        generated_prompt_file = f"{promptDir}/generated/{model}/{category}.json"
        if not os.path.exists(generated_prompt_file):
            print(f'category:{category} not ready, skipping image...{imageName}')
            continue
        # Read Image in RGB order
        img = cv2.imread(f'{inputDir}/{image}')
        # Encode into PNG and send to ControlNet
        retval, bytes = cv2.imencode('.png', img)
        encoded_image = base64.b64encode(bytes).decode('utf-8')
        # A1111 payload
        with open(generated_prompt_file,'r') as promptFile:
            payload = json.load(promptFile)
            orinial_prompt = payload["prompt"]
            payload["alwayson_scripts"]["ControlNet"]["args"][0]["input_image"] = encoded_image
            #fix seed for testing
            payload['seed'] = 42
            # Trigger Generation caption
            payload["prompt"] = orinial_prompt.replace('{tag}', prompt_tag)
            response = requests.post(url=f'{url}/sdapi/v1/txt2img', json=payload)
            print(f'{index}_{category}--{fixedBlip}--{tag}')
            # Read results
            r = response.json()
            if 'error' in r:
                print(f'error: {r["error"]}, detail: {r["detail"]}')
                continue
            result = r['images'][0]
            info_dict = json.loads(r['info'])
            parameter = info_dict['infotexts'][0]
            metadata = PngInfo()
            metadata.add_text("parameters", parameter)
            generated_image = Image.open(io.BytesIO(base64.b64decode(result.split(",", 1)[0])))
            if not os.path.exists(f'{outputDir}/all'):
                os.makedirs(f'{outputDir}/all')
            if not os.path.exists(f'{outputDir}/all_jpg'):
                os.makedirs(f'{outputDir}/all_jpg')
            generated_image.save(f'{outputDir}/all/{index}_{category}_{prompt_tag}.png',quality=80, optimize=True, pnginfo=metadata)
            generated_image.save(f'{outputDir}/all_jpg/{index}_{category}_{prompt_tag}.jpg',quality=80, optimize=True, pnginfo=metadata)
            if not os.path.exists(f'{outputDir}/{category}'):
                os.makedirs(f'{outputDir}/{category}')
            generated_image.save(f'{outputDir}/{category}/{index}_{category}_{prompt_tag}.jpg',quality=80, optimize=True, pnginfo=metadata)
            shutil.copy2(os.path.join(inputDir, image), f'{outputDir}/{category}/{index}_input_{category}_{prompt_tag}.jpg')
