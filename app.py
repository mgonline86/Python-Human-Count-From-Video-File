from Final import main
import os
from flask import Flask, flash, request, redirect, url_for, render_template, abort, Response, make_response, stream_with_context
from werkzeug.utils import secure_filename
from database.models import db_drop_and_create_all, setup_db, User, Video, db
from fpdf import FPDF
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

UPLOAD_FOLDER = os.path.abspath(os.path.dirname(__file__))
ALLOWED_EXTENSIONS = {'mov', 'mp4'}

app = Flask(__name__)
setup_db(app)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#----------------------------------------------------------------------------#
# Create PDF
#----------------------------------------------------------------------------#


class PDF(FPDF):
    def header(self):
        # Logo
        self.image(os.path.join(
            app.config['UPLOAD_FOLDER'], 'static', 'img', 'Logo.jpeg'), 150, 8, 50)
        # Line break
        self.ln(30)
        # Arial bold 15
        self.set_font('Arial', 'B', 26)
        # Title
        self.cell(0, 20, 'Display information about this video', 1, 0, 'C')
        # Line break
        self.ln(20)

    # Page footer
    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # Arial italic 8
        self.set_font('Arial', 'I', 8)
        # Page number
        self.cell(0, 10, 'Page ' + str(self.page_no()) +
                  '/{nb}', 0, 0, 'C')


def create_pdf(video):
    # Instantiation of inherited class
    pdf = PDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_font('Times', '', 20)
    # Line break
    pdf.ln(10)
    pdf.cell(0, 20, 'Video name is : '+str(video.name), 0, 1)
    pdf.cell(0, 20, 'Video extension is : '+str(video.extension), 0, 1)
    pdf.cell(0, 20, 'Video size is : '+str(video.size)+' bytes', 0, 1)
    pdf.cell(0, 20, 'number of human in this video : '+str(video.humans), 0, 1)
    pdf.cell(0, 20, 'number of human penetrated social distance : ' +
             str(video.pent), 0, 1)
    pdf.cell(0, 20, 'number of human that not penetrated social distance : ' +
             str(video.not_pent), 0, 1)
    pdf.cell(0, 20, 'persentage of human execeeded the safty distance : ' +
             str(video.percent)+'%', 0, 1)
    return pdf.output(dest='S').encode('latin-1', 'ignore')

# Uncomment the following line if you want to reset your database and then comment it again
# db_drop_and_create_all()


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Index route
@ app.route('/')
def index():
    return render_template('pages/LoginForm1.html')


# Homepage route
@ app.route('/homepage')
def homepage():
    file_name = request.args.get('file_name', type=str)
    file_path = request.args.get('file_path', type=str)
    file_extension = request.args.get('file_extension', type=str)
    file_size = request.args.get('file_size', type=int)
    user = User.query.filter_by(logged=True).first()
    reports = Video.query.filter_by(user_id=user.id).all()
    total_reports = len(reports)
    return render_template('pages/Homepage.html', user=user, file_name=file_name, file_path=file_path, file_extension=file_extension, file_size=file_size, total_reports=total_reports)


# ExportReport route
@ app.route('/export_report')
def export_report():
    last_video_extension = Video.query.order_by(
        db.desc(Video.upload_date)).first().extension
    if os.path.exists(os.path.join(UPLOAD_FOLDER, 'temp.'+last_video_extension)):
        os.remove(os.path.join(UPLOAD_FOLDER, 'temp.'+last_video_extension))
    user = User.query.filter_by(logged=True).first()
    from_date = request.args.get('from_date', type=str)
    to_date = request.args.get('to_date', type=str)
    reports = Video.query.filter_by(user_id=user.id).all()
    total_reports = len(reports)
    if from_date and to_date:
        format_from_date = datetime.strptime(from_date, '%Y-%m-%dT%H:%M')
        format_to_date = datetime.strptime(to_date, '%Y-%m-%dT%H:%M')
        reports = Video.query.filter(Video.upload_date > format_from_date,
                                     Video.upload_date < format_to_date, Video.user_id == user.id).all()
    else:
        reports = Video.query.filter_by(user_id=user.id).all()
    return render_template('pages/exportReport.html', reports=reports, user=user, total_reports=total_reports)


# LoginForm1 route
@ app.route('/login_form_1')
def login_form_1():
    return render_template('pages/LoginForm1.html')


@ app.route('/login_form_1', methods=['POST'])
def login():
    # Logging out all users
    users = User.query.filter_by(logged=True).all()
    if users:
        for user in users:
            user.logged = False
            user.update()

    # Logging In user
    email = request.form.get('email')
    password = request.form.get('password')

    user = User.query.filter_by(email=email).first()

    if user and check_password_hash(user.password, password):
        user.logged = True
        user.update()
        return redirect(url_for('homepage'))

    flash('Wrong E-mail or Password!')
    return redirect(request.url)


# LoginForm2 route
@ app.route('/login_form_2')
def login_form_2():
    return render_template('pages/LoginForm2.html')


# SignUp route
@ app.route('/sign_up')
def sign_up():
    return render_template('pages/SIGNUP.html')

# Register route


@ app.route('/register', methods=['POST'])
def register():
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    email = request.form.get('email')
    phone_number = request.form.get('phone_number')
    password = request.form.get('password')

    user = User(first_name=first_name, last_name=last_name, email=email,
                phone_number=phone_number, password=generate_password_hash(password))
    user.insert()
    return redirect(url_for('login_form_1'))

# testmenu route


@ app.route('/testmenu')
def testmenu():
    return render_template('pages/testmenu.html')


# upload route
@ app.route('/upload')
def upload():
    user = User.query.filter_by(logged=True).first()
    reports = Video.query.filter_by(user_id=user.id).all()
    total_reports = len(reports)
    return render_template('pages/upload.html', user=user, total_reports=total_reports)


# Post Upload Video route
@ app.route('/upload', methods=['POST'])
def upload_file():
    # check if the post request has the file part
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    # if user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        file_name = file.filename.rsplit('.', 1)[0]
        file_path = os.path.join(
            app.config['UPLOAD_FOLDER'], 'temp.'+file_extension)
        file.save(file_path)
        file_stats = os.stat(file_path)
        file_size = file_stats.st_size  # in Bytes
        return redirect(url_for('homepage', file_name=file_name, file_path=file_path, file_extension=file_extension, file_size=file_size))
    else:
        flash('Something went wrong!')
        return redirect(request.url)


# video route
@ app.route('/video_feed')
def video_feed():
    file_name = request.args.get('file_name', type=str)
    file_path = request.args.get('file_path', type=str)
    file_extension = request.args.get('file_extension', type=str)
    file_size = request.args.get('file_size', type=int)
    return Response(stream_with_context(main(file_path, file_name, file_extension, file_size)), mimetype='multipart/x-mixed-replace; boundary=frame')


# Report route
@ app.route('/report_download')
def report_download():
    # Choosing Video Report
    id = request.args.get('id', type=int)
    video = Video.query.filter_by(id=id).first()
    # Creating Video Report
    pdf = create_pdf(video)
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename={}.pdf'.format(
        str(video.upload_date))
    return response


@ app.route('/report_delete', methods=['POST'])
def report_delete():
    id = request.args.get('id', type=int)
    video = Video.query.filter_by(id=id).first()
    video.delete()
    return redirect(url_for('export_report'))


if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(host="0.0.0.0")
