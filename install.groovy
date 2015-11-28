
defaultHost = args[0]
defaultUser = 'pi'
defaultPassword = 'raspberry'

remoteSession {

  exec 'sudo apt-get -y update'
  exec 'sudo apt-get -y upgrade'

  // Install developer tools.
  exec 'sudo apt-get -y install nano git subversion bzr dos2unix iceweasel curl wget'

  // TODO: Enable i2c with raspi-config ("Advanced Options" -> "I2C" -> "Yes"): sudo raspi-config
  // TODO: sudo dpkg-reconfigure tzdata
  // TODO: sudo service cron restart

  // Install i2c libraries.
  exec 'sudo apt-get -y install i2c-tools'

  // Install useful Python libraries.
  exec 'sudo apt-get -y install python-setuptools'
  exec 'sudo apt-get -y install python-smbus'
  exec 'sudo apt-get -y install python-yaml'
  exec 'sudo apt-get -y install python-picamera'

  // Install libnfc.
  exec 'wget http://dl.bintray.com/nfc-tools/sources/libnfc-1.7.1.tar.bz2'
  exec 'tar -xf libnfc-1.7.1.tar.bz2'
  prefix('cd ~/libnfc-1.7.1 ; sudo ') {
    exec './configure --prefix=/usr --sysconfdir=/etc'
    exec 'make'
    exec 'make install'
  }
  exec 'sudo cp ~/libnfc-1.7.1/contrib/udev/42-pn53x.rules /lib/udev/rules.d/'
  if (!remoteFile('/etc/modprobe.d/blacklist-libnfc.conf').text.readLines().find { it.startsWith('blacklist pn533') }) {
    exec /sudo sh -c "echo 'blacklist pn533' >> /etc/modprobe.d/blacklist-libnfc.conf"/
  }
  if (!remoteFile('/etc/modprobe.d/blacklist-libnfc.conf').text.readLines().find { it.startsWith('blacklist nfc') }) {
    exec /sudo sh -c "echo 'blacklist nfc' >> /etc/modprobe.d/blacklist-libnfc.conf"/
  }

  // Install GrovePi Python modules.
  exec 'cd ~/GrovePi/Software/Python ; sudo python setup.py install'

  // Configure i2c kernel modules.
  if (!remoteFile('/etc/modules').text.readLines().find { it.startsWith('i2c-bcm2708') }) {
    exec /sudo sh -c "echo 'i2c-bcm2708' >> /etc/modules"/
  }
  if (!remoteFile('/etc/modules').text.readLines().find { it.startsWith('i2c-dev') }) {
    exec /sudo sh -c "echo 'i2c-dev' >> /etc/modules"/
  }

  // Install nfcutils.
  exec 'wget https://nfc-tools.googlecode.com/files/nfcutils-0.3.2.tar.gz'
  exec 'tar -xf nfcutils-0.3.2.tar.gz'
  prefix('cd ~/nfcutils-0.3.2 ; sudo ') {
    exec './configure --prefix=/usr --sysconfdir=/etc'
    exec 'make'
    exec 'make install'
  }

  // Install nfc-eventd.  
  exec 'wget https://nfc-tools.googlecode.com/files/nfc-eventd-0.1.7.tar.gz'
  exec 'tar -xf nfc-eventd-0.1.7.tar.gz'
  prefix('cd ~/nfc-eventd-0.1.7 ; sudo ') {
    exec './configure --prefix=/usr --sysconfdir=/etc --enable-debug'
    exec 'make'
    exec 'make install'
  }

  // Install pyusb.
  exec 'https://github.com/walac/pyusb/archive/1.0.0b1.tar.gz'
  exec 'tar -xf 1.0.0b1.tar.gz'
  exec 'cd ~/pyusb-1.0.0b1 ; sudo python setup.py install'

  // Install nfcpy.    
  exec 'bzr branch lp:nfcpy'
  remoteFile('nfcpy/setup.py').text ='''
    #!/usr/bin/env python
    
    from distutils.core import setup
	
    import nfc

    setup(
      name='nfc',
      version=nfc.__version__,
      description='Python NFC access module',
      url='http://nfcpy.org',
      packages=['nfc', 'nfc.dev', 'nfc.handover', 'nfc.llcp', 'nfc.ndef', 'nfc.snep', 'nfc.tag']
    )
  '''
  exec 'cd nfcpy ; sudo python setup.py install'

  // Configure WiFi networks.
  // TODO: sudo nano /etc/network/interfaces
  //  auto lo
  //  
  //  iface lo inet loopback
  //  iface eth0 inet dhcp
  //  
  //  allow-hotplug wlan0
  //  
  //  iface wlan0 inet dhcp
  //  wpa-ssid aestas_hq
  //  wpa-psk *******    
  // To be able to automatically connect to several WiFi networks you can read [these intructions](http://www.instantsupportsite.com/self-help/raspberry-pi/raspberry-connect-multiple-wireless-networks/).

  // Copy 
  scp {
    from { localDir 'scripts' }
    into { remoteDir 'scripts' }
  }
  scp {
    from { localDir 'config' }
    into { remoteDir 'config' }
  }

  // TODO: install services and copy configuration
  //  cd /home/pi/scripts
  //  sudo cp device.sh /etc/init.d/device
  //  sudo chmod 755 /etc/init.d/device
  //  sudo chmod 755 voter.py 
  //  sudo update-rc.d voter defaults
  //  sudo ln voter.yaml /etc/device.yaml

  // Reboot device.
  exec 'sudo reboot'

}