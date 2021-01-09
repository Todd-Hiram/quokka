import napalm
from quokka.models.apis import get_facts, set_facts
from quokka.controller.utils import log_console
from ncclient import manager
# The following comment/lines are to work around a Pycharm bug
# noinspection PyUnresolvedRefernces
from xml.dom.minidom import parseString


def get_napalm_device(device):

    if device["os"] == "ios" or device["os"] == "iosxe":
        driver = napalm.get_network_driver("ios")
    elif device["os"] == "nxos-ssh":
        driver = napalm.get_network_driver("nxos_ssh")
    elif device["os"] == "nxos":
        driver = napalm.get_network_driver("nxos")
    else:
        return "failure", "Unsupported OS"

    if device["os"] in {"ios", "iosxe", "nxos-ssh"}:
        napalm_device = driver(
            hostname=device["hostname"],
            username=device["username"],
            password=device["password"],
            optional_args={"port": device["ssh_port"]}
        )
    else:
        napalm_device = driver(
            hostname=device["hostname"],
            username=device["username"],
            password=device["password"],
        )

    return napalm_device


def get_device_info(device, requested_info, get_live_info=False):

    if device["transport"] == "napalm":
        return get_device_info_napalm(device, requested_info, get_live_info)
    elif device["transport"] == "ncclient":
        # log_console(f"Getting device info via ncclient for {device['name']}")
        return get_device_info_ncclient(device, requested_info, get_live_info)
    elif device["transport"] == "HTTP-REST" and requested_info == "facts":
        # HTTP-REST devices will update device information with their heartbeats, no need to fetch it
        facts = {
            "fqdn": device["hostname"],
            "hostname": device["hostname"],
            "os_version": device["version"],
            "serial_number": device["serial"],
            "uptime": device["uptime"],
            "vendor": device["vendor"]
        }
        return "success", {"facts": facts}

    else:
        return "failure", "Unable to retrieve requested info from device"
