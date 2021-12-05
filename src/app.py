import argparse
import datetime;
import os
import pandas as pd

import segmentation
import clustering

from aiohttp import web
from aiohttp_swagger import *
from elasticsearch import Elasticsearch
from elasticsearch.helpers import async_bulk

parser = argparse.ArgumentParser(description="HyperAdTech aiohttp server")
parser.add_argument('--host')
parser.add_argument('--port')

es = Elasticsearch(['http://localhost:9200/'])

async def gendata(index: str, documents):
    for document in documents:
        yield {
            "_index": index,
            "doc": document,
        }


async def index(request):
    return web.FileResponse('./index.html')


async def predict(request):
    """
    ---
    description: Ok, gimme data to predict your fickin metrics.
    consumes:
      - application/json
    tags:
    - predict
    parameters: 
    - in: body
      name: data
      description: Data to predict.
      schema:
        type: array
        items:
          type: object
          properties:
            gamecategory:
              type: string
              default: Applications
            subgamecategory:
              type: string
              default: Shopping
            bundle:
              type: string
              default: com.allgoritm.youla
            created:
              type: string
              format: date-time
              default: '2021-09-19 17:31:33'
            shift:
              type: string
              default: MSK+2
            oblast:
              type: string
              default: Томская область
            city:
              type: string
              default: Северск
            os:
              type: string
              default: android
            osv:
              type: string
              default: '10.0'
    produces:
    - application/json
    responses:
      "200":
        description: OK
        content:
          application/json:
            schema:
              type: array
              items:
                type: object
                properties:
                  '1':
                    type: number
                    format: float
                  '3':
                    type: number
                    format: float
                  '4':
                    type: number
                    format: float
                  '5':
                    type: number
                    format: float
                  prediction:
                    type: number
                    format: float
                  confidence:
                    type: number
                    format: float
    """
    json = await request.json()
    data = pd.DataFrame(json)
    data['created'] = pd.to_datetime(data['created'])

    prediction = segmentation.predict(data)[[1, 3, 4, 5, 'prediction', 'confidence']]
    response = prediction.to_json(orient = "records")

    if es.ping():
        await async_bulk(es, gendata('segmentation', response))

    return web.json_response(response)


async def csv(request):

    """
    ---
    description: Ok, gimme data to predict your fickin metrics.
    tags:
    - predict
    parameters: 
    - in: formData
      name: file
      type: file
      description: Data to predict.
    produces:
    - application/json
    responses:
      "200":
        description: OK
    """

    reader = await request.multipart()
    csv = await reader.next()

    ts = datetime.datetime.now().timestamp()
    temp_file_name = f'temp{ts}.csv'
    with open(temp_file_name, 'wb') as temp:
        while True:
            chunk = await csv.read_chunk()
            if not chunk:
                break
            temp.write(chunk)
        
    df = pd.read_csv(temp_file_name)
    df = df.fillna('missing')
    df['created'] = pd.to_datetime(df['created'])
    df['Segment'] = segmentation.predict(df)['prediction']
    df = segmentation.get_time_features(df)

    df = clustering.preprocessing(df)
    df['cluster'] = clustering.model_inference(df)

    table = clustering.table_generation(df)

    os.remove(temp_file_name)
    
    response = {
        'records': df.to_json(orient = "records"),
        'table': table.reset_index().to_json(orient = "records")
    }
    return web.json_response(response)


def main():
    STATIC_PATH = os.path.join(os.path.dirname(__file__), "static")    

    app = web.Application()
    app.router.add_static('/static', STATIC_PATH, name='static')
    app.router.add_route('GET', "/", index)
    app.router.add_route('POST', "/predict", predict)
    app.router.add_route('POST', "/csv", csv)

    setup_swagger(app, ui_version=2, ) 

    args = parser.parse_args()
    web.run_app(app, host=args.host, port=args.port)


if __name__ == '__main__':
    main()