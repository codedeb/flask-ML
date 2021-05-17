import os
from ocr_wrapper_service.app import create_app

app = create_app(os.getenv('APP_SETTING_MODULE'))

if __name__  == "__main__":
    app.run(host="0.0.0.0", port=5000)

# gunicorn run_app:app
# gunicorn -c python:devops.gunicorn_sample_flask_app_config wsgi:app
# python wsgi.py
# curl -i localhost:5000/
# curl -i localhost:5000/get
# curl -X POST localhost:5000/post
# ps -ef | grep python
# chmod 755 python_build.sh