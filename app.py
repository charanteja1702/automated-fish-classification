from flask import Flask, url_for, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
import tensorflow as tf
from tensorflow import keras

from keras.models import load_model
from keras.preprocessing import image
import numpy as np

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

    def __init__(self, username, password):
        self.username = username
        self.password = password


@app.route('/', methods=['GET'])
def index():
    if session.get('logged_in'):
        return render_template('index.html')
    else:
        return render_template('index.html', message="Hello!")


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            db.session.add(User(username=request.form['username'], password=request.form['password']))
            db.session.commit()
            return redirect(url_for('login'))
        except:
            return render_template('index.html', message="User Already Exists")
    else:
        return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        u = request.form['username']
        p = request.form['password']
        data = User.query.filter_by(username=u, password=p).first()
        if data is not None:
            session['logged_in'] = True
            return render_template("index1.html")
        return render_template('index.html', message="Incorrect Details")

dic = {0 : 'Black Sea Sprat', 1 : 'Gilt-Head Bream', 2 : 'Hourse Mackerel', 3 : 'Red Mullet', 4 : 'Red Sea Bream', 5 : 'Sea Bass', 6 : 'Shrimp', 7 : 'Striped Red Mullet', 8 : 'Trout'}

model = load_model('trainedModel.h5')

model.make_predict_function()

def predict_label(img_path):
    # image = tf.keras.preprocessing.image.load_img(img_path, target_size=(256,256))
    # input_arr = tf.keras.preprocessing.image.img_to_array(image)
    # input_arr = np.ndarray([input_arr][np.indices.astype(int)]) # Convert single image to a batch.
    # p = model.predict(input_arr)
    # return dic[p[0]]
    
	i = keras.utils.load_img(img_path)
	i = keras.utils.img_to_array(i)
	i =np.expand_dims(i, axis=0)
	# i = i.reshape(1, 256,256,3)
	p = model.predict(i)
	
	return dic[np.argmax(p)]


# routes
@app.route("/aq", methods=['GET', 'POST'])
def main():
	return render_template("index1.html")

p=''
@app.route("/submit", methods = ['GET', 'POST'])
def get_output():
	if request.method == 'POST':
		img = request.files['my_image']

		img_path = "static/" + img.filename	
		img.save(img_path)

		p = predict_label(img_path)

	return render_template("in.html", prediction = p, img_path = img_path,)



@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session['logged_in'] = False
    return redirect(url_for('index'))

@app.route("/up", methods=['GET', 'POST'])
def up():
	return render_template("index1.html")

if(__name__ == '__main__'):
    app.secret_key = "ThisIsNotASecret:p"
    db.create_all()
    app.run(debug = False,host='0.0.0.0')
