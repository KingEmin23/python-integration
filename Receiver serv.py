import fastapi
import uvicorn
from fastapi import FastAPI, status
import json
from Logger import rec_log

app = FastAPI()


@app.post("/finalreceiver")
async def receiver(body: dict, status_code=status.HTTP_200_OK):
    if body:
        rec_log.info(f"DATA RECEIVED SUCCESSFUL\n{body}")
        return status_code
    else:
        rec_log.info(f"no data rec")
        return fastapi.HTTPException(status_code=500, detail="No data rec!")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=7001)
