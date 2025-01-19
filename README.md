# Steganography Tool

This project implements a steganography tool designed for encoding and decoding text messages into image files by modifying the least significant bits (LSB) of pixel values in each color channel. Steganography allows hidden communication within images, where encoded messages are concealed in digital image data, making them virtually invisible to the human eye.

## Features

- **Dynamic LSB Encoding**: Automatically adjusts the number of LSBs used for encoding to fit the message into the image without significantly degrading its quality.
- **Message Sanitization**: Removes non-ASCII characters from the input message to ensure compatibility with encoding.
- **Multi-File Message Combination**: Combines messages from multiple text files into a single continuous message for encoding.
- **Noise Generation**: Simulates noise by generating random binary data when no actual message is provided.
- **CLI Support**: Easily interact with the tool via a command-line interface with customizable parameters.

## Key Algorithms

1. **Dynamic LSB Encoding**: Gradually increases the number of LSBs used for encoding until the entire message fits within the image's pixel data.
2. **Binary Message Storage**: Converts the text message to binary, appends a unique end marker, and stores it by modifying the LSB of each pixel.
3. **Decoding Algorithm**: Reads the LSBs of image pixels to reconstruct the binary message and stops at the unique end marker, converting it back to text.

## Command-Line Interface (CLI)

The tool supports CLI interaction, allowing users to specify input files, source images, and output files for both encoding and decoding. Key parameters include:

- `--file_paths`: List of text file paths containing the message(s) to encode. Multiple files can be combined into a single message.
- `--source_image`: Path to the input image where the message will be encoded.
- `--output_text`: Path to save the decoded message extracted from the image.
- `--lorem`: Instructs the program to generate random noise instead of encoding a real message. Unlocks additional options:
- `--given_lsb`: Specifies the number of LSBs used for encoding data.
- `--percent`: Determines the percentage of the image's available space used for encoding.

## Examples

### Encoding a Text Message
```bash
python steganography.py --file_paths text1.txt text2.txt --source_image example.jpg --output_text result.txt
```
This command encodes the message from `text1.txt` and `text2.txt` into the image `example.jpg` and saves the decoded message to `result.txt`.

### Encoding Random Noise
```bash
python steganography.py --source_image med_img.jpg --lorem --given_lsb 6 --percent 50
```
This command encodes random noise into `med_img.jpg` using 6 LSBs per pixel channel, leaving 50% of the image untouched for easier visual detection of encoding.

## Key Functions
- `message_to_binary`: Converts a text message into its binary representation.
- `binary_to_string`: Converts binary data back into readable text.
- `encode_image`: Encodes a binary message into an image by modifying pixel LSBs.
- `decode_image`: Extracts a hidden message from an image's pixel LSBs.
- `sanitize_message`: Cleans the message by removing non-ASCII characters.
- `combine_messages`: Combines messages from multiple text files for encoding.

## Requirements
- Python 3.x
- Pillow (Python Imaging Library)

## Installation
```bash
git clone https://github.com/yourusername/steganography-tool.git
cd steganography-tool
pip install -r requirements.txt
```
