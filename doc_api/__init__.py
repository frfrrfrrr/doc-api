import os
import sys
from flask import Flask, Response, request, has_request_context
from flask.logging import default_handler
import logging
from logging.config import dictConfig
from requests_toolbelt import MultipartEncoder
# local modules
from doc_api import doc_utils

# класс сообщений при ошибках во вложении
class AttachmentException(Exception):
    pass

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'default_handler': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://sys.stdout',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['default_handler']
    }
})

class RequestFormatter(logging.Formatter):
    def format(self, record):
        if has_request_context():
            record.url = request.url
            record.remote_addr = request.remote_addr
        else:
            record.url = None
            record.remote_addr = None
        return super().format(record)

formatter = RequestFormatter(
    'request handler [%(asctime)s] %(remote_addr)s requested %(url)s\n'
    '%(levelname)s in %(module)s: %(message)s zazaza'
)
default_handler.setFormatter(formatter)

def pretty_print_POST(req):
    print('-----start of request info-----')
    print(f'request content type: {req.content_type}')
    if not req.values is None:
        print(f'request values: {req.values}')
    if not req.files is None:
        print(f'request files are: {req.files}')
    if not req.data is None:
        print(f'(warning if not empty) request data: {req.data}')        
    print('-----end of request info-----')

def __check_attachment(request, in_file):
    # файл должен быть
    if len(request.files) == 0:
        raise AttachmentException('error', 'Отсутствует вложенный файл')

    # файл должен с тегом in_file
    if in_file is None:
        raise AttachmentException('error', 'отсутствует входной параметр in_file')
    
    # файл должен быть не пустым
    if len(in_file.read(1)) == 0:
        raise AttachmentException('warning', 'Файл пустой')
    
    # принимаем на вход только pdf
    if not in_file.mimetype == 'application/pdf':
        raise AttachmentException('error', 'Допускаются только PDF-файлы')


def create_app():
    app = Flask(__name__)
    @app.route('/', methods=['GET'])
    def index():
        return 'Сервисы компьютерного зрения для налогового мониторинга'

    @app.route('/api/excludeApproval', methods=['GET', 'POST'])
    def exclude_approval():
        pretty_print_POST(request)
        try:
            # инициализация переменных
            status = 'success'
            message = ''
            # вытаскиваем файл из запроса здесь, а не в __check*, т.к. он нужен несколько раз
            pdf_file = request.files.get('in_file')
            __check_attachment(request, pdf_file)
            output = doc_utils.process_pdf_from_bin(pdf_file, pdf_file.filename)
            out_file = (pdf_file.filename, output, 'application/pdf')
        except AttachmentException as e:
            out_file = None
            status, message = e.args
        except Exception as e:
            status = 'error'
            message = str(e)
        finally:
            m = MultipartEncoder(
                fields={'out_file': out_file,
                'status': status,
                'message': message}
            )        
            return Response(m.to_string(), mimetype=m.content_type)
    return app