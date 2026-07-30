DOMAIN = "mcsmanager"

CONF_HOST = "host"
CONF_API_KEY = "api_key"
CONF_DAEMON_ID = "daemonId"
CONF_INSTANCE_UUID = "instance_uuid"

SCAN_INTERVAL_SECONDS = 10

STATUS_MAP = {
    -1: "Stopped",
    0: "Stopped",
    1: "Stopping",
    2: "Starting",
    3: "Running",
}
