from flask import Flask,render_template,request

app = Flask(__name__)
# app.static_folder = 'static'

@app.route('/',methods =['GET','POST'])
def index():
    if request.method == 'GET' :
        return render_template('home.html')
    elif request.method == 'POST':
        return render_template('resulturl.html')
    else:
        return render_template('error404.html')

if __name__ == '__main__':
    app.run(port=8080,debug=True)