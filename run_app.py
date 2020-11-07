import json

from flask import Flask
from markupsafe import escape

from data_analisys.data_analyser import DataAnalyser

app = Flask(__name__)
data_analyser = DataAnalyser()


@app.route('/user/<username>')
def show_user_profile(username):
    user_info = data_analyser.get_user_info(int(escape(username)))
    return json.dumps(user_info)


if __name__ == '__main__':
    print('running!!!')
    app.run(host="0.0.0.0")