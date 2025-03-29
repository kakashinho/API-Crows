import os
from flask import Flask, render_template

# 
# Criação da instância do Flask e passando o caminho absoluto para a pasta templates e static
app = Flask(__name__, template_folder=os.path.join('Src', 'templates'), static_folder=os.path.join('Src', 'static'))

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/graficos')
def graficos():
    return render_template('graficos.html')

if __name__ == '__main__':
    app.run(debug=True)