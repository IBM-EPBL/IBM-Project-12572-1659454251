from flask import Flask,render_template
app = Flask(__name__)
@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
def index():
 return render_template('index.html')
if __name__ == '__main__':
    app.run(port=5000,debug=True)