from flask import Flask, render_template, request, redirect
import requests

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/items')
def items():
    #dohvati unose sa FastAPI backend-a
    response = requests.get('http://127.0.0.1:8000/items/')
    items = response.json()
    return render_template('items.html', items=items)

@app.route('/add_item',methods=['POST','GET'])
def add_item():
    if request.method=='POST':
        #izvuci podatke o unosu iz forme
        name = request.form['name']
        description = request.form['description']

        #pošalji POST zahtjev za dodati unos
        payload = {'name':name, 'description': description}
        response = requests.post('http://127.0.0.1:8000/items/', json=payload)
        if response.status_code==200:
            return redirect('/items')
        else:
            return render_template('error.html', message="Failed to add item")

    return render_template('add_item.html')


if __name__ == '__main__':
    app.run(debug=True)
