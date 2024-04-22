from detecto.core import Model
from detecto.utils import read_image
import numpy as np
from PIL import Image
import keras

def image_processing():
    '''
    Still need to do this, but this will take the image file, use PIL to binzarize (make black and white a la a scanned document
    and return the binarize image)
    '''
    pass

def line_detection(line_model, image, threshold=0.9):

    _, boxes, scores = line_model.predict(image)

    high_confidence_indices = scores >= threshold
    filtered_boxes = boxes[high_confidence_indices]

    return image, filtered_boxes

def symbol_detection(symbol_model, image, box, threshold=0.9):
    #unfinished - fundamentally similar to line_detection
    cropped_image = image.crop((int(box[0]), int(box[1]), int(box[2]), int(box[3])))

    cropped_img_array = np.array(cropped_image)

    _, boxes, scores = symbol_model.predict(cropped_img_array)

    high_confidence_indices = scores >= threshold
    filtered_boxes = boxes[high_confidence_indices]

    #need to also do non-max suppresion
    return filtered_boxes

def symbol_recognition(recognition_model, image, box):
    cropped_image = image.crop((int(box[0]), int(box[1]), int(box[2]), int(box[3])))

    width, height = cropped_image.size
    if width > height:
        diff = width - height
        padding = (0, diff // 2, 0, diff - (diff // 2))
    elif height > width:
        diff = height - width
        padding = (diff // 2, 0, diff - (diff // 2), 0)
    else:
        padding = (0, 0, 0, 0)

    padded_image = Image.new("RGB", (max(width, height), max(width, height)), (255, 255, 255))
    padded_image.paste(cropped_image, (padding[0], padding[1]))

    resized_image = Image.resize((45, 45), Image.LANCZOS)

    resized_array = np.array(resized_image)

    proba = recognition_model.predict(resized_array)[0]

    character_dct = {1: '(', 2: ')', 3:'+', 5:'-', 6:'0', 7:'1', 
                     8:'2', 9:'3', 10:'4', 11:'5', '12':'6', 13:'7', 
                     14:'8', 15:'9', 16:'=', 36:'/', 78:'y', 27:'x'}
    top_classes = np.argsort(proba)[::-1]
    pred = [x for x in top_classes if x in character_dct.keys()][0]
    return character_dct[pred]

def scan_image(image_path):
    image = image_processing(image_path)

    line_model = Model.load('complete_line_detection.pth', ['line'])
    symbol_model = 'symbol_model'
    recognition_model = keras.models.load_model("mathsymbols.model")

    line_boxes = line_detection(line_model, image)
    image_result = []


    for box in line_boxes:
        character_boxes = symbol_detection(symbol_model, image, box)
        character_results = [symbol_recognition(recognition_model, image, x) for x in character_boxes]
        line_string = character_results.join()
        image_result.append(line_string)

    return image_result
