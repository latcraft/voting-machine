
1. Boot to desktop/autologin
2. Change password to '*********'
3. Disable screen sleep in screen saver
4. Check timezone to be Europe/Riga
5. Install Emoji plugin in Chrome
6. Update system

        sudo apt-get update
        sudo apt-get upgrade

sudo apt-get install chromium-browser x11-xserver-utils unclutter
sudo apt-get install xscreensaver

sudo nano /etc/network/interfaces

source-directory /etc/network/interfaces.d

auto lo
iface lo inet loopback

iface eth0 inet manual

allow-hotplug wlan0
iface wlan0 inet manual
wpa-conf /etc/wpa_supplicant/wpa_supplicant.conf


sudo nano /etc/wpa_supplicant/wpa_supplicant.conf


ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

network={
        ssid="aestas_hq"
        psk="********"
        key_mgmt=WPA-PSK
}

network={
        ssid="DevTernity"
        psk="thebestconference"
        key_mgmt=WPA-PSK
}

network={
        ssid="Devternity 2017"
        psk="thebestconference"
        key_mgmt=WPA-PSK
}

network={
        ssid="Devternity2017"
        psk="thebestconference"
        key_mgmt=WPA-PSK
}

network={
        ssid="DevTernity"
        psk="hello2018"
        key_mgmt=WPA-PSK
}

network={
        ssid="Devternity"
        psk="hello2018"
        key_mgmt=WPA-PSK
}




nano /home/pi/.config/lxsession/LXDE-pi/autostart

@lxpanel --profile LXDE-pi
@pcmanfm --desktop --profile LXDE-pi
@xset s off
@xset -dpms
@xset s noblank
@sed -i 's/"exited_cleanly": false/"exited_cleanly": true/' ~/.config/chromium-browser Default/Preferences
@chromium-browser --noerrdialogs --kiosk http://dashboard.devternity.com/cycle --incognito --disable-translate


