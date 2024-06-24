import requests
from utils.config_utils import get_configs
from utils.hwinfo_utils import get_int_reading, calculate_power_multiplier, calculate_fans_power


class WebhookService:
    """
    Handles comunication with the remoteHWInfo service
    """

    def __init__(self, url: str, token: str):
        """
        Initializes the WebhookService that sends post requests to an endpoint
        :param url: endpoint of the WebhookService
        :param token: bearer token of the WebhookService
        """
        self.url = url
        self.token = token
        self.config = get_configs("")

    def push_load_to_webhook(self, platform_id: str, platform_name: str, hwinfojson: dict,
                             send_zeros: bool = False) -> None:
        """
        Pushes the HWinfo estimated system load to the webhook.
        :param platform_id: unique identifier of the platform
        :param platform_name: name of the platform
        :param hwinfojson: the hwinfo normalized json
        :param send_zeros: if true, the system load will be sent as 0
        :return:
        """
        if send_zeros:
            cpu_usage = {'value': 0, 'unit': '%'}
            gpu_usage = {'value': 0, 'unit': '%'}
            ram_usage = {'value': 0, 'unit': '%'}
        else:
            # tries to get the load of every component, returns 0 otherwise
            cpu_usage = get_int_reading(
                hwinfojson,
                self.config.get('HWInfoSensorNames', 'CpuLoad', fallback='Total CPU Usage'),
                "%"
            )
            gpu_usage = get_int_reading(
                hwinfojson,
                self.config.get('HWInfoSensorNames', 'GpuLoad', fallback='GPU Core Load'),
                "%"
            )
            ram_usage = get_int_reading(
                hwinfojson,
                self.config.get('HWInfoSensorNames', 'RamLoad', fallback='Physical Memory Load'),
                "%"
            )

        # push values rounded to the first decimal to webhook
        self.push_reading_to_webhook(
            platform_id + '_cpu_load',
            platform_name + " CPU Load",
            round(cpu_usage['value'], 1),
            cpu_usage['unit']
        )
        self.push_reading_to_webhook(
            platform_id + '_gpu_load',
            platform_name + " GPU Load",
            round(gpu_usage['value'], 1),
            gpu_usage['unit']
        )
        self.push_reading_to_webhook(
            platform_id + '_ram_load',
            platform_name + " RAM Load",
            round(ram_usage['value'], 1),
            ram_usage['unit']
        )

    def push_power_to_webhook(self, platform_id: str, platform_name: str, psu_efficiency: int, hwinfojson: dict,
                              detailed: bool = True, send_zeros: bool = False) -> None:
        """
        Pushes the HWinfo estimated system power usage to the webhook.
        :param platform_id: unique identifier of the platform
        :param platform_name: name of the platform
        :param psu_efficiency:
        :param hwinfojson: the hwinfo normalized json
        :param detailed: if true, sends every power reading along the total system power
        :param send_zeros: if true, the system load will be sent as 0
        :return:
        """
        if send_zeros:
            cpu_power = {'value': 0, 'unit': 'W'}
            gpu_power = {'value': 0, 'unit': 'W'}
            ram_power = {'value': 0, 'unit': 'W'}
            fans_power = {'value': 0, 'unit': 'W'}
            drives_power = {'value': 0, 'unit': 'W'}
            total_power = {'value': 0, 'unit': 'W'}
        else:
            # tries to get the power of every component, returns 0 otherwise
            cpu_power = get_int_reading(
                hwinfojson,
                self.config.get('HWInfoSensorNames', 'CpuPower', fallback='CPU Package Power'),
                "W"
            )
            gpu_power = get_int_reading(
                hwinfojson,
                self.config.get('HWInfoSensorNames', 'GpuPower', fallback='GPU Power (Total)'),
                "W"
            )

            # get the ram load and calculates the power consumption
            ram_used = get_int_reading(
                hwinfojson,
                self.config.get('HWInfoSensorNames', 'RamUsed', fallback='Physical Memory Used'),
                ""
            )
            ram_available = get_int_reading(
                hwinfojson,
                self.config.get('HWInfoSensorNames', 'RamAvailable', fallback='Physical Memory Available'),
                ""
            )
            total_ram = ram_used['value'] + ram_available['value']
            ram_power = round(total_ram / 1000 / 2.6)

            fans_power = calculate_fans_power(hwinfojson, self.config)

            drives_power = (5 * self.config.getint('Platform', 'DrivesQuantity', fallback=1))

            # computes the total  power consumption
            total_power = cpu_power['value'] + gpu_power['value'] + ram_power + fans_power + drives_power

        power_consumption_multiplier = calculate_power_multiplier(psu_efficiency)

        # push values rounded to the first decimal to webhook
        # always push the total
        self.push_reading_to_webhook(
            platform_id + '_total_power',
            platform_name + " Total Power",
            round(total_power * power_consumption_multiplier),
            "W"
        )

        # push details only if needed
        if detailed:
            self.push_reading_to_webhook(
                platform_id + '_cpu_power',
                platform_name + " CPU Power",
                round(cpu_power['value'] * power_consumption_multiplier),
                cpu_power['unit']
            )
            self.push_reading_to_webhook(
                platform_id + '_gpu_power',
                platform_name + " GPU Power",
                round(gpu_power['value'] * power_consumption_multiplier),
                gpu_power['unit']
            )
            self.push_reading_to_webhook(
                platform_id + '_ram_power',
                platform_name + " RAM Power",
                round(ram_power * power_consumption_multiplier),
                "W"
            )
            self.push_reading_to_webhook(
                platform_id + '_drives_power',
                platform_name + " Drives Power",
                round(drives_power * power_consumption_multiplier),
                "W"
            )
            self.push_reading_to_webhook(
                platform_id + '_fans_power',
                platform_name + " Fans Power",
                round(fans_power * power_consumption_multiplier),
                "W"
            )

    def push_reading_to_webhook(self, device_id: str, device_name: str, state, unit: str) -> int:
        """
        Formats and pushes a reading to the webhook
        :param device_id: the device id
        :param device_name: human friendly name
        :param state: device state or reading
        :param unit: mesurement unit
        :return:
        """
        data = {
            "state": str(state),
            "attributes": {
                "friendly_name": device_name,
                "unit_of_measurement": unit
            }
        }
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

        response = requests.post(self.url + device_id, json=data, headers=headers)
        return response.status_code
