
import asyncio
import aiohttp

from .. import fhem
from .. import utils

BASE_URL = "http://www.wienerlinien.at/ogd_realtime/monitor?rbl={}"

DEPARTURES = {
    "first": {"key": 0, "name": "{} first departure"},
    "next": {"key": 1, "name": "{} next departure"},
}

class wienerlinien:

    def __init__(self, logger):
        self.logger = logger
        self.firstnext = "first"
        self._updateloop = None
        self._last_data = None
        return

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        self.hash = hash
        self._stopid = args[3]
        self.api = WienerlinienAPI(self._stopid)
        self._updateloop = asyncio.create_task(self.update_loop())
        # delete all readings on define
        asyncio.create_task(fhem.CommandDeleteReading(hash, hash['NAME'] + " .*"))

    # FHEM FUNCTION
    async def Undefine(self, hash):
        if self._updateloop:
            self._updateloop.cancel()
        return

    # FHEM FUNCTION
    async def Set(self, hash, args, argsh):
        set_list_conf = {
           "update": {}
        }
        return await utils.handle_set(set_list_conf, self, hash, args, argsh)

    async def set_update(self, hash):
        asyncio.create_task(self.update())
        return ""

    async def update_loop(self):
        while True:
            await self.update()
            await asyncio.sleep(30)

    async def update(self):
        try:
            data = await self.api.get_json()
            self.logger.debug(data)
            if data is None:
                return
            message = data.get("message", {})
            data = data.get("data", {})
        except:
            self.logger.debug("Could not get new state")
            return

        if data is None:
            return
        try:
            flat_data = utils.flatten_json(data['monitors'][0]['lines'][0])
            flat_data_location = utils.flatten_json(data['monitors'][0]['locationStop'])

            if self._last_data:
                del_readings = set(self._last_data) - set(flat_data)
            else:
                del_readings = {}

            await fhem.readingsBeginUpdate(self.hash)
            for msg in message:
                await fhem.readingsBulkUpdateIfChanged(self.hash, "msg_" + msg, message[msg])
            for data_name in flat_data:
                await fhem.readingsBulkUpdateIfChanged(self.hash, "line_" + data_name, flat_data[data_name])
            for data_name in flat_data_location:
                await fhem.readingsBulkUpdateIfChanged(self.hash, "loc_" + data_name, flat_data_location[data_name])
            state_text = flat_data['towards'] + ": " + str(flat_data['departures_departure_0_departureTime_countdown'])
            if flat_data['trafficjam'] == 1:
                state_text += " (traffic jam)"
            await fhem.readingsBulkUpdateIfChanged(self.hash, "state", state_text)
            await fhem.readingsEndUpdate(self.hash, 1)

            # delete old readings which were not updated
            for del_reading in del_readings:
                await fhem.CommandDeleteReading(self.hash, self.hash["NAME"] + " line_" + del_reading)

            self._last_data = flat_data
            
        except Exception:
            self.logger.exception("Failed...")
            pass

class WienerlinienAPI:
    """Call API."""

    def __init__(self, stopid):
        """Initialize."""
        self.session = aiohttp.ClientSession()
        self.stopid = stopid

    async def get_json(self):
        """Get json from API endpoint."""
        value = None
        url = BASE_URL.format(self.stopid)
        try:
            response = await self.session.get(url)
            value = await response.json()
        except Exception:
            self.logger.exception("Failed...")
            pass

        return value