FROM python:3.9
WORKDIR opt/
RUN pip install jishaku
RUN pip uninstall discord.py
RUN pip install algoliasearch
RUN pip install git+https://github.com/nextcord/nextcord.git
COPY . ./
CMD ["python", "main.py"]
