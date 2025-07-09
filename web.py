from flask import Flask, render_template, request, send_file, jsonify
from io import BytesIO
import os

app = Flask(__name__)

# Function to apply the fourbit conversion to each byte
def fourbit(x):
    return x & 0xf0

# Route to display the index.html page
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle file conversion and download
@app.route('/convert', methods=['POST'])
def convert_file():
    # Check if the 'raw_file' exists in the request
    if 'raw_file' not in request.files:
        return jsonify(message="No file part")

    raw_file = request.files['raw_file']

    # Check if the file name is empty
    if raw_file.filename == '':
        return jsonify(message="No selected file")

    # Check if the file ends with ".raw"
    if not raw_file.filename.lower().endswith('.raw'):
        return jsonify(message="Invalid file format. Please upload a .raw file.")

    # Read the content of the uploaded raw file
    raw_content = raw_file.read()

    # Check if the file size is within the limit (512KB)
    if len(raw_content) > 512 * 1024:
        return jsonify(message="File size exceeds the limit (512KB).")

    # Open amenizer.gb and read its content
    with open("amenizer.gb", "rb") as g:
        gb_content = g.read(16384)

    # Apply the fourbit conversion to each byte in the raw file
    y = [fourbit(i) for i in raw_content]

    # Group the converted bytes into pairs
    y = zip(y[0::2], y[1::2])

    # Create a BytesIO object to store the converted file content
    output_file = BytesIO()

    # Write the content of amenizer.gb to the output file
    output_file.write(gb_content)

    # Write the converted data to the output file
    for i in y:
        output_file.write(bytes([i[0] | i[1] >> 4]))

    # Set the file pointer to the beginning of the BytesIO object
    output_file.seek(0)

    # Get the name of the raw file without the extension
    raw_filename = os.path.splitext(raw_file.filename)[0]

    # Send the converted file as a response with a specified download name
    return send_file(output_file, as_attachment=True, download_name=f"{raw_filename}.gb", mimetype='application/octet-stream')

if __name__ == '__main__':
    app.run()
