from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from fusionbrain_sdk_python import AsyncFBClient, PipelineType
import base64
import uuid
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

API_KEY = os.getenv("FB_API_KEY")
SECRET_KEY = os.getenv("FB_SECRET_KEY")

# --- Создаем папку для изображений заранее ---
os.makedirs("images", exist_ok=True)

app = FastAPI()

# Подключаем статическую папку для изображений
app.mount("/images", StaticFiles(directory="images"), name="images")

# Инициализируем клиент SDK один раз при старте сервера
async_client = AsyncFBClient()

class PromptRequest(BaseModel):
    text: str

@app.post("/generate")
async def generate_image(req: PromptRequest):
    try:
        # 1. Получаем пайплайн для text-to-image
        pipelines = await async_client.get_pipelines_by_type(PipelineType.TEXT2IMAGE)
        if not pipelines:
            raise HTTPException(status_code=500, detail="Нет доступных пайплайнов")
        text2image_pipeline = pipelines[0]

        # 2. Запускаем генерацию
        run_result = await async_client.run_pipeline(
            pipeline_id=text2image_pipeline.id,
            prompt=req.text
        )

        # 3. Ждём завершения задачи
        final_status = await async_client.wait_for_completion(
            request_id=run_result.uuid,
            initial_delay=run_result.status_time
        )

        if final_status.status != "DONE":
            raise HTTPException(status_code=500, detail=f"Ошибка генерации: {final_status.status}")

        # 4. Получаем изображения (Base64)
        image_base64 = final_status.result.files[0]
        image_data = base64.b64decode(image_base64)

        # 5. Сохраняем файл
        filename = f"images/{uuid.uuid4().hex}.png"
        with open(filename, "wb") as f:
            f.write(image_data)

        return {"url": f"/images/{os.path.basename(filename)}", "prompt": req.text}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
