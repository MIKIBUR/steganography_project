from PIL import Image
import re
import random
import argparse
import os

# Function to convert message to binary
def message_to_binary(message):
    return ''.join([format(ord(i), "08b") for i in message])

# Function to convert binary to string
def binary_to_string(binary_message):
    return ''.join([chr(int(binary_message[i:i + 8], 2)) for i in range(0, len(binary_message), 8)])

def generate_random_noise(length):
    return ''.join(random.choice(['0', '1']) for _ in range(int(length-16)))

# Function to encode the message into the image with dynamic LSB encoding
def encode_image(image_path, message, lorem=False, given_lsb=0,percent=100):
    img = Image.open(image_path)
    img = img.convert('RGB')
    
    # Initial number of LSBs to use
    lsb_count = 1
    max_lsb = 8  # Limit to 8 LSBs max (beyond which it degrades the image quality drastically)
    binary_message = message_to_binary(message) + '1111111111111111'
    
    width, height = img.size
    pixels = img.load()
    base_capacity = width * height * 3

    if not(lorem and lsb_count != 0):
        while True:
            capacity = width * height * 3 * lsb_count
            print(f"Trying with {lsb_count} LSB(s)")
            print(f"Available capacity in bits: {capacity}")
            print(f"Message length in bits: {len(binary_message)}")
            print(f"Percent use of available space: {len(binary_message) / capacity * 100}%")
            print(f" ")

            if len(binary_message) <= capacity:
                break
            elif lsb_count < max_lsb:
                lsb_count += 1  # Increase LSBs if message doesn't fit
            else:
                print("Error: Message too large, even with maximum LSBs.")
                return
    else:
        binary_message = generate_random_noise(base_capacity*given_lsb*percent/100) + '1111111111111111'
        lsb_count = given_lsb

    # Store the LSB count in the first 3 bytes of the image (using 3 bits per channel)
    binary_lsb_count = format(lsb_count, '08b')
    pixels[0, 0] = (
        (pixels[0, 0][0] & 0xF8) | int(binary_lsb_count[:3], 2),
        (pixels[0, 0][1] & 0xF8) | int(binary_lsb_count[3:6], 2),
        (pixels[0, 0][2] & 0xFC) | int(binary_lsb_count[6:], 2)
    )
    
    message_index = 0
    for y in range(height):
        for x in range(1 if y == 0 else 0, width):  # Skip the first pixel
            r, g, b = pixels[x, y]
            channels = [r, g, b]
            
            for i in range(3):  # Loop through RGB channels
                if message_index < len(binary_message):
                    channels[i] = (channels[i] & (0xFF - (2 ** lsb_count - 1))) | int(binary_message[message_index:message_index + lsb_count], 2)
                    message_index += lsb_count
                else:
                    break
            
            pixels[x, y] = tuple(channels)
            
            if message_index >= len(binary_message):
                break
        if message_index >= len(binary_message):
            break

    os.makedirs('output/' + image_path.split('.')[0], exist_ok=True)
    output_image_path = f"output/{image_path.split('.')[0]}/LSB{lsb_count}{'_Percent' + str(percent) if lorem else ''}.png"

    img.save(output_image_path)
    print(f"Message encoded using {lsb_count} LSB(s) and saved to {output_image_path}")
    # print(f"Binary message tail: {binary_message[-16:]}")
    # print(f"Binary message length: {len(binary_message)}")
    return output_image_path

# Function to decode the hidden message from the image with dynamic LSB decoding
def decode_image(image_path):
    img = Image.open(image_path)
    img = img.convert('RGB')
    pixels = img.load()

    # Retrieve the LSB count from the first pixel
    lsb_count = (
        ((pixels[0, 0][0] & 0x07) << 5) |
        ((pixels[0, 0][1] & 0x07) << 2) |
        ((pixels[0, 0][2] & 0x03))
    )
    
    print(f"Detected LSB count: {lsb_count}")
    
    binary_message = ""
    width, height = img.size
    end_marker = '1111111111111111'
    
    for y in range(height):
        for x in range(1 if y == 0 else 0, width):  # Skip the first pixel
            r, g, b = pixels[x, y]
            channels = [r, g, b]
            
            for i in range(3):  # Loop through RGB channels
                binary_message += format(channels[i] & (2 ** lsb_count - 1), f'0{lsb_count}b')
                if binary_message.endswith(end_marker):
                    message = binary_to_string(binary_message[:-16])  # Exclude marker and offset
                    # print(binary_message[24727184:24727200])
                    # print(len(binary_message))
                    return message.strip()  # Strip any trailing newlines or spaces

    return "No hidden message found"

# Function to sanitize the input message
def sanitize_message(message):
    # Remove any non-ASCII characters using a regular expression
    return re.sub(r'[^\x00-\x7F]+', '', message)

# Function to read the message from a text file
def read_message_from_file(file_path):
    with open('text/'+file_path, 'r', encoding='utf-8', errors='ignore') as file:
        message = file.read().strip()  # Read the content and remove any leading/trailing whitespace
    return sanitize_message(message)

# Function to combine messages from multiple files
def combine_messages(file_paths):
    combined_message = ""
    for i, path in enumerate(file_paths):
        combined_message += read_message_from_file(path)
        if i < len(file_paths) - 1:  # Add a newline only if it's not the last file
            combined_message += "\n"
    return combined_message

# Main function that takes file paths and image paths as input parameters
def process_steganography(text_file_paths, input_image_path, output_text_file_path, lorem=False, given_lsb=0,percent=100):
    # Combine messages from input text files
    secret_message = combine_messages(text_file_paths)

    # Encode the combined message into the image using dynamic LSB encoding
    output_image_path = encode_image('images/'+input_image_path, secret_message, lorem, given_lsb,percent)

    # Decode the message from the image
    decoded_message = decode_image(output_image_path)
    
    # Save the decoded message to the result text file
    with open(output_text_file_path, 'w', encoding='utf-8') as result_file:
        result_file.write(decoded_message.strip())
    
    print(f"Decoded message saved to {output_text_file_path}")

# CLI support with argparse
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Steganography tool to hide and extract text messages from images.")
    
    # Default values for file paths and image paths
    default_file_paths = ['lotr0.txt', 'lotr1.txt', 'lotr2.txt', 'lotr3.txt']
    default_source_image_path = 'small_img.jpg'
    default_output_text_file = 'result.txt'

    # Add arguments for the CLI
    parser.add_argument('--file_paths', nargs='+', default=default_file_paths, help='Paths to the text files containing the secret message')
    parser.add_argument('--source_image', default=default_source_image_path, help='Path to the input image')
    parser.add_argument('--output_text', default=default_output_text_file, help='Path to save the decoded text')
    parser.add_argument('--lorem', action='store_true', help='Enable random noise instead of a message')
    parser.add_argument('--given_lsb', type=int, default=0, help='Number of LSBs to use for encoding')
    parser.add_argument('--percent', type=int, default=100, help='Percentage of available space to use for encoding')

    # Parse the arguments
    args = parser.parse_args()

    # Call the main function with the parsed arguments
    process_steganography(
        args.file_paths,
        args.source_image,
        args.output_text,
        lorem=args.lorem,
        given_lsb=args.given_lsb,
        percent=args.percent
    )
