from flask import Flask, render_template, url_for

app = Flask(__name__)

posts = [
    {
        "author": "William Lee",
        "title": "First Post",
        "content": "First post!",
        "date_posted": "Jan 1, 2018"
    },
    {
        "author": "William Lee",
        "title": "Second Post",
        "content": "Second post!",
        "date_posted": "Jan 2, 2018"
    }
]

@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html", posts=posts)

@app.route("/about")
def about():
    return render_template("about.html", title="About")

if __name__ == "__main__":
    app.run()
