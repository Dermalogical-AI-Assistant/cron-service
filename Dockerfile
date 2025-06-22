FROM python:3.12-slim

# Set the container timezone to Asia/Bangkok
ENV TZ=Asia/Bangkok

WORKDIR /app

COPY . .

RUN apt-get update && apt-get install -y tzdata \
 && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
 && echo $TZ > /etc/timezone \
 && pip install --upgrade pip \
 && pip install -r requirements.txt

CMD ["python", "-u", "-m", "main"]
