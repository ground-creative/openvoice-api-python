import json
from quart import jsonify, make_response
from datetime import datetime

class Response:
    @staticmethod
    def payload(success, code, msg, data={}):
        dt = datetime.now()
        response = {
            "result": {
                "success": success,
                "message": msg,
                "data": data,
            },
            "code": code,
            "time": int(dt.timestamp() * 1000)  # Convert to milliseconds and round to integer
        }
        return response

    @staticmethod
    def timeout(code, msg, data=None):
        dt = datetime.now()
        response = {
            "result": {
                "success": False,
                "message": msg,
                "data": data,
            },
            "code": code,
            "time": int(dt.timestamp() * 1000)  # Convert to milliseconds and round to integer
        }
        return response

    @staticmethod
    def not_found(msg, data=None):
        dt = datetime.now()
        response = {
            "result": {
                "success": False,
                "message": msg,
                "data": data,
            },
            "code": 404,
            "time": int(dt.timestamp() * 1000)  # Convert to milliseconds and round to integer
        }
        return response

    @staticmethod
    async def output(data, code=None, headers=None):
        response = await make_response(data, code if code is not None else 200)
        if headers:
            response.headers['Content-Type'] = headers
        return response
