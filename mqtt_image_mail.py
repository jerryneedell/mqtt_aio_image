# Example of using the MQTT client class to subscribe to a feed and print out
# any changes made to the feed.  Edit the variables below to configure the key,
# username, and feed to subscribe to for changes.

# Import standard python modules.
import sys
import binascii
from PIL import Image
import os
# Import Adafruit IO MQTT client.
from Adafruit_IO import MQTTClient

# Import smtplib for the actual sending function.
import smtplib

# Here are the email package modules we'll need.
from email.message import EmailMessage

aio_username = os.environ.get("ADAFRUIT_IO_USERNAME")
aio_key = os.environ.get("ADAFRUIT_IO_KEY")

# Set to the ID of the feed to subscribe to for updates.
FEED_ID = 'esp32s3revtft'


# Define callback functions which will be called when certain events happen.
def connected(client):
    # Connected function will be called when the client is connected to Adafruit IO.
    # This is a good place to subscribe to feed changes.  The client parameter
    # passed to this function is the Adafruit IO MQTT client so you can make
    # calls against it easily.
    print('Connected to Adafruit IO!  Listening for {0} changes...'.format(FEED_ID))
    # Subscribe to changes on a feed named DemoFeed.
    client.subscribe(FEED_ID)

def subscribe(client, userdata, mid, granted_qos):
    # This method is called when the client subscribes to a new feed.
    print('Subscribed to {0} with QoS {1}'.format(FEED_ID, granted_qos[0]))

def disconnected(client):
    # Disconnected function will be called when the client disconnects.
    print('Disconnected from Adafruit IO!')
    sys.exit(1)

def message(client, feed_id, payload):
    # Message function will be called when a subscribed feed has a new value.
    # The feed_id parameter identifies the feed, and the payload parameter has
    # the new value.
#    print('Feed {0} received new value: {1}'.format(feed_id, payload))
    print('Feed {0} received new image'.format(feed_id))
    jpeg_image = binascii.a2b_base64(payload)
    with open("test.jpeg", "wb") as file:
        file.write(jpeg_image)
#    new_image=Image.open('test.jpeg')
#    new_image.show()
    # Create the container email message.
    msg = EmailMessage()
    msg['Subject'] = 'image test'
    icloud_username = os.environ.get("ICLOUD_EMAIL")
    recipient = os.environ.get("IMAGE_RECIPIENT")
    msg['From'] = icloud_username
    msg['To'] = recipient
    msg.preamble = 'You will not see this in a MIME-aware mail reader.\n'

    msg.add_attachment(jpeg_image, maintype='image',
                             subtype='jpeg')

    try:
        # Connect to the iCloud SMTP server and start a secure session
        with smtplib.SMTP('smtp.mail.me.com', 587) as server:
            server.starttls()
            # Log in with your Apple ID and app-specific password
            username = os.environ.get("AIOIMAGE_USERNAME")
            password = os.environ.get("AIOIMAGE_PASSWORD")
            server.login(username, password)
            # Send the message
            server.send_message(msg)
            print("Email sent successfully!")

    except smtplib.SMTPException as e:
        print(f"Error: Unable to send email. {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


# Create an MQTT client instance.
client = MQTTClient(aio_username, aio_key)

# Setup the callback functions defined above.
client.on_connect    = connected
client.on_disconnect = disconnected
client.on_message    = message
client.on_subscribe  = subscribe

# Connect to the Adafruit IO server.
client.connect()

# Start a message loop that blocks forever waiting for MQTT messages to be
# received.  Note there are other options for running the event loop like doing
# so in a background thread--see the mqtt_client.py example to learn more.
client.loop_blocking()



