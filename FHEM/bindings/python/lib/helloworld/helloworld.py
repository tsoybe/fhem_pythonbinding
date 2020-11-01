
import asyncio

from .. import fhem
from .. import utils

class helloworld:

    def __init__(self, logger):
        self.logger = logger
        return

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        await fhem.readingsBeginUpdate(hash)
        await fhem.readingsBulkUpdateIfChanged(hash, "state", "on")
        await fhem.readingsEndUpdate(hash, 1)
        return ""

    # FHEM FUNCTION
    async def Undefine(self, hash):
        return

    # FHEM FUNCTION
    async def Set(self, hash, args, argsh):
        set_list_conf = {
           "mode": { "args": ["mode"], "argsh": ["mode"], "params": { "mode": { "default": "eco", "optional": False }}, "options": "eco,comfort" },
           "desiredTemp": { "args": ["temperature"], "options": "slider,10,1,30"},
           "holidayMode": { "args": ["start", "end", "temperature"], "params": { "start": {"default": "Monday"}, "end": {"default": "23:59"}, "temperature": {"default": ""}}},
           "on": { "args": ["seconds"], "params": { "seconds": { "default": "", "optional": True}}},
           "off": {}
        }
        return await utils.handle_set(set_list_conf, self, hash, args, argsh)

    async def set_on(self, hash, params):
        seconds = params['seconds']
        await fhem.readingsSingleUpdate(hash, "state", "on " + seconds, 1)
        return ""

    async def set_off(self, hash):
        await fhem.readingsSingleUpdate(hash, "state", "off", 1)
        return ""

    async def set_mode(self, hash, params):
        mode = params['mode']
        await fhem.readingsSingleUpdate(hash, "mode", mode, 1)
        return ""

    async def set_desiredTemp(self, hash, params):
        temp = params['temperature']
        await fhem.readingsSingleUpdate(hash, "mode", temp, 1)
        return ""

    async def set_holidayMode(self, hash, params):
        start = params['start']
        end = params['end']
        temp = params['temperature']
        await fhem.readingsSingleUpdate(hash, "start", start, 1)
        await fhem.readingsSingleUpdate(hash, "end", end, 1)
        await fhem.readingsSingleUpdate(hash, "temp", temp, 1)
        return ""
