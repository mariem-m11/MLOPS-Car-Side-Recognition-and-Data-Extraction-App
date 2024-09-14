from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.openapi.utils import get_openapi
from tensorflow.keras.models import load_model
import numpy as np
from tensorflow.keras.preprocessing.image import load_img
from tensorflow.keras.applications.vgg16 import preprocess_input #vgg16 :  convolution neural network (CNN) model supporting 16 layers.
import os
from tensorflow.keras.preprocessing import image
import shutil
from pydantic import BaseModel, validator
from typing import Any



description=""" 
To test out the code please do upload a pic in /Model in the route section

## CarPose

You can find out whether this is a side, front , back or console of the car \n 
if the pic is bad then the model can't detect and will return a "bad side " msg \n
if the file extension isn't allowed a "Invalid file extension" will appear
"""
app=FastAPI()

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="DriveSure",
        description= description,
        version="2.5.0",
        routes=app.routes,
    )

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi


model = load_model('model/final_model.h5')

target_img = os.path.join(os.getcwd(), 'static/images')

"""
class FileUpload(BaseModel):
    file: UploadFile = None

    @validator('file')
    def validate_file(cls, file):
        ALLOWED_EXT = {"jpg", "jpeg", "png"}
        if '.' not in file.filename or file.filename.rsplit('.', 1)[1] not in ALLOWED_EXT:
            raise ValueError('Invalid file extension')
        return file
"""


ALLOWED_EXT = {"jpg", "jpeg", "png"}

def allowed_file(filename: str):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXT


#prepressing method
def read_image(filename):
    img = load_img(filename, target_size=(244, 244))
    x = image.img_to_array(img) #to numpy :: each pixel represented as a list : RGB
    x = np.expand_dims(x, axis=0) #a batch of one
    x = preprocess_input(x)
    return x


@app.get("/home",tags=["Home Page"])
async def mainPage():
    return {"message": "Use /predict to upload and classify the image"}
    #will delete since the front will be added 

@app.post("/CarPose",tags=["reconnaissance"])
#flask == file = request.files['file']
async def predict(file: UploadFile): # uses a "spooled" file,  has a file-like async interface., 
    if allowed_file(file.filename):

        filename = file.filename
        file_path = os.path.join('static/images', filename)

        with open(file_path, "wb") as buffer: #write and binary(non text)  since we're "writing" to static/images
            shutil.copyfileobj(file.file, buffer) #Copy the contents of the file-like object fsrc to the file-like object fdst.
            #On Windows shutil.copyfile() uses a bigger default buffer size
        #flask == file.save(file_path) 
        
        """
        without shutil :
        
        async def predict(file: UploadFile = File(...)):
        contents = await file.read()
        with open(file.filename, 'wb') as f:
        f.write(contents)
        """

        img = read_image(file_path) #prepressing method
        classes = model.predict(img, batch_size=1)
        print(classes[0])
        
        pred = max(classes[0])
        if pred == classes[0][0]:
            return {"prediction": "console"}
        elif pred == classes[0][1]:
            return {"prediction": "back complete"}
        elif pred == classes[0][2]:
            return {"prediction": "bad side"}
        elif pred == classes[0][3]:
            return {"prediction": "front complete"}
        elif pred == classes[0][4]:
            return {"prediction": "side left complete"}
        elif pred == classes[0][5]:
            return {"prediction": "side right complete"}

    else:
        raise HTTPException(status_code=400, detail="Invalid file extension")#rather than a simple msg
        #it will terminate that request right away and send the HTTP error from the HTTPException to the client. 

# python -m uvicorn appfast:app --reload (reloads each time we make changes)



"""
without UploadFile

@app.post("/files/")
async def create_file(file: Annotated[bytes, File()]):
    return {"file_size": len(file)}
"""


