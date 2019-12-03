import os
from flask import Flask, Response, request
from requests_toolbelt import MultipartEncoder
# local modules
from doc_api import doc_utils

# класс сообщений при ошибках во вложении
class AttachmentException(Exception):
    pass

def __check_attachment(request, in_file):
    # файл должен быть
    # assert len(request.files) > 0
    if len(request.files) == 0:
        raise AttachmentException('error', 'Отсутствует вложенный файл')

    # файл должен с тегом in_file
    # assert not pdf_file is None
    if in_file is None:
        raise AttachmentException('error', 'отсутствует входной параметр in_file')
    
    # файл должен быть не пустым
    # assert len(pdf_file.read(1)) > 0
    if len(in_file.read(1)) == 0:
        raise AttachmentException('warning', 'Файл пустой')
    
    # принимаем на вход только pdf
    # assert pdf_file.mimetype == 'application/pdf'
    if not in_file.mimetype == 'application/pdf':
        raise AttachmentException('error', 'Допускаются только PDF-файлы')


def create_app():
    app = Flask(__name__)
    @app.route('/', methods=['GET'])
    def index():
        return 'Сервисы компьютерного зрения для налогового мониторинга'

    @app.route('/api/excludeApproval', methods=['GET', 'POST'])
    def exclude_approval():
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