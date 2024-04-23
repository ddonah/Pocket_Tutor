from detecto.core import Model
from detecto.utils import read_image
import numpy as np
from PIL import Image
from PIL import ImageOps
import keras
import pillow_heif
import cv2
import torch
import cv2

def process_image(image_path):
    if image_path.split('.')[-1] == 'HEIC':
        heif_img = pillow_heif.read_heif(image_path)
        img = Image.frombytes(
            heif_img.mode,
            heif_img.size,
            heif_img.data,
            'raw'
        )
        img = np.array(img)
        if img.shape[2] == 4: 
            img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)
    else:
        img = cv2.imread(image_path)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, otsu_thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    adjusted_thresh_value = max(0, (_ - 0.11 * 255))

    _, adjusted_thresh = cv2.threshold(blur, adjusted_thresh_value, 255, cv2.THRESH_BINARY_INV)
    
    final_image = cv2.bitwise_not(adjusted_thresh)
    
    pil_image = Image.fromarray(final_image)

    return pil_image

def line_detection(line_model, image, threshold=0.9):

    lines, boxes, scores = line_model.predict(image)

    high_confidence_indices = scores >= threshold
    filtered_boxes = boxes[high_confidence_indices]

    return image, lines, filtered_boxes

def symbol_detection(symbol_model, image, box, threshold=0.9):
    #unfinished - fundamentally similar to line_detection
    cropped_image = image.crop((int(box[0]), int(box[1]), int(box[2]), int(box[3])))

    rgb_cropped_image = cropped_image.convert('RGB')
    rgb_cropped_image_padded = ImageOps.expand(rgb_cropped_image, border=(0, 60, 0, 60), fill='white')

    #cropped_img_array = np.array(rgb_cropped_image_padded)

    _, boxes, scores = symbol_model.predict(rgb_cropped_image_padded)

    high_confidence_indices = scores >= threshold
    filtered_boxes = boxes[high_confidence_indices]
    filtered_scores = scores[high_confidence_indices]
    characters = ['character'] * len(filtered_scores)

    #need to also do non-max suppresion
    return rgb_cropped_image_padded, filtered_boxes

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

    resized_image = padded_image.resize((45, 45), Image.LANCZOS)

    resized_array = np.array(resized_image)

    resized_array = resized_array.astype('float32') / 255.0

    resized_array = np.expand_dims(resized_array, axis=0)

    proba = recognition_model.predict(resized_array)[0]

    character_dct = {1: '(', 2: ')', 3:'+', 5:'-', 6:'0', 7:'1', 
                     8:'2', 9:'3', 10:'4', 11:'5', '12':'6', 13:'7', 
                     14:'8', 15:'9', 16:'=', 36:'/', 78:'y', 27:'x'}
    top_classes = np.argsort(proba)[::-1]
    pred = [x for x in top_classes if x in character_dct.keys()][0]
    return character_dct[pred]

def check_multiplication(line_list):
    numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    symbols = ['+', '-', '*']
    variables = ['x', 'y']
    parenthensis = ['(', ')']

    positions = [index for index, value in enumerate(line_list) if value == 'x']
    if positions:
        for position in positions:
            if (position > 0) and (position < len(line_list)-1):
                if line_list[position - 1] in symbols or line_list[position + 1] in symbols:
                    continue
                elif line_list[position - 1] in numbers and line_list[position + 1] in numbers:
                    line_list[position] = '*'
                    continue
    
    return line_list

def pipeline(image_path):
    line_model = Model.load('line_detection.pth', ['line'])
    character_detection_model = Model.load('character_detector.pth', ['character'])
    recognition_model = keras.models.load_model("mathsymbols.model")

    image = process_image(image_path)
    image_rgb = image.convert('RGB')
    image_rgb, lines, line_boxes = line_detection(line_model, image_rgb)

    _, sorted_indices = torch.sort(line_boxes[:, 1])
    sorted_line_boxes = line_boxes[sorted_indices]
    result_list = []

    for line_box in sorted_line_boxes:
        line_list = []

        line_cropped_image, symbol_boxes = symbol_detection(character_detection_model, image, line_box)

        _, sorted_indices = torch.sort(symbol_boxes[:, 0])
        sorted_symbol_boxes = symbol_boxes[sorted_indices]

        for symbol_box in sorted_symbol_boxes:
            predicted_element = symbol_recognition(recognition_model, line_cropped_image, symbol_box)

            line_list.append(predicted_element)
        
        line_list = check_multiplication(line_list)

        result_list.append(line_list)
    
    result_list = [''.join(x) for x in result_list]

    with open('unconfirmed_results.txt', 'w') as f:
        for line in result_list:
            f.write(f'{line}\n')

    f.close()

def main():
    image_path = 'need-to-connect-this'

    pipeline(image_path)

if '__main__' in __name__:
    main()

