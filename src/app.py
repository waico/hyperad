import argparse
import os
import pandas as pd

import segmentation

from aiohttp import web
from aiohttp_swagger import *

parser = argparse.ArgumentParser(description="HyperAdTech aiohttp server")
parser.add_argument('--host')
parser.add_argument('--port')


def test_predict(pickle_path: str):

    from datetime import datetime

    start = datetime.now()

    df = pd.read_pickle(pickle_path)
    df['created'] = pd.to_datetime(df['created'])
    df = df.fillna('missing')

    prediction = segmentation.predict(df)
    prediction.info()

    print(datetime.now() - start)


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
    return web.json_response(prediction.to_json(orient = "records"))


def main():
    STATIC_PATH = os.path.join(os.path.dirname(__file__), "static")    

    app = web.Application()
    app.router.add_static('/static', STATIC_PATH, name='static')
    app.router.add_route('GET', "/", index)
    app.router.add_route('POST', "/predict", predict)

    setup_swagger(app, ui_version=2, ) 

    args = parser.parse_args()
    web.run_app(app, host=args.host, port=args.port)


if __name__ == '__main__':
    main()