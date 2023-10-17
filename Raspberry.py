import RPi.GPIO as GPIO
import time
import socket
import tkinter as tk
from threading import Thread

# Define the GPIO pins for TRIG (trigger) and ECHO (echo) of the ultrasonic sensor
TRIG_PIN = 19
ECHO_PIN = 20
SENSOR_HEIGHT_ABOVE_WATER = 14


# Define the GPIO pins
ENA = 17
IN1 = 18
IN2 = 27

GPIO.setmode(GPIO.BCM)
# Set up the GPIO pins
GPIO.setup(ENA, GPIO.OUT)
GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)

# Create PWM object
pwm = GPIO.PWM(ENA, 100)  # 100 Hz frequency

# Start the PWM with 0% duty cycle (stopped)
pwm.start(0)




# Speed of sound in cm/s (approximately 34300 cm/s at room temperature)
SPEED_OF_SOUND = 34300

# Raspberry Pi's IP address and port to listen on
host = '192.168.78.69'  # Listen on all available network interfaces
port = 12345  # Use the same port as on the Arduino

# Create a socket object
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the address and port
server_socket.bind((host, port))

# Listen for incoming connections
server_socket.listen(5)
# Initialize global variables for sensor data
soilMoisture = 0
airQuality = 0
distance = 0
depth = 0
volume = 0
amount = 0


# Create a function to continuously listen for incoming connections
def listen_for_connections():
    print("Listening for incoming connections...")
    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Accepted connection from {client_address}")
        data = client_socket.recv(1024).decode()
        print(f"Received data: {data}")
        process_arduino_data(data)
        client_socket.close()

# Create a thread to run the network communication
network_thread = Thread(target=listen_for_connections)
network_thread.daemon = True
network_thread.start()

# Create a function to update the GUI with sensor readings
def update_gui():
    # Update the GUI elements with sensor readings
    distance_var.set(f"Distance: {distance:.2f} cm")
    depth_var.set(f"Depth: {depth:.2f} cm")
    volume_var.set(f"Volume Used: {volume:.2f} cubic cm")
    bill_var.set(f"Bill: {amount:.2f} Rs")
    soil_moisture_var.set(f"Soil Moisture: {soilMoisture}")
    air_quality_var.set(f"Air Quality: {airQuality}")
    root.after(1000, update_gui)  # Update the GUI every second

# Create a function to setup the ultrasonic sensor
def setup_sensor():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(TRIG_PIN, GPIO.OUT)
    GPIO.setup(ECHO_PIN, GPIO.IN)

# Create a function to measure distance using the ultrasonic sensor
def measure_distance():
    # (The measure_distance function from your original code here)
    GPIO.output(TRIG_PIN, GPIO.LOW)
    time.sleep(0.1)

    GPIO.output(TRIG_PIN, GPIO.HIGH)
    time.sleep(0.00001)
    GPIO.output(TRIG_PIN, GPIO.LOW)

    while GPIO.input(ECHO_PIN) == 0:
        pulse_start = time.time()

    while GPIO.input(ECHO_PIN) == 1:
        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * SPEED_OF_SOUND / 2  # Calculate distance in cm
    return distance


# Create a function to calculate depth from distance
def depth_from_distance(distance):
    # (The depth_from_distance function from your original code here)
    # Assuming water has a similar speed of sound as air (approx. 34300 cm/s)
    # and that distance is measured from the sensor to the water surface
    # Convert the distance to depth assuming the sensor is placed above the water
    depth = 0
    if distance > 0:
        depth = SENSOR_HEIGHT_ABOVE_WATER-distance
    return depth


# Create a function to calculate volume left
def volume_left(depth):
    initial_volume=991.847
    new_volume=0
    net_volume=0
    if depth>0:
        new_volume=3.14*4.75*4.75*depth
        net_volume=initial_volume-new_volume
    return net_volume



# Create a function to calculate the bill
def bill(net_volume):
    # (The bill function from your original code here)
    rate=0.2
    bill_amount=rate*net_volume
    return bill_amount


# Create a function to process data from the Arduino
def process_arduino_data(data):
    global soilMoisture, airQuality, distance, depth, volume, amount

    values = data.split(",")
    if len(values) == 2:
        soilMoisture = int(values[0])
        airQuality = int(values[1])

        # Process sensor data and update GUI
        setup_sensor()
        distance = measure_distance()
        depth = depth_from_distance(distance)
        volume = volume_left(depth)
        amount = bill(volume)



def turn_on_pump():
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    pwm.ChangeDutyCycle(50)  # 50% speed
    status_label.config(text="Pump turned on.")

# Function to turn off the pump
def turn_off_pump():
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW)
    pwm.ChangeDutyCycle(0)  # 0% speed
    status_label.config(text="Pump turned off.")
    
    
    
# Initialize the GUI
root = tk.Tk()
root.title("Sensor Data and Billing")

# Create Tkinter variables to display sensor data
soil_moisture_var = tk.StringVar()
air_quality_var = tk.StringVar()
distance_var = tk.StringVar()
depth_var = tk.StringVar()
volume_var = tk.StringVar()
bill_var = tk.StringVar()

# Create labels to display sensor data
distance_label = tk.Label(root, textvariable=distance_var)
depth_label = tk.Label(root, textvariable=depth_var)
volume_label = tk.Label(root, textvariable=volume_var)
bill_label = tk.Label(root, textvariable=bill_var)
soil_moisture_label = tk.Label(root, textvariable=soil_moisture_var)
air_quality_label = tk.Label(root, textvariable=air_quality_var)

# Pack the labels in the GUI
distance_label.pack()
depth_label.pack()
volume_label.pack()
bill_label.pack()
soil_moisture_label.pack()
air_quality_label.pack()




on_button = tk.Button(root, text="Turn On Pump", command=turn_on_pump)
off_button = tk.Button(root, text="Turn Off Pump", command=turn_off_pump)
status_label = tk.Label(root, text="Pump is off")

# Arrange the widgets in the window
on_button.pack()
off_button.pack()
status_label.pack()




# Start the GUI event loop
try:
	root.after(1000, update_gui)  # Start updating the GUI every second
	root.mainloop()
except KeyboardInterrupt:
    print("Exiting the control script.")
    
finally:
    # Cleanup and cleanup GPIO settings
    GPIO.cleanup()