# iCloud-Homie
 iCloud to Homie MQTT Bridge

Connects iCloud Accounts/Devices to [Homie 4 MQTT convention](https://homieiot.github.io/).

To start as a service on raspbian 

Create icloud_homie.yml in /etc using the following settings:


```yaml
mqtt:
  MQTT_BROKER: 
  MQTT_PORT: 1883

icloud:
  account_name: 
    username: 
    password: 
  account_name:
    username:
    password:

update_interval:
  ```

  Create icloud-homie.service in /etc/systemd/system

  ```service
[Unit]
Description=iCloud Homie
After=multi-user.target

[Service]
User=pi
Type=simple
ExecStart=/usr/bin/python3 /usr/local/bin/icloud_homie_start.py
Restart=on-abort

[Install]
WantedBy=multi-user.target
```

The first time the service starts, you should receive a text message on your phone with a verifcation code (do not use the verifcation code from the Apple App). You need to send this code back to the Homie account device. Easy to do this with MQTT Explorer.

Publish: homie/icloudaccount/account/verificationcode/set with the verification code as a raw payload

