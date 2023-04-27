# Program for creating fog-server
from os import walk
import shutil
from datetime import datetime
import sys

# cheak images in feedback folder
f = []
for (dirpath, dirnames, filenames) in walk('static/feedback'):
	f.extend(filenames)
	break

sys.path.insert(1, '/Users/rugvedchavan/Desktop/Project/Healthcare-Edge-Fog-Cloud/Model_Training')
import client2
from flask import Flask, flash, request, redirect, url_for, render_template, send_from_directory
from werkzeug.utils import secure_filename
import tensorflow as tf
print(tf. __version__)
#from keras.models import model_from_json

from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import load_model

import numpy as np
global score
global globalfilename
globalfilename = "hello"
score = 10

import os

import predction

# create the application object
app = Flask(__name__)

# upLoad Image in website
UPLOAD_FOLDER = 'static/uploads/'
UPLOAD_FOLDER1 = 'static/uploads_report/'
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['UPLOAD_FOLDER1'] = UPLOAD_FOLDER1
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
ALLOWED_EXTENSIONS1 = {'docx','pdf'}

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def allowed_file1(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS1

# use decorators to link the function to a url
@app.route('/')
def welcome():
    return render_template('index.html')  # render a template

@app.route('/pneumonia')
def pneumonia():
	f = []
	for (dirpath, dirnames, filenames) in walk('static/feedback'):
		f.extend(filenames)
		break
	print(f)
	return render_template('pneumonia.html', score =score,f=f)  # render a template

@app.route('/upload_data')
def upload_data():
	f = []
	for (dirpath, dirnames, filenames) in walk('static/users_data'):
		f.extend(filenames)
		break
	print(f)
	return render_template('upload_data.html',f=f)  # render a template

@app.route('/research_group')
def research_group():
    return render_template('research_group.html')  # render a template

@app.route('/collaborations')
def collaborations():
    return render_template('collaborations.html')  # render a template

@app.route('/news')
def news():
    return render_template('news.html')  # render a template

@app.route('/facilites')
def facilites():
    return render_template('facilites.html')  # render a template

@app.route('/contactus')
def contactus():
    return render_template('contactus.html')  # render a template

@app.route('/nfc')
def nfc():
    return render_template('nfc.html')  # render a template


@app.route('/', methods=['POST'])
def upload_image():
	if 'file' not in request.files:
		flash('No file part')
		return redirect(request.url)
	file = request.files['file']
	if file.filename == '':
		flash('No image selected for uploading')
		return redirect(request.url)
	if file and allowed_file(file.filename):
		filename = secure_filename(file.filename)
		upload_image.globalfilename = filename
		file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
		# print('upload_image filename: ' + filename)
		flash('Image successfully uploaded and displayed below')

		print('Person is report =')
		# print('display_image filename: ' + filename)

		# Model prediction
		score = predction.prediction(filename)
		print("Done my Prediction Function")
		upload_image.score = score
		print(score)
		return render_template('pneumonia.html', filename=filename,score =score)
	else:
		flash('Allowed image types are - png, jpg, jpeg, gif')
		return redirect(request.url)

@app.route('/display/<filename>')
def display_image(filename):
		return redirect(url_for('static', filename='uploads/' + filename), code=301)

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
	score = upload_image.score
	filename =   upload_image.globalfilename
	filename1 = 'SC' + str(score) + str(filename)
	img_path = ('static/uploads/'+ filename)
	print(filename1)
	if request.method == 'POST':
		value = request.form['yes_no'] # Check weather the report is correct or wrong feedback
		print("The report was = ",value)
		if value == '1': # if report is correct
			print('flag')
			if score == 0:
				destination = 'static/new-dataset/new-dataset1/class0/'+ filename1
				shutil.copy(img_path, destination)

			elif score == 1:
				destination = 'static/new-dataset/new-dataset1/class1/' + filename1
				shutil.copyfile(img_path, destination)

			elif score == 2:
				destination = 'static/new-dataset/new-dataset1/class2/' + filename1
				shutil.copyfile(img_path, destination)

			elif score == 3:
				destination = 'static/new-dataset/new-dataset1/class3/' + filename1
				shutil.copyfile(img_path, destination)

			# Sending file to cloud SERVER
			DIR = 'static/uploads'
			no_of_files = len([name for name in os.listdir(DIR) if os.path.isfile(os.path.join(DIR, name))])
			print("NUMBER OF FILE =", no_of_files)
			if(no_of_files >=3):
				# make zip file
				dir_name = 'static/new-dataset/new-dataset1'
				output_filename = 'static/uploads_ready'
				shutil.make_archive(output_filename, 'zip', dir_name)
				# send zip file to server
				client2.clent(output_filename + '.zip')
				now = datetime.now()
				dt_string = now.strftime("%d-%m-%Y-%H-%M-%S")
				print(dt_string)
				# create a backup
				original = r'static/uploads_ready.zip'
				target = r'static/Backup/Backup-'+ dt_string + '.zip'
				shutil.copyfile(original, target)
				# delete all files from uploads Directory
				dir = 'static/uploads'
				for f in os.listdir(dir):
					os.remove(os.path.join(dir, f))
				print('done classifing img file folder')
				return redirect(url_for('pneumonia'))
		else: # else report is wrong
			print('pending')
			# Move the 'not sure file' to feedback directory
			destination = 'static/feedback/' + filename1
			shutil.copyfile(img_path, destination)
			return redirect(url_for('pneumonia'))
	return redirect(url_for('pneumonia'))

@app.route('/cheaker/<item>',methods=['GET', 'POST'])
def cheaker(item):
	imgPath = os.path.join('C:/Users/Rugved Chavan/Desktop/Projects/Healthcare-Edge-Fog-Cloud/User Interface/Flask/static/feedback', str(item))
	print("IMgPath = ", imgPath)
	if request.method == 'POST':
		if 'file1' not in request.files:
			flash('No file part')
			return redirect(request.url)
		file = request.files['file1']
		if file.filename == '':
			flash('No image selected for uploading')
			return redirect(request.url)
		if file and allowed_file1(file.filename):
			filename = secure_filename(file.filename)
			upload_image.globalfilename = filename
			file.save(os.path.join(app.config['UPLOAD_FOLDER1'], filename))
			# print('upload_image filename: ' + filename)
			print('Image successfully uploaded and displayed below')

			value = request.form['yes_no2'] # Check weather the report is correct or wrong feedback
			print("The report was = ",value)
			if value == '1':
				imagePath = 'static/feedback/' + item
				destination = 'static/new-dataset/new-dataset1/class' + str(item[3]) + '/'
				shutil.move(imagePath,destination)
				print('Done')
				# filename extraction and classification
			else:
				print('hehehehehehehehehhehehehehe')
				imagePath = 'static/feedback/' + item
				ReportPath = 'static/uploads_report/' + filename
				Admindestination1 = 'static/Admin_cheak/'+item
				Admindestination2 = 'static/Admin_cheak/' + filename
				shutil.move(imagePath,Admindestination1)
				shutil.move(ReportPath,Admindestination2)
			return redirect(url_for('pneumonia'))
		else:
			print('Allowed image types are - png, jpg, jpeg, gif')
			return redirect(request.url)

	return render_template('cheaker.html',item=item,imgPath = imgPath)  # render a template


@app.route('/upload_data1',methods=['GET', 'POST'])
def upload_data1():
	if request.method == 'POST':
		if 'file1' not in request.files:
			flash('No file part')
			return redirect(request.url)
		file = request.files['file1']
		if file.filename == '':
			flash('No image selected for uploading')
			return redirect(request.url)
		if file and allowed_file1(file.filename):
			filename = secure_filename(file.filename)
			upload_image.globalfilename = filename
			file.save(os.path.join(app.config['UPLOAD_FOLDER1'], filename))
			# print('upload_image filename: ' + filename)
			print('Image successfully uploaded and displayed below')

			print('hehehehehehehehehhehehehehe')
			ReportPath = 'static/uploads_report/' + filename
			Admindestination2 = 'static/users_data/' + filename
			shutil.move(ReportPath,Admindestination2)
			return redirect(url_for('upload_data'))
		else:
			print('Allowed image types are - png, jpg, jpeg, gif')
			return redirect(request.url)

	return render_template('upload_data1.html',item=item,imgPath = imgPath)  # render a template

# start the server with the 'run()' method
if __name__ == '__main__':
    app.run(host='0.0.0.0',port=2000,debug=True)
	#app.run(debug=True)