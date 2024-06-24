import requests


def change_reading_types(json_data: dict) -> dict:
    reading_types = {'0': 'None', '1': 'Temp', '2': 'Voltage',
                     '3': 'Fan', '4': 'Current', '5': 'Power',
                     '6': 'Clock', '7': 'Usage', '8': 'Other'}
    for index, value in enumerate(json_data['readings']):
        json_data['readings'][index]['readingTypeName'] = reading_types[str(value['readingType'])]
    return json_data


class HWInfoService:
    """
    Handles comunication with the remoteHWInfo service
    """

    def __init__(self, host, port):
        """
        Initializes the HWInfoService that communicates with the remoteHWInfo service
        :param host: host of the remoteHWInfo service
        :param port: port of the remoteHWInfo service
        """
        self.url = f'http://{host}:{port}/json.json'

    def get_normalized_hwinfo_json(self) -> dict:
        json_data = requests.get(self.url, verify=False, timeout=5).json()['hwinfo']

        for reading_index, reading in enumerate(json_data['readings']):
            json_data['readings'][reading_index]['readingIndex'] = reading_index

        change_reading_types(json_data)

        return json_data

    # def replaceUrlPlaceholders(url: str, device_id, device_name):
    #    temp = url.replace("[deviceId]", str(device_id))
    #    temp = url.replace("[deviceNameTitleCase]", str(device_name).title().replace(" ", ""))
    #    temp = url.replace("[deviceNameSnakeCase]", str(device_name).replace(" ", "_"))
    #    temp = url.replace("[deviceName]", str(device_name).replace(" ", ""))
    #    return temp
