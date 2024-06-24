import os
import configparser

config = configparser.ConfigParser()


def get_configs(filename: str) -> configparser.ConfigParser:
    """
    Reads the config file, or creates it if it doesn't exist.
    :param filename:
    :return:
    """
    global config
    # skip if already loaded
    if config.has_option('HWInfo', 'host'):
        return config

    # output default config file if not found
    if not os.path.isfile(filename):
        config['HWInfo'] = {'Host': '127.0.0.1', 'Port': 60005}
        config['Webhook'] = {
            'Enabled': 'True',
            'Token': 'xxx',
            'Url': 'http://127.0.0.1:8123/api/states/',
            'SendSystemLoad': 'True',
            'SendDetailedPowerUsage': 'False'
        }
        config['Platform'] = {
            'Name': 'Main Pc',
            'Id': 'main_pc',
            'DrivesQuantity': '3',
            'PsuPowerEfficiencyPercentage': '85',
            'Fan80mmQuantity': '2',
            'Fan120mmQuantity': '4',
            'Fan200mmQuantity': '0',
        }
        config['HWInfoSensorNames'] = {
            'CpuPower': 'CPU Package Power',
            'GpuPower': 'GPU Power (Total)',
            'CpuLoad': 'Total CPU Usage',
            'GpuLoad': 'GPU Core Load',
            'RamLoad': 'Physical Memory Load',
            'RamUsed': 'Physical Memory Used',
            'RamAvailable': 'Physical Memory Available'
        }
        with open(filename, 'w') as configfile:
            config.write(configfile)

    # load config
    config.read(filename)

    return config
