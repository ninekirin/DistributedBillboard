# Distributed Billboard

Distributed Billboard is a decentralized application that allows nodes to update images remotely.

## Installation

1. Install [Python](https://www.python.org/downloads/).
2. Clone the repository.

```bash
git clone https://github.com/ninekirin/DistributedBillboard.git
```

3. Install the required packages. You must be in the root directory of the repository.

```bash
pip install -r requirements.txt
```

4. Check if the tkinter package is installed.

```bash
python -m tkinter
```

5. Run the start script.

```bash
python starter.py
```

## Usage

In the terminal, you can see the log of the application. You can see the current image and detailed error messages in the log.

In the main window, you can see the current image. You can switch to the next image by clicking your left mouse button on the image.

To switch between the fullscreen and windowed mode, press `F11`. Press `ESC` to exit the fullscreen mode.

In the billboard window, press `m` to open the management window. Press `m` again to close the menu. You can also press `q` to exit the application.

In the management window, you can see the list of nodes and their status, where you can add a new node, remove a node, update the image, change the interface address and port of the current node, and edit other settings in the "Other" tab. Press `ESC` to close the management window.

## Configuration File

The configuration file is located in the root directory of the repository. You can edit the configuration file to change the settings of the application.

```yaml
# Background color of the main window, in hexadecimal format or color name.
background_color: skyblue
# The address of the current node, currently supports only IPv4 addresses.
endpoint_ipaddr: 0.0.0.0
# The port of the current node.
endpoint_port: 6000
# If the application should be in fullscreen mode at startup.
fullscreen: true
# The interval in seconds to switch to the next image.
image_switch_interval: 15
# The node list, each node should have an address and a port like 'http://<address>:<port>'.
nodes: []
# The interval in seconds to ping the nodes.
ping_interval: 15
# The timeout in seconds to ping the nodes.
ping_timeout: 1
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
