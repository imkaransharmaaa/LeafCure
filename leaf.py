from flask import Flask, render_template, request, redirect, url_for
import numpy as np
import os
from tensorflow.keras.preprocessing.image import load_img
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.models import load_model
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User
from forms import RegistrationForm, LoginForm
from config import Config

filepath = 'C:/Users/ks228/OneDrive/Desktop/leaf_disease_detection/model.h5'
model = load_model(filepath)
print(model)

print("Model Loaded Successfully")

def pred_tomato_dieas(tomato_plant):
  test_image = load_img(tomato_plant, target_size = (128, 128)) # load image 
  print("@@ Got Image for prediction")
  
  test_image = img_to_array(test_image)/255 # convert image to np array and normalize
  test_image = np.expand_dims(test_image, axis = 0) # change dimention 3D to 4D
  
  result = model.predict(test_image) # predict diseased palnt or not
  print('@@ Raw result = ', result)
  
  pred = np.argmax(result, axis=1)
  print(pred)
  if pred==0:
      return "Tomato - Bacteria Spot Disease", 'Tomato-Bacteria Spot.html'
       
  elif pred==1:
      return "Tomato - Early Blight Disease", 'Tomato-Early_Blight.html'
        
  elif pred==2:
      return "Tomato - Healthy and Fresh", 'Tomato-Healthy.html'
        
  elif pred==3:
      return "Tomato - Late Blight Disease", 'Tomato - Late_blight.html'
       
  elif pred==4:
      return "Tomato - Leaf Mold Disease", 'Tomato - Leaf_Mold.html'
        
  elif pred==5:
      return "Tomato - Septoria Leaf Spot Disease", 'Tomato - Septoria_leaf_spot.html'
        
  elif pred==6:
      return "Tomato - Target Spot Disease", 'Tomato - Target_Spot.html'
        
  elif pred==7:
      return "Tomato - Tomoato Yellow Leaf Curl Virus Disease", 'Tomato - Tomato_Yellow_Leaf_Curl_Virus.html'
  elif pred==8:
      return "Tomato - Tomato Mosaic Virus Disease", 'Tomato - Tomato_mosaic_virus.html'
        
  elif pred==9:
      return "Tomato - Two Spotted Spider Mite Disease", 'Tomato - Two-spotted_spider_mite.html'

    

# Create flask instance
app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# render index.html page
@app.route("/", methods=['GET', 'POST'])
def home():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        print("------------002-------------")
    form = RegistrationForm()
    print("------------003-------------")
    if form.validate_on_submit():
        print("------------004-------------")
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        print("------------005-------------")
        user = User(name=form.name.data, username=form.username.data, email=form.email.data, password=hashed_password, city=form.city.data, state=form.state.data)
        print("------------006-------------")
        db.session.add(user)
        print("------------007-------------")
        db.session.commit()
        print("------------008-------------")
        print("------------009-------------")
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = LoginForm()
    print("------------0011-------------")
    if form.validate_on_submit():
        print("------------0012-------------")
        user = User.query.filter_by(email=form.email.data).first()
        print("------------0013-------------")
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            print("------------0014-------------")
            login_user(user)
            print("------------0015-------------")
            return redirect(url_for('dashboard'))
            print("------------0016-------------")
        else:
            print("------------Password is incorrect !!!-------------")
            
    return render_template('login.html', form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('index.html', username=current_user.username)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

 
# get input image from client then predict class and render respective .html page for solution
@app.route("/predict", methods = ['GET','POST'])
def predict():
     if request.method == 'POST':
        file = request.files['image'] # fet input
        filename = file.filename        
        print("@@ Input posted = ", filename)
        
        file_path = os.path.join('C:/Users/ks228/OneDrive/Desktop/leaf_disease_detection/static/upload/', filename)
        file.save(file_path)

        print("@@ Predicting class......")
        pred, output_page = pred_tomato_dieas(tomato_plant=file_path)
              
        return render_template(output_page, pred_output = pred, user_image = file_path)
    
# For local system & cloud
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(threaded=False,port=8080) 
    
    
