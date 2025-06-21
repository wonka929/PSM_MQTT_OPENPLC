#import all your libraries here
import psm
import time
import paho.mqtt.client as mqtt
import json

# Configurazione MQTT
MQTT_BROKER = "_IPADDRESS_"
MQTT_PORT = "_1883_"
MQTT_USERNAME = "_USERNAME_"'
MQTT_PASSWORD = "_PASSWORD_"
MQTT_TOPIC_PUB = "_openplc/inputs_"
MQTT_TOPIC_SUB = "_openplc/outputs_"
PUBLISH_INTERVAL = 5  # Publication interval

psm.start()

# Initialize MQTT client
mqtt_client = mqtt.Client()
mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT with code", rc)
    client.subscribe(MQTT_TOPIC_SUB)

def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        write_variables(data)  # Write received values
    except Exception as e:
        print("Error handling MQTT message:", e)

# Global variables
variables = {}

def hardware_init():
    global variables
    start_copy = False
    # Read the name of the active file
    with open("/workdir/webserver/active_program", "r") as active_file:
        active_st_filename = active_file.read().strip()
    st_filepath = f"/workdir/webserver/st_files/{active_st_filename}"
    # Read the active .st file and import variables
    with open(st_filepath, "r") as f:
        for line in f:
            line_stripped = line.strip()
            if line_stripped.startswith("VAR"):
                start_copy = True
                continue
            elif line_stripped.startswith("END_VAR"):
                start_copy = False
                continue
            if start_copy:
                if "%" in line_stripped:
                    try:
                        var_name, var_position = line_stripped.split(":")[0].strip().split(" AT ")
                        variables[var_name.strip()] = var_position.strip()
                    except Exception as e:
                        print(f"Error parsing line: {line_stripped} - {e}")

def write_variables(data):
    global variables
    for var_name, value in data.items():
        try:
            if var_name in variables:
                psm.set_var(variables[var_name].replace("%", ""), value)
            else:
                print(f"Variable {var_name} not found in variables.")
        except Exception as e:
            print(e)

def send_variables_values():
    payload = {}
    global variables
    for var_name, var_position in variables.items():
        try:
            value = psm.get_var(var_position)
            payload[var_name] = value
        except Exception as e:
            print(f"Error reading {var_name}: {e}")
            continue
    mqtt_client.publish(MQTT_TOPIC_PUB, json.dumps(payload))

if __name__ == "__main__":
    hardware_init()
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
    mqtt_client.loop_start()
    while not psm.should_quit():
        send_variables_values()
        time.sleep(PUBLISH_INTERVAL) # You can adjust the psm cycle time here
    psm.stop()
