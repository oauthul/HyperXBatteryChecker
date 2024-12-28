# Currently supported devices: "HyperX Cloud Stinger 2 Wireless"
import hid
from time import sleep

def find_path(vendor_id, product_id):
    target_device = None
    max_usage = 0
    max_usage_page = 0
    try:
        for device in hid.enumerate():
            if device['vendor_id'] == vendor_id and device['product_id'] == product_id:
                usage_page = device.get('usage_page', 0)
                usage = device.get('usage', 0)
                if usage_page > max_usage_page and usage > max_usage or (usage_page == max_usage_page and usage > max_usage) or (usage_page > max_usage_page and usage == usage_page):
                    # The path with the highest value for "usage_page" and "usage" usually contains the battery level.
                    max_usage_page, max_usage = usage_page, usage 
                    target_device = device
        print(f'Found path of highest usage page and usage:\nPath: "{target_device['path']}"\nUsage Page: "{usage_page}"\nUsage: "{usage}"')
        print('Using the path to load device..')
        # Returns the path of the highest usage_page and usage values.
        return target_device['path'] if target_device else None
    except TypeError as e:
        print(f'Unable to get path: "{e}". Is the Vendor ID and the Product ID valid?')

def write():
    # Performs a write operation to get the battery level.
    print('Performing HID Write operation..')
    data = [0x06, 0xFF, 0xBB, 0x02] # Battery level command, 0x06 is the report ID.
    print(f'Battery level command for "{device_name}": {[hex(x) for x in data]}')
    print('Sending battery level command..')
    write = h.write(data)
    # A failed write operation will result in a "-1" error code. "0" is successful.
    if write < 0:
        h.close()
        print(f'Failed to write. Return value: "{write}". HIDAPI response: "{h.error()}"')
        return 1
    else:
        print(f'Successful write. Return value: "{write}". HIDAPI response: "{h.error()}"')
        return 0
    
def read():
    # Wait to ensure the data was written successfully.
    print('Waiting 0.1 seconds until read..')
    sleep(0.1)
    # Read within 64 buffers, without block, to ensure the script doesn't hang when reading.
    print('Reading data within 64 buffers with non-block mode..')
    read = h.read(64)
    # If a read value is found, print the result.
    if read:
        print([hex(x) for x in read])
    else:
        print('Failed to read data..')
        # If the script fails to read any data, it will automatically close the connection and raise an Exception to ensure it does not continue the script.
        h.close()
        raise Exception('Unable to read data. Stopping script.')
    # Globally call the variable to allow other functions to access it.
    global battery_level
    # For the Cloud Stinger 2 Wireless, the battery percentage is in the 8th hex.
    battery_level = read[7]
    print(f'Battery level hex: {hex(read[7])}')
    print(f'Battery percentage: {battery_level}%')
    return battery_level

# Initial connection
def init(refresh=False):
    VENDOR_ID = 0x03F0 # HP, Inc. VID
    PRODUCT_ID = 0x0D93 # HyperX Cloud Stinger 2 Wireless PID
    global h
    h = hid.device()
    # Attempts a connection.
    print('Attempting to open connection with device..')
    try:
        # Tries to open the path of the "find_path" function.
        h.open_path(find_path(VENDOR_ID, PRODUCT_ID))
        if h:
            print('Successful initial connection to device.')
            global device_name
            device_name = str(h.get_product_string())
            # If the name of the device is the same as a supported device, it will continue.
            if device_name == "HyperX Cloud Stinger 2 Wireless":
                print(f'Supported device, received name: "{device_name}"')
                print(f'Manufacturer: "{h.get_manufacturer_string()}",  ' + hex(VENDOR_ID))
                print(f'Serial Number: "{h.get_serial_number_string()}", ' + hex(PRODUCT_ID))
                print('Setting non-block mode to 1 (enabled)')
                h.set_nonblocking(1)
                # Executes the write function.
                if write() > 0:
                    print('Writing failed, stopping script..')
                    h.close()
                else:
                    print('Writing operation success, reading response.')
                    read()
                    print(f'Closing connection to: "{device_name}"')
                    h.close()
                    input(f'Script finished, connection closed, initial battery level is {battery_level}%.')
                    if refresh == True:
                        return battery_level
            else:
                print(f'Incorrect device connected, given: "{device_name}" but expected: "HyperX Cloud Stinger 2 Wireless", stopping script..')
    except OSError:
        print('Failed to open the path, stopping script..')
    except TypeError as e:
        print(f'Failed to get path: "{e}". Check your Product ID and Vendor ID.')

if __name__ == '__main__':
    init(refresh=False)
