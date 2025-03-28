from flask import Flask, render_template
app = Flask(__name__)

@app.route("/")
def home():
    return render_template ("home.html")

@app.route("/graficos.html")
def graficos():
    return render_template("graficos.html")

if __name__ == "__main__":
    app.run(debug=True)
