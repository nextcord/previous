FROM python:3.9
WORKDIR opt/
RUN pip install git+https://github.com/nextcord/nextcord.git jishaku
COPY . ./
CMD ["python", "main.py"]
