from flask import Flask, render_template, request, send_file, redirect, url_for
import os
from werkzeug.utils import secure_filename
from c5i_final import process
from prediction import prediction

app = Flask(__name__, template_folder="templates", static_folder="static")

UPLOAD_FOLDER = os.getcwd()  # Set upload folder to the current directory
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def home():
    # Retrieve the filename from query parameters if available
    filename = request.args.get('filename')
    return render_template('index.html', filename=filename)

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['excelFile']
    if file.filename == '':
        return "No selected file"

    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    
    f = process(file_path)
    df = prediction(f)
    
    # Save the updated DataFrame
    output_filename = "predicted_data.xlsx"
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
    df.to_excel(output_path, index=False)
    
    # Redirect to the home page with the filename as a query parameter
    return redirect(url_for('home', filename=output_filename))

@app.route('/download/<filename>')
def download_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return "File not found", 404

if __name__ == '__main__':
    app.run(debug=True)
