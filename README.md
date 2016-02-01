# voting-machine

Code for Voting Machine used at Latcraft meetups (<http://latcraft.lv>) and DevTernity conference (<http://devternity.com>).

## Installation

Raspberry Pi needs to be configured to use latest Raspbian distribution and be connected to the network (cable or WiFi). 

After that you can execute the following command remotely from your computer to configure Raspberry Pi:

    gradlew -Phost=<DEVICE CONFIG REF> initNode configNode

where `<DEVICE CONFIG REF>` is the name of the host configuration file. For example, for the following command:

    gradlew -Phost=vt1 initNode configNode

the configuration will be taken from the `hosts/vt1.groovy` file. Example configuration looks like this:

    host     = '192.169.1.13'
    user     = 'pi'
    password = 'raspberry'
    hostname = 'voting1'
    mac      = 'e8:4e:06:29:08:9e'
    type     = 'latcraft_voter'

It is also possible to execute same command for several devices:

    gradlew -Phost=vt1,vt2,vt3 initNode configNode

### Supported device types

 - `latcraft_voter` - button-based voting device. 

    ![First Generation](https://raw.githubusercontent.com/latcraft/voting-machine/master/images/03_button_voters.jpg)

 - `devternity_voter` - NFC-based voting device.

    ![Second Generation](https://raw.githubusercontent.com/latcraft/voting-machine/master/images/04_devternity_nfc.jpg)

 - `devternity_collector` - NFC data collector.

    ![Data Collector](https://raw.githubusercontent.com/latcraft/voting-machine/master/images/06_devternity_collectors.jpg)

 - `latcraft_dashboard` (not fully supported yet)

    ![Dashboard](https://raw.githubusercontent.com/latcraft/voting-machine/master/images/07_dashboard.jpg)
