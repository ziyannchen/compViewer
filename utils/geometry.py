from PIL import Image, ImageSequence
import numpy as np

def transform_gif(input_gif, output_gif, target_size, resample=Image.Resampling.LANCZOS):
    # dx, dy = transform_matrix[2], transform_matrix[5]
    t_w, t_h, dx, dy, sx, sy = target_size
    # Open the input GIF
    original_gif = Image.open(input_gif)

    # Get frames and apply transformation
    frames = []
    for frame in ImageSequence.Iterator(original_gif):
        # Convert the frame to numpy array
        # frame = frame.convert('RGBA')
        w, h = frame.size
        # print(w, h, dx, dy, t_w, t_h)
        dx, dy = min(w, max(dx, 0)), min(h, max(dy, 0))
        # print(w, h, dx, dy, t_w, t_h)
        
        # Apply the transformation
        transformed_image = frame.resize((int(sx * w), int(sy * h)), resample)
        # transformed_image = transformed_image.convert('P', palette=Image.ADAPTIVE, dither=Image.FLOYDSTEINBERG)
        # Convert back to PIL Image and append to frames list
        frames.append(transformed_image.crop((dx, dy, dx+t_w, dy+t_h)))
    
    # Save frames as new GIF
    frames[0].save(output_gif, save_all=True, append_images=frames[1:], loop=0, duration=original_gif.info['duration'], optimize=True)