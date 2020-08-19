import os
from flask import Flask , redirect , render_template, request,url_for,session,flash
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


class Imagee(db.Model):
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    username = db.Column(db.String(200),nullable=False)
    email = db.Column(db.String(200),nullable=False)
    path = db.Column(db.String(200),nullable=False)
    place = db.Column(db.String(200),nullable=False)
    latitude = db.Column(db.String(200), nullable=False)
    longitude = db.Column(db.String(200), nullable=False)
    population = db.Column(db.String(200), nullable=False)
    bikes = db.Column(db.String(200), nullable=False)
    car = db.Column(db.String(200), nullable=False)
    bus = db.Column(db.String(200), nullable=False)
    mask = db.Column(db.String(200), nullable=False)
    counter = db.Column(db.String(200), nullable=False)
    carbon = db.Column(db.String(200), nullable=False)
    oxygen = db.Column(db.String(200), nullable=False)
    trees = db.Column(db.String(200), nullable=False)
    aqi = db.Column(db.String(200), nullable=False)
    greenery = db.Column(db.String(200), nullable=False)
    plantation = db.Column(db.String(200), nullable=False)
    planted = db.Column(db.String(200), nullable=False)


@login_manager.user_loader
def get(id):
    return User.query.get(id)


@app.route('/home',methods=['GET'])
@login_required
def get_home():
    return render_template('index.html')


@app.route('/uploading/<id>',methods=['GET'])
@login_required
def get_uploading(id):
    return render_template('uploadimg.html',id=id)


@app.route('/upload',methods=['GET'])
@login_required
def upload_gets():
    return render_template('upload.html')


@app.route('/upload',methods=['POST'])
@login_required
def upload_post():
    pl = request.form['name']
    latitude = request.form['latitude']
    longitude = request.form['longitude']
    population = request.form['population']
    bikes = request.form['bikes']
    car = request.form['car']
    bus = request.form['bus']
    email = current_user.email
    username = current_user.username
    path = "static/img/"
    carbon=0
    oxygen=0
    trees=0
    aqi="normal"
    greenery="ample"
    plantation="No"
    planted=0
    info = Imagee(username=username, email=email, path=path, place=pl, latitude=latitude,longitude=longitude, population=population, bikes=bikes ,car=car,bus=bus, mask=path, counter=path ,carbon=carbon,oxygen=oxygen,trees=trees,aqi=aqi,greenery=greenery,plantation=plantation,planted=planted)
    db.session.add(info)
    db.session.commit()
    id = info.id
    return redirect(url_for('get_uploading',id=id))


@app.route('/details/<id>',methods=['GET'])
@login_required
def get_details(id):
    information = Imagee.query.filter_by(id=id).first()
    return render_template('details.html',information=information)


@app.route('/myuploads',methods=['GET'])
@login_required
def get_my_uploads():
    email = current_user.email
    table = Imagee.query.filter_by(email=email).all()
    return render_template('myuploads.html',table=table)


@app.route('/delete/<id>',methods=['GET'])
@login_required
def del_id(id):
    delete = Imagee.query.filter_by(id=id).first()
    db.session.delete(delete)
    db.session.commit()
    return redirect('/myuploads')


@app.route('/techstuff/<id>',methods=['GET'])
@login_required
def get_techstuff(id):
    information = Imagee.query.filter_by(id=id).first()
    return render_template('techstuff.html',information=information)


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


