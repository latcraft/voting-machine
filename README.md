# voting-machine

Code for Voting Machine used at Latcraft meetups (<http://latcraft.lv>) and DevTernity conference (<http://devternity.com>).

## Installation

Raspberry Pi needs to be configured to use latest Raspbian distribution and be connected to the network (cable or WiFi). 
After that you can execute the following command remotely from your computer to configure Raspberry Pi for one of the possible device types:

    gradlew initNode -Phost=<DEVICE IP ADDRESS> -Ptype=<DEVICE TYPE>

### Supported device types

 - `latcraft-voter` - button-based voting device. 

    ![First Generation](https://raw.githubusercontent.com/latcraft/voting-machine/master/images/03_button_voters.jpg)

 - `devternity-voter` - NFC-based voting device.

    ![Second Generation](https://raw.githubusercontent.com/latcraft/voting-machine/master/images/04_devternity_nfc.jpg)

 - `devternity-collector` - NFC data collector.

    ![Data Collector](https://raw.githubusercontent.com/latcraft/voting-machine/master/images/06_devternity_collectors.jpg)

 - `latcraft-dashboard` (not fully supported yet)

    ![Dashboard](https://raw.githubusercontent.com/latcraft/voting-machine/master/images/07_dashboard.jpg)

