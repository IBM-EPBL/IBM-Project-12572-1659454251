import ibm_db
from flask import Flask, flash, redirect, render_template, request, url_for
from flask_mail import Mail, Message
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from sendmailer import *
import pandas as pd

app = Flask(__name__)


# app.secret_key=''
# configure the mail settings   

SENDGRID_API_KEY = "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"
app.config['SECRET_KEY'] = 'top-secret!'
app.config['MAIL_SERVER'] = 'smtp.sendgrid.net'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'apikey'
# app.config['MAIL_PASSWORD'] = os.environ.get('SENDGRID_API_KEY')
# app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('vasanthias52@gmail.com')
mail = Mail(app)

conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=b0aebb68-94fa-46ec-a1fc-1c999edb6187.c3n41cmd0nqnrk39u98g.databases.appdomain.cloud;PORT=31249;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=pfd03782;PWD=dnhtwrcfkZlhkhAO",'','')  # type: ignore
print(conn)
print("connection successful...")

@app.route('/sendgrid')
def sendgrid():
    return render_template('sendgrid.html')



@app.route('/loginpage', methods=['POST','GET'])
def loginpage():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if not email or not password:
            return render_template('login.html',error='Please fill all fields')
        
        query = "SELECT * FROM USERS WHERE EMAIL=? AND PASSWORD=?"
        stmt = ibm_db.prepare(conn, query) # type:ignore
        ibm_db.bind_param(stmt,1,email) # type:ignore
        ibm_db.bind_param(stmt,2,password) # type:ignore
        ibm_db.execute(stmt) # type:ignore
        isUser = ibm_db.fetch_assoc(stmt) # type:ignore
        print(isUser,password)

        if not isUser:
            return render_template('login.html',error='Invalid Credentials')
      
        return redirect(url_for('home'))

    return render_template('login.html',name='Home')
   

@app.route('/signup')
def registration():
    return render_template('signup.html')


@app.route('/signup', methods=['POST','GET'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']
        
        sql ="INSERT INTO USERS VALUES (?,?,?,?)"
        stmt = ibm_db.prepare(conn,sql)  # type: ignore
        ibm_db.bind_param(stmt, 1, name)  # type: ignore
        ibm_db.bind_param(stmt, 2, email)  # type: ignore
        ibm_db.bind_param(stmt, 3, phone)  # type: ignore
        ibm_db.bind_param(stmt, 4, password)  # type: ignore
        ibm_db.execute(stmt)  # type: ignore
        sendemail(email,'')
        return redirect(url_for('home'))
    
    return render_template('signup.html')


@app.route('/')
@app.route('/login')
def login():
    return render_template('login.html')





@app.route('/stats')
def stats():
    return render_template('stats.html')

@app.route('/contacts')
def requester():
    return render_template('contacts.html')



@app.route('/tech', methods=['POST'])
def by_tech():
    jobs = pd.read_csv('jobs.csv')
    input = request.get_json()
    tech_name = input['techName']
    page = int(input['page']) if input['page'] else 0
    sorting = input['sorting'] if input['sorting'] else 0

    filtered_jobs = jobs.loc[jobs['Tech Stack'].str.contains(tech_name, na=False)]

    if sorting:
        filtered_jobs = filtered_jobs.sort_values(by=[sorting])

    return filtered_jobs[page*10:page*10+10].drop(['Unnamed: 0'], axis=1).to_json(orient='records')


@app.route('/location', methods=['POST'])
def by_location():
    jobs = pd.read_csv('jobs.csv')
    input = request.get_json()
    location = input['location']
    page = int(input['page']) if input['page'] else 0
    sorting = input['sorting'] if input['sorting'] else 0

    filtered_jobs = jobs.loc[jobs['Location'] == location]
    if sorting:
        filtered_jobs = filtered_jobs.sort_values(by=[sorting])

    return filtered_jobs[page*10:page*10+10].drop(['Unnamed: 0'], axis=1).to_json(orient='records')

@app.route('/forgot')
def reques():
    return render_template('forgotten-password.html')

@app.route('/forgot',methods=['POST','GET'])
def forgot():
    if request.method == 'POST':
        email = request.form['email']
        query = "SELECT * FROM USERS WHERE EMAIL=?"
        stmt = ibm_db.prepare(conn, query) # type:ignore
        ibm_db.bind_param(stmt,1,email)
        ibm_db.execute(stmt) # type:ignore
        isUser = ibm_db.fetch_assoc(stmt) # type:ignore
        # print(isUser,password)
        print(isUser)
        print(stmt)
        sendemail(email,'We have recieved your email! from your email address to reset the password, we will send you a link to reset your password')
        return render_template('login.html')
    return render_template('forgotten-password.html')

@app.route('/features')
def features():
    return render_template('features.html')


@app.route('/home')
def home():
    return render_template('index.html')

# @app.route('/')
# def home():
#     return render_template('index.html')

@app.route('/contacts' ,methods=['POST'])
def contacts():
    email = request.form['email']
    sendemail(email,'We have recieved your email!')
    return render_template('contacts.html')


@app.route('/logout')
def logout():
    
    session.pop('email', None) # type:ignore
    return redirect(url_for('login'))

    
if __name__=='__main__':
        app.run(debug=True)

       