@app.route('/uploader', methods=['GET', 'POST'])
@login_required
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            path=os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(path)
            id= request.form['id']
            data_row = Imagee.query.get(id)
            data_row.path='static/img/'+filename
            db.session.commit()
            #Image Processing
            from PIL import Image, ImageFilter, ImageEnhance
            import cv2
            import numpy as np
            image = Image.open(path)
            width, height = image.size
            if (width==1280 and height==720):
                #Mask Image
                for x in range(width):
                    for y in range(height):
                        red, green, blue = image.getpixel((x, y))
                        #RED AND BLUE SHOULD BE NON ZERO
                        if (red >= 0 and blue >= 0):
                            #GREEN MUST BE GREATER THAN RED AND BLUE
                            if (red < green and blue < green):
                                #CALCULATE DIFFERENCE
                                zz = green - red
                                xx = green - blue
                                #IF RED AND BLUE IS LESS THAN 20 THAN DIFFERENCE CAN BE 1 OR MORE
                                if(red <= 20 and blue <= 20 and green <= 20):
                                    image.putpixel((x, y), (255, 255, 255))
                                # IF RED AND BLUE IS GREATER THAN 200 DO'NT CONSIDER THAT PIXEL
                                elif (red > 100 and blue > 100 and green > 100):
                                        image.putpixel((x, y), (0, 0, 0))
                                #DIFFERENCE MUST BE OF 10
                                elif (zz > 10 and xx > 10):
                                    image.putpixel((x, y), (255, 255, 255))
                                #FILL BLACK COLOR
                                else:
                                    image.putpixel((x, y), (0, 0, 0))
                            #GREEN IS NOT LARGER FILL BLACK COLOR
                            else:
                                image.putpixel((x, y), (0, 0, 0))
                        #INVALID
                        else:
                            image.putpixel((x, y), (0, 0, 0))
                #SAVE MASK IMAGE
                image.save("static/img/mask_"+filename)
                img_mask = Imagee.query.get(id)
                img_mask.mask = 'static/img/mask_' + filename
                db.session.commit()
                #DRAW RECTANGLE
                img = cv2.pyrDown(cv2.imread("static/img/mask_"+filename, cv2.IMREAD_UNCHANGED))
                ret, threshed_img = cv2.threshold(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), 127, 255, cv2.THRESH_BINARY)
                contours, hier = cv2.findContours(threshed_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                coo = 0
                for c in contours:
                    x, y, w, h = cv2.boundingRect(c)
                    aa = (w) * (h)
                    if aa > 70:
                        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
                        coo = coo + 1
                    else:
                        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 0), -1)
                #NO OF TREE
                no_tree = Imagee.query.get(id)
                no_tree.trees = coo
                db.session.commit()
                #SAVE COUNTER IMAGE
                cv2.imwrite("static/img/counter_"+filename, img)
                img_counter = Imagee.query.get(id)
                img_counter.counter = 'static/img/counter_' + filename
                db.session.commit()
                #CALCULATING OXYGEN AND CARBONDIOXIDE IN AIR
                #VALUES ASSIGN
                data_values = Imagee.query.get(id)
                no_of_people = data_values.population
                no_of_two_wheel = data_values.bikes
                no_of_four_wheel_car = data_values.car
                no_of_four_wheel_bus = data_values.bus
                tree_count = data_values.trees
                #AMOUNT OF CARBONDIOXIDE
                carbon_people = (454.54 * float(no_of_people))
                carbon_two_wheel = (16.86 * 0.26 *float(no_of_two_wheel))
                carbon_four_wheel_car = (59.09 * 0.26 * float(no_of_four_wheel_car))
                carbon_four_wheel_bus =  (299.39* 0.26 *float(no_of_four_wheel_bus))
                carbon_consume_tree = (float(tree_count) * 30.13)
                total_carbon = carbon_people + carbon_two_wheel + carbon_four_wheel_car + carbon_four_wheel_bus - carbon_consume_tree
                #AMOUNT OF OXYGEN CONSUME
                oxygen_people = (576 * float(no_of_people))
                #OXYGEN PRODUCED
                oxygen_produced = (float(tree_count) * 230.4)
                t_oxygen= oxygen_produced - oxygen_people
                no_of_required_tree=0
                tpm=round(float(no_of_people)*2.5)
                if(int(tree_count) <= tpm):
                    aqi="LOW"
                    nop="YES"
                    no_of_required_tree = tpm-int(tree_count)
                else:
                    aqi = "Ample"
                    nop= "No"
                val = Imagee.query.get(id)
                val.carbon = total_carbon
                val.oxygen = oxygen_produced
                val.aqi=aqi
                val.plantation = nop
                val.planted = no_of_required_tree
                db.session.commit()



                #MESSAGE
                flash("Image Uploaded")
                return redirect(url_for('get_details', id=id))
            else:
                image.close()
                os.remove("static/img/"+filename)
                delt = Imagee.query.get(id)
                db.session.delete(delt)
                db.session.commit()
                flash("Image must be of 1280 X 720 pixel")
                return redirect(url_for('upload_gets'))
        else:
            delt = Imagee.query.get(id)
            db.session.delete(delt)
            db.session.commit()
            flash("IMAGE UPLOADING FAILED")
            return redirect(url_for('upload_gets'))
    else:
        delt = Imagee.query.get(id)
        db.session.delete(delt)
        db.session.commit()
        flash("IMAGE UPLOADING FAILED")
        return redirect(url_for('upload_gets'))

    
@app.route('/logout',methods=['GET'])
def logout():
    logout_user()
    return redirect('/')


if __name__=='__main__':
    app.run(debug=True)