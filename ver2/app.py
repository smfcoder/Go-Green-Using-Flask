import os
from flask import Flask , redirect , render_template, request,url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager , UserMixin , login_required ,login_user, logout_user,current_user
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'static/img/'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///db.db'
app.config['SECRET_KEY']='619619'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=True
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin,db.Model):
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    username = db.Column(db.String(200), unique=True, nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    password = db.Column(db.String(200))




@login_manager.user_loader
def get(id):
    return User.query.get(id)

@app.route('/home',methods=['GET'])
@login_required
def get_home():
    return render_template('home.html')

@app.route('/',methods=['GET'])
def get_login():
    return render_template('login.html')


@app.route('/signup',methods=['GET'])
def get_signup():
    return render_template('signup.html')

@app.route('/login',methods=['POST'])
def login_post():
    email = request.form['email']
    password = request.form['password']
    user = User.query.filter_by(email=email,password=password).first()
    if user:
        login_user(user)
        return redirect('/home')
    else:
        error ='Invalid'
        return render_template('login.html',error=error)



@app.route('/signup',methods=['POST'])
def signup_post():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    user = User(username=username,email=email,password=password)
    db.session.add(user)
    db.session.commit()
    user = User.query.filter_by(email=email).first()
    if user:
        login_user(user)
        return redirect('/home')
    else:
        error = 'Invalid'
        return render_template('signup.html', error=error)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


class Imagee(db.Model):
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    username = db.Column(db.String(200),nullable=False)
    email = db.Column(db.String(200),nullable=False)
    path = db.Column(db.String(200))

@app.route('/uploader', methods=['GET', 'POST'])
def upload_file():
    success = 'failed'
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            path=os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(path)

            username=current_user.username
            email=current_user.email
            img = Imagee(username=username, email=email, path=path)
            db.session.add(img)
            db.session.commit()


            from PIL import Image, ImageFilter, ImageEnhance
            import cv2
            import numpy as np

            image = Image.open(path)
            image.show()
            width, height = image.size
            if (width==1280 and height==720):
                a = 0
                green = 0
                for x in range(width):
                    for y in range(height):
                        r, g, b = image.getpixel((x, y))
                        if (r >= 0 and b >= 0):
                            if (r < g and b < g):
                                zz = g - r
                                xx = g - b
                                if (zz > 10 and xx > 10):
                                    green = green + 1
                                    image.putpixel((x, y), (255, 255, 255))
                                else:
                                    image.putpixel((x, y), (0, 0, 0))
                            else:
                                image.putpixel((x, y), (0, 0, 0))
                        else:
                            image.putpixel((x, y), (0, 0, 0))

                        a = a + 1
                image.show()
                image.save("mask.jpg")
                print("Total Pixel %d" % a)
                print("Total Green Pixel  %d" % green)
                print(width)
                print(height)

                img = Image.open("mask.jpg")
                img.filter(ImageFilter.FIND_EDGES).save("edge.jpg")

                im = Image.open("edge.jpg")
                im.show()

                img = cv2.pyrDown(cv2.imread('mask.jpg', cv2.IMREAD_UNCHANGED))

                ret, threshed_img = cv2.threshold(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), 127, 255, cv2.THRESH_BINARY)

                contours, hier = cv2.findContours(threshed_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                coo = 0
                for c in contours:
                    x, y, w, h = cv2.boundingRect(c)
                    aa = (w) * (h)
                    #print(aa)
                    if aa > 2:
                        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
                        coo = coo + 1
                    else:
                        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 0), -1)

                print("Total Counter of box :-  ")
                print(len(contours))

                print(" Approx No of tree : ")
                print(coo)

                cv2.imwrite("contours.jpg", img)
                imc = Image.open("contours.jpg")
                imc.show()

            else:
                print("Enter image of 1280 X 720 pixel")

            success = 'Uploaded'
            return render_template('home.html', success=success)
    return render_template('home.html', success=success)

@app.route('/logout',methods=['GET'])
def logout():
    logout_user()
    return redirect('/')


if __name__=='__main__':
    app.run(debug=True)