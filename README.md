# eDrive

Software for home automatization. Master device controls group of slave devices connected via serial bus.

The Master device runs python script periodically launched by task scheduller, usually crontab on linux.
Script sends command addressed to the slave device by serial bus and reads response, if needed.
As slave devices are used hw based on [PICAXE](www.picaxe.com) chips, which are able to do simple operations as read values from sensors, switch on/off relays or rise signals for stepper drivers, etc.


## current status
Currently, as just presented, system is used for recording temperature values in periodic time interval.
Script `main.py` is launched every 15min, using ctontab service. Reads four temperature values from sensors on serial bus and writes them to CSV file.
Master device, placed into LAN network, hosts apache server. Apache allows to show recorded values to every host in LAN network, using PHP to load CSV file into `apache/index.php`.

### requirements
Master device:<br>
- python3, modules `serial` , `lxml`<br>
- apache2 server<br>
- PHP 7 +<br>

Slave devices; sw for flash firmware into chips:<br>
- [linaxepad](https://picaxe.com/software/picaxe/axepad/) for linux<br>
- or [VS Code](https://picaxe.com/software/third-party/visual-studio-code/) for all platforms<br>
- or [PICAXE Editor 6](https://picaxe.com/software/picaxe/picaxe-editor-6/) for win<br>