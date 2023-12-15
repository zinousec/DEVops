import os

SECRET_KEY = 'secret-key'

SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://std_2172_exam:password@std-mysql.ist.mospolytech.ru/std_2172_exam'
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = True

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'media', 'images')
ADMIN_ROLE_ID = 1
MODER_ROLE_ID = 2
PER_PAGE = 10