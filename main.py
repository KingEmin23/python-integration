import fastapi
from fastapi import FastAPI, Request, status
import uvicorn
from db_funcs import *

app = FastAPI()


@app.post("/api/v1/push")
async def create(body: dict):
    print(f"Received body: {body}")
    try:
        if body:
            print("Data picker starts...")
            result = data_picker(body)
            print(f"Data pickers result is {result} ")
            await add_to_db(result[0], result[1], result[2], result[3], result[4], result[5])
            return status.HTTP_200_OK
        else:
            print(f"No data is not received!")
            raise fastapi.HTTPException(status_code=400, detail="No data received")

    except Exception as e:
        traceback_str = traceback.format_exc()
        print(f"Error: {e}\n{traceback_str}\n{fastapi.HTTPException}")
        return status.HTTP_500_INTERNAL_SERVER_ERROR


@app.patch("/update")
async def update(request: Request, body: dict):
    pass


if __name__ == "__main__":
    uvicorn.run(app, host=SERV_IP, port=SERV_PORT)



