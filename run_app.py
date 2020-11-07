import json

from flask import Flask
from markupsafe import escape

from data_analisys.data_analyser import DataAnalyser

app = Flask(__name__)
data_analyser = DataAnalyser()


@app.route('/user/<user_id>')
def show_user_profile(user_id):
    user_info = data_analyser.get_user_info(int(escape(user_id)))
    return json.dumps(user_info)


@app.route('/user/insides/<user_id>/<date>/<type>')
def show_user_insides(user_id, date, type):
    # date: yyyy-mm-dd
    user_insides = data_analyser.get_insides(int(escape(user_id)), escape(date), escape(type))
    return json.dumps(user_insides)


if __name__ == '__main__':
    app.run(host="0.0.0.0")