# PSM_MQTT_OPENPLC
This is a script to allow OpenPLC PSM to send data to mqtt broker and to write variables using tagname from MQTT.

This allows SCADA/MES to get values easier from OpenPLC runtime.

This need 2 things:
 - installation of paho-mqtt for python, entering ```/workdir/.venv/bin/pip3 install paho-mqtt```
 - modification of ```/workdir/webserver/core/psm/psm.py``` changing d_inputs, d_outputs, a_inputs and a_outputs so that external device modbus values are accepted (n>800)

   ```#Initialize points database
   d_inputs = ModbusSequentialDataBlock(0, [0]*3000)
   d_outputs = ModbusSequentialDataBlock(0, [0]*4000)
   a_inputs = ModbusSequentialDataBlock(0, [0]*2000)
   a_outputs = ModbusSequentialDataBlock(0, [0]*2000)
This works on my OpenPLC istance:

https://github.com/user-attachments/assets/89b7f1e5-3d24-46fb-a244-d7416f705013

See ya
