import os
import shutil
import zipfile
import Augmentor
from flask import Flask, render_template, request, send_file

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/augment', methods=['POST'])
def augment():
    # Get the uploaded folder
    uploaded_folder = request.files['folder']

    # Save the folder to disk
    folder_path = os.path.join(app.root_path, 'uploads')
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
    os.makedirs(folder_path)
    uploaded_folder.save(folder_path)

    # Create a new folder for the augmented images
    output_path = os.path.join(app.root_path, 'static', 'output')
    if os.path.exists(output_path):
        shutil.rmtree(output_path)
    os.makedirs(output_path)

    # Augment the images
    p = Augmentor.Pipeline(folder_path)
    p.ground_truth(folder_path)
    p.rotate(probability=1, max_left_rotation=5, max_right_rotation=5)
    p.flip_left_right(probability=0.5)
    p.zoom_random(probability=0.5, percentage_area=0.8)
    p.flip_top_bottom(probability=0.5)
    p.sample(50)

    # Zip the augmented images
    zip_path = os.path.join(app.root_path, 'static', 'output.zip')
    with zipfile.ZipFile(zip_path, 'w') as zip_file:
        for file_name in os.listdir(output_path):
            file_path = os.path.join(output_path, file_name)
            zip_file.write(file_path, file_name)

    # Remove the output folder
    shutil.rmtree(output_path)

    # Download the zip file
    return send_file(zip_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
