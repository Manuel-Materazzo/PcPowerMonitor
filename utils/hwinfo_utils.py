from configparser import ConfigParser


def get_int_reading(hwinfojson, name, unit):
    """
    Extracts a reading from a hardware info json file if present, returns 0 otherwise
    :param hwinfojson: The hardware info standardized json file
    :param name: name of the reading
    :param unit: unit of the reading
    :return: an object with the specified unit and the corresponding reading (or 0)
    """
    return next(
        (reading for reading in hwinfojson['readings'] if reading['labelOriginal'] == name),
        {"value": 0, "unit": unit}
    )


def calculate_power_multiplier(psu_efficiency: int) -> float:
    power_dissipation = 100 - psu_efficiency
    return (100 + power_dissipation) / 100


def calculate_fans_power(hwinfojson: dict, config: ConfigParser) -> float:
    fan_80mm_power = config.getint('Platform', 'Fan80mmQuantity', fallback=0)
    fan_120mm_power = 5 * config.getint('Platform', 'Fan120mmQuantity', fallback=0)
    fan_200mm_power = 7 * config.getint('Platform', 'Fan200mmQuantity', fallback=0)
    cpu_usage = get_int_reading(
        hwinfojson,
        config.get('HWInfoSensorNames', 'CpuLoad', fallback='Total CPU Usage'),
        "%"
    )
    return (fan_80mm_power + fan_120mm_power + fan_200mm_power) / 100 * max(40, cpu_usage['value'])
