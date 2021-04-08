import socket
import asyncio
import time
import random
import json
import requests

from walkoff_app_sdk.app_base import AppBase

class PrismaCloud(AppBase):
    __version__ = "1.0.0"
    app_name = "prisma-cloud"  # this needs to match "name" in api.yaml

    def __init__(self, redis, logger, console_logger=None):
        """
        Each app should have this __init__ to set up Redis and logging.
        :param redis:
        :param logger:
        :param console_logger:
        """
        super().__init__(redis, logger, console_logger)


    # Prisma Cloud Authentication - Get JWT Token before injecting into header
    def get_jwt(self, url, accesskey, secretkey):
        headers = {
            "accept": "application/json; charset=UTF-8",
            "content-type": "application/json; charset=UTF-8"
        }
        payload = "{\"username\":\"" + accesskey + \
            "\",\"password\":\"" + secretkey + "\"}"
        response = requests.request(
            "POST", url+"/login", headers=headers, data=payload)
        if response.status_code != 200:
            print("Prisma cloud token is wrong or expired boy! status code : " +
                str(response.status_code))
        else:
            print("Ok for the prisma token")
        return response.json()["token"]


    # Prisma Cloud Authentication - Make the header with the JWT Token - Valid for 10 minutes
    def generate_prisma_header(self, url, accesskey, secretkey):
        headers = {
            "accept": "*/*",
            "x-redlock-auth": self.get_jwt(url, accesskey, secretkey)
        }
        return headers

    async def get_alert(self, url, accesskey, secretkey, alertId):
        suffix = "/alert/" + str(alertId)
        # headers = {
        # 'Content-Type': 'application/json',
        # 'x-redlock-auth': self.get_jwt(url, accesskey, secretkey)
        # }   
        headers = self.generate_prisma_header(url, accesskey, secretkey)     
        try:
            r = requests.get(url + suffix, headers=headers)
            return json.dumps(r.json())
        except Exception as e:
            return e.__class__
    


if __name__ == "__main__":
    asyncio.run(PrismaCloud.run(), debug=True)
