import socket
import asyncio
import time
import random
import json
import requests

import urllib3

from walkoff_app_sdk.app_base import AppBase


class SplunkActions(AppBase):
    __version__ = "1.0.1"
    app_name = "splunk-actions"

    def __init__(self, redis, logger, console_logger=None):
        """
        Each app should have this __init__ to set up Redis and logging.
        :param redis:
        :param logger:
        :param console_logger:
        """
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        super().__init__(redis, logger, console_logger)


    def run_search_export(self, auth, url, query):
        url = '%s/services/search/jobs/export' % (url)
        run_search_result = requests.post(url, auth=auth, data=query, timeout=10, verify=False)

        return run_search_result


    def run_splunk_search(self, url, username, password, search_query, earliest_time="-24h", latest_time="now", return_format="json"):
        auth = (username, password)

        # Handle the searches that use inputlookup
        if not (search_query.startswith('|inputlookup') or search_query.startswith('| inputlookup')):
            print("Doesn't start with |inputlookup")
            search_query = "search " + search_query

        query = {
            "search": "%s" % search_query,
            "earliest_time": earliest_time,
            "latest_time": latest_time,
            "output_mode": "json",
            "exec_mode": "oneshot",
            "enable_lookups": True,
            "preview": False
        }

        print("Current search: %s" % query["search"])

        run_search_result = {}
        try:
            run_search_result = self.run_search_export(auth, url, query)
            run_search_result_clean_str = json.dumps(json.loads(run_search_result.text))
            run_search_result_json = json.loads(run_search_result_clean_str)
        except requests.exceptions.ConnectTimeout as e:
            print("Timeout: %s" % e)
            return {"success": False, "reason": "Timeout: %s" % e}

        if run_search_result.status_code != 200:
            print("Bad status code: %d" % run_search_result.status_code)
            return {"success": False, "reason": "Bad status code %d - expecting 200." % run_search_result.status_code}

        ret = {"success": True, "results": run_search_result_json}

        return ret


if __name__ == "__main__":
    SplunkActions.run()
