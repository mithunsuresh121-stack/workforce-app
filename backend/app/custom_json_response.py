from typing import Any

from starlette.responses import JSONResponse

from app.custom_json_encoder import custom_json_dumps


class CustomJSONResponse(JSONResponse):
    def render(self, content: Any) -> bytes:
        return custom_json_dumps(content).encode("utf-8")
