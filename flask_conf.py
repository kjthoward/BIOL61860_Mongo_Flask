# Flask app set up, this can be left 
from flask import Flask
from flask_bootstrap import Bootstrap
app = Flask(__name__,
            static_url_path='', 
            static_folder='static',
            template_folder='templates')

app.config['SECRET_KEY'] = 'C2HWGVoMGfNTBsrYQg8EcMrdTimkZfAb'

Bootstrap(app)
