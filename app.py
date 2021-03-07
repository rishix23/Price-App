from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import json
import ebayScraper as es
# from rq import Queue
# from worker import conn

# from redis import Redis
# from rq.job import Job

# imports are special for redis conenctions
# import redis
# from rq import Worker, Queue, Connection
# redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
# conn = redis.from_url(redis_url)

app = Flask(__name__)
app.secret_key = "price"

ENV = 'prod'
if ENV == 'dev':
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:superuser@localhost/price-dev'
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://nwjtcklkcpxhjs:6c7a56e4c538d1b6ba18434f20bf654f826acd3ff550fc2f19aacf8b0b1a4a8e@ec2-54-155-35-88.eu-west-1.compute.amazonaws.com:5432/d8m2u4dgujc43c'
    app.debug = False

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# holds tweet, prediction
class Prices(db.Model):
    __tablename__ = 'Prices'
    id = db.Column(db.Integer, primary_key=True)
    Text = db.Column(db.String(1000))

    def __init__(self, Text):
        self.Text = Text

# loads home page
@app.route("/", methods=["POST", "GET"])
def index():

    return render_template("index.html")


@app.route("/test", methods=["POST"])
def test():

    text = request.form['text']
    print(text)
    data = Prices(text)
    db.session.add(data)
    db.session.commit()

    return ('', 204)

@app.route("/startScrape", methods=["POST"])
def startScrape():



if __name__ == '__main__':
    app.debug = True
    app.run()

