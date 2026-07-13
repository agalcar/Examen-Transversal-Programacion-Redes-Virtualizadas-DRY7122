from ncclient import manager

HOST = "192.168.56.103"
PORT = 830
USERNAME = "cisco"
PASSWORD = "cisco123!"

netconf_filter = """
<filter>
  <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
    <hostname/>
  </native>
</filter>
"""

with manager.connect(
    host=HOST,
    port=PORT,
    username=USERNAME,
    password=PASSWORD,
    hostkey_verify=False
) as m:

    respuesta = m.get_config(source="running", filter=netconf_filter)
    print(respuesta.xml)
