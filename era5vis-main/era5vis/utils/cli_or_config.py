"""
Utility function to prioritize command-line arguments over configuration file values.
Author: Leah Herrfurth
"""
def cli_or_config(cli_val, config_val, default=None):
    if cli_val is not None:
        return cli_val
    elif config_val is not None:
        return config_val
    else:
        return default