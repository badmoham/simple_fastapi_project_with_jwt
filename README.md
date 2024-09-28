# simple_fastapi_project_with_jwt

## FastApi-App

1. Make a Directory for the Project and navigate into it
     > mkdir fastapi-app && cd fastapi-app

2. Create a Python Virtual Environment and Activate it
     > python3 -m venv venv 
     > ls
     > source venv/bin/activate

3. Install Fastapi 
     > pip install fastapi

4. Install an ASGI server 
     > pip install "uvicorn[standard]"

5. Install requirements.txt for all of dependencies 
     > pip install -r [requirements.txt](requirements.txt)

6. To run the app, with uvicorn using the file_name:app_instance

     > uvicorn main:app --reload

Preview the App at http://127.0.0.1:8000/ and the out-of-the-box [API Documentation](http://127.0.0.1:8000/docs)

### signing in
all the endpoints are 'authorized only' , therefore you need to log-in and get your jwt credential before using any endpoint.

default user:pass choosed for this project are as stated below

username: ```johndoe```
password: ```123456```


made with 🔥