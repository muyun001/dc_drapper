FROM python:3

COPY download_center-5.2.1-py3-none-any.whl download_center-5.2.1-py3-none-any.whl

RUN pip install -i https://mirrors.aliyun.com/pypi/simple/ download_center-5.2.1-py3-none-any.whl

ADD . /app

WORKDIR /app

CMD ["python", "dc_wrapper.py"]