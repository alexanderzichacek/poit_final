# Záverečné zadanie z predmetu POIT

Cieľom zadanie je vzdialený monitoring podľa vybraného senzoru. V tomto projekte budeme pracovať so zariadením RaspberryPi 2B a senzorom DHT11.

## Príprava RaspberryPi

1. Inštalácia python3

```bash
  sudo apt-get install python3
```

2. Inštalácia potrebných knižníc

```bash
  sudo apt-get install dht11
```

## Spustenie web servera na RaspberryPi

1. Stiahnutie repozitára

a) pomocou HTTPS

```bash
  git clone https://github.com/alexanderzichacek/poit_zaverecne.git
```

b) pomocou SSH

```bash
  git clone git@github.com:alexanderzichacek/poit_zaverecne.git
```

2. Spustenie web servera

```bash
  cd poit_zaverecne
  python3 web_server.py
```

## Automatické spustenie web servera ako proces na pozadí systému

Ak chceme aby sa nám server spustil automaticky pri spustení RaspberryPi potrebujeme vytvorit service

1. Vytvorenie service

```bash
  cd ~
  sudo vim /etc/systemd/system/web_server.service
```

2. Obsah service

```bash
[Unit]
Description=Python Web Server
After=network.target

[Service]
User=pi
WorkingDirectory=/home/pi/Desktop/poit_zaverecne
ExecStart=/usr/bin/python3 /home/pi/Desktop/poit_zaverecne/web_server.py
Restart=always

[Install]
WantedBy=multi-user.target
```

pre WorkingDirectory a ExecStart zadefinujeme cestu k serveru na RaspberryPi podľa toho kde ho máme uložený a zároveň pre ExecStart zadefinujeme aj cestu k dependenciám python3

3. Kontrola service či je spustená

```bash
  systemctl status web_server
```

4. Reštart service

```bash
  sudo systemctl restart web_server
```

## Autor

- [@alexanderzichacek](https://github.com/alexanderzichacek)
