class JsonFormatter:

    @classmethod
    def outgoing_request(cls, json_data: dict) -> dict:
        return json_data

    @classmethod
    def incoming_response(cls, json_data: dict) -> dict:
        return json_data
