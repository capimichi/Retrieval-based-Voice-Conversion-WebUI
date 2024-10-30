from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import os
import sys
import base64
from dotenv import load_dotenv
from scipy.io import wavfile
from configs.config import Config
from infer.modules.vc.modules import VC
import tempfile
from fastapi.responses import FileResponse
import uvicorn

app = FastAPI()


class ConversionParams(BaseModel):
    f0up_key: int = 0
    input_file_base64: str
    index_path: Optional[str] = None
    f0method: str = "harvest"
    model_name: str
    index_rate: float = 0.66
    device: Optional[str] = None
    is_half: Optional[bool] = None
    filter_radius: int = 3
    resample_sr: int = 0
    rms_mix_rate: float = 1
    protect: float = 0.33


@app.post("/convert")
def convert_audio(params: ConversionParams):
    try:
        load_dotenv()

        # Decode the base64 input file and save it temporarily
        input_wav_data = base64.b64decode(params.input_file_base64)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_input_file:
            temp_input_file.write(input_wav_data)
            temp_input_path = temp_input_file.name

        config = Config()
        config.device = params.device if params.device else config.device
        config.is_half = params.is_half if params.is_half else config.is_half
        vc = VC(config)
        vc.get_vc(params.model_name)
        _, wav_opt = vc.vc_single(
            0,
            temp_input_path,
            params.f0up_key,
            None,
            params.f0method,
            params.index_path,
            None,
            params.index_rate,
            params.filter_radius,
            params.resample_sr,
            params.rms_mix_rate,
            params.protect,
        )

        # Save the output file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_output_file:
            wavfile.write(temp_output_file.name, wav_opt[0], wav_opt[1])
            temp_output_path = temp_output_file.name

        return FileResponse(temp_output_path, media_type="audio/wav", filename="output.wav")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Run the FastAPI app
if __name__ == "__main__":
    host = os.getenv("RVC_WEBUI_HOST", "0.0.0.0")
    port = int(os.getenv("RVC_WEBUI_PORT", 8000))
    uvicorn.run(app, host=host, port=port)
