FROM python:3.7-slim

COPY ./requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY ./wf_market_gsheet /wf_market_gsheet

CMD ["python", "-m", "wf_market_gsheet.main"]
