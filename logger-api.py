from flask import Flask, request
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)

from logger import BoulderbarCapacityLogger

class Log(Resource):
    def get(self):
        df = BoulderbarCapacityLogger.data_frame()
        
        if df is None:
            return {}
        else:
            return df.to_json()

api.add_resource(Log, '/boulderbar-capacity-log')

if __name__ == '__main__':
    app.run(debug=True)