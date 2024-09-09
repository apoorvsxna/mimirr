This has been abandoned as the latency involved here is not acceptable for using phone as gamepad (even if [socket.io](https://socket.io/) is used). Although there are plans to build this from scratch, using native Java for Android, sometime in the future.

# Mimir
A multi-purpose remote control utility to control your PC using another device such as a phone, or even another PC.

### Setup and Usage-
- You need Node.js on the host device for Mimir to be functional. [Download Node.js](https://nodejs.org/en/download/current "Download Node.js") if you don't have it.
- Download the [latest release](https://github.com/apoorvsxna/Mimir/releases/ "latest Mimir release") on the device you wish to control, and extract the files.
- Run `install-packages.bat` to install dependencies.
- Run `start.bat` to start the server.
- Get the local IP address of the host PC. You will be asked to enter it when you use any of the utilities.
- To get the IP address on Windows, you can enter `ipconfig` in the command prompt and find it listed next to the 'IPv4 Address' property
 (**Note:** The local IP address of the same device may vary on different networks.)
- Now download the application on the device to be used as a remote control and open `index.html`.
(**Note:** Make sure both devices are on the same local network.)
- Click/tap on the utility you want to use.
- Enter your IP address when prompted and you're all set.
- Run `stop.bat` to stop the server when you're done.

### Demo Video-
- Here's a demonstration of the usage- [Demo Video](https://youtu.be/jvd2k8i5Yt4 "Video")
