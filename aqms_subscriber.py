#!/usr/bin/env python3

import paho.mqtt.client as mqtt
import json
import time
from datetime import datetime
from collections import defaultdict
import sys

class AQMSSubscriber:
    """Subscriber untuk Air Quality Monitoring System"""
    
    def __init__(self, broker_host='localhost', broker_port=1883, 
                 subscriber_id='monitor_001'):
        """
        Inisialisasi MQTT Subscriber
        
        Args:
            broker_host (str): Hostname atau IP address dari MQTT Broker
            broker_port (int): Port MQTT Broker (default: 1883)
            subscriber_id (str): Identifier unik untuk subscriber
        """
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.subscriber_id = subscriber_id
        self.connected = False
        
        # Statistics tracking
        self.message_count = defaultdict(int)
        self.received_data = {}
        self.start_time = None
        
        # Inisialisasi MQTT Client
        self.client = mqtt.Client(client_id=f"{subscriber_id}")
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message
        self.client.on_subscribe = self._on_subscribe
    
    def _on_connect(self, client, userdata, flags, rc, properties=None):
        """Callback untuk connection event"""
        if rc == 0:
            self.connected = True
            self.start_time = datetime.now()
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Subscriber {self.subscriber_id} terhubung ke broker {self.broker_host}:{self.broker_port}")
        else:
            print(f"[ERROR] Gagal terhubung. Return code: {rc}")
    
    def _on_disconnect(self, client, userdata, rc, properties=None):
        """Callback untuk disconnection event"""
        self.connected = False
        if rc != 0:
            print(f"[WARNING] Unexpected disconnection. Return code: {rc}")
    
    def _on_subscribe(self, client, userdata, mid, granted_qos, properties=None):
        """Callback untuk subscription confirmation"""
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Subscription confirmed")
    
    def _on_message(self, client, userdata, msg):
        """Callback untuk received message"""
        try:
            # Decode payload
            payload = json.loads(msg.payload.decode('utf-8'))
            
            # Track message
            sensor_id = payload.get('sensor_id', 'unknown')
            parameter = payload.get('parameter', 'unknown')
            self.message_count[f"{sensor_id}:{parameter}"] += 1
            
            # Store latest data
            key = f"{payload.get('location', 'unknown')}:{parameter}"
            self.received_data[key] = {
                'value': payload.get('value'),
                'unit': payload.get('unit'),
                'status': payload.get('status'),
                'timestamp': payload.get('timestamp'),
                'sensor_id': sensor_id
            }
            
            # Display received message
            self._display_message(msg.topic, payload)
            
        except json.JSONDecodeError:
            print(f"[ERROR] Invalid JSON payload on topic {msg.topic}: {msg.payload}")
        except Exception as e:
            print(f"[ERROR] Error processing message: {e}")
    
    def _display_message(self, topic, payload):
        """
        Tampilkan pesan yang diterima dengan format yang readable
        
        Args:
            topic (str): MQTT topic
            payload (dict): Parsed JSON payload
        """
        location = payload.get('location', 'N/A')
        parameter = payload.get('parameter', 'N/A')
        value = payload.get('value', 'N/A')
        unit = payload.get('unit', '')
        status = payload.get('status', 'N/A')
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {location:20} | {parameter:15} = {value:8} {unit:6} [{status:20}]")
    
    def connect(self):
        """Connect ke MQTT Broker"""
        try:
            self.client.connect(self.broker_host, self.broker_port, keepalive=60)
            self.client.loop_start()
            time.sleep(1)  # Wait untuk connection complete
        except Exception as e:
            print(f"[ERROR] Failed to connect: {e}")
            return False
        return True
    
    def disconnect(self):
        """Disconnect dari MQTT Broker"""
        self.client.loop_stop()
        self.client.disconnect()
    
    def subscribe(self, topics, qos=1):
        """
        Subscribe ke satu atau lebih topic
        
        Args:
            topics (str or list): Topic atau list of topics untuk subscribe
            qos (int): Quality of Service level (default: 1)
        """
        if isinstance(topics, str):
            topics = [topics]
        
        for topic in topics:
            result = self.client.subscribe(topic, qos=qos)
            if result[0] != mqtt.MQTT_ERR_SUCCESS:
                print(f"[ERROR] Failed to subscribe to {topic}: {result[0]}")
            else:
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Subscribed to: {topic}")
    
    def print_statistics(self):
        """Print statistik pesan yang diterima"""
        print("\n" + "=" * 70)
        print("STATISTIK MONITORING")
        print("=" * 70)
        
        if self.start_time:
            elapsed = (datetime.now() - self.start_time).total_seconds()
            print(f"Waktu running: {elapsed:.1f} detik")
        
        print(f"Total data points: {sum(self.message_count.values())}")
        print(f"Unique sensors: {len(set([k.split(':')[0] for k in self.message_count.keys()]))}")
        
        print("\nData per sensor:")
        for key, count in sorted(self.message_count.items()):
            sensor_id, param = key.split(':')
            print(f"  {sensor_id:30} - {param:15}: {count:5} messages")
        
        print("\nLatest readings:")
        for key, data in sorted(self.received_data.items()):
            location, param = key.split(':')
            print(f"  {location:25} - {param:15}: {data['value']:8.2f} {data['unit']} [{data['status']}]")
        
        print("=" * 70)


def skenario_1_basic_communication():
    """Skenario 1: Komunikasi Dasar Publisher-Subscriber"""
    print("\n" + "=" * 70)
    print("SKENARIO 1: Komunikasi Dasar Publisher-Subscriber")
    print("FILKOM L4 F414 (QoS 0)")
    print("=" * 70)
    
    subscriber = AQMSSubscriber(subscriber_id='subscriber_skenario1')
    
    if subscriber.connect():
        # Subscribe ke single topic FILKOM L4 F414
        subscriber.subscribe('FILKOM/L4/F414/sensor/pm25', qos=1)
        
        print("\nWaiting for messages... (Press Ctrl+C to stop)")
        print("-" * 70)
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopped by user")
            subscriber.print_statistics()
            subscriber.disconnect()


def skenario_2_qos_comparison():
    """Skenario 2: Perbandingan QoS"""
    print("\n" + "=" * 70)
    print("SKENARIO 2: Perbandingan QoS Levels")
    print("=" * 70)
    
    subscriber = AQMSSubscriber(subscriber_id='subscriber_skenario2')
    
    if subscriber.connect():
        # Subscribe ke semua sensor FILKOM dengan berbeda QoS
        # L4 F414 (QoS 0), L3 F313 (QoS 1), L2 F28 (QoS 2)
        subscriber.subscribe([
            'FILKOM/L4/F414/sensor/pm25',
            'FILKOM/L3/F313/sensor/pm25',
            'FILKOM/L2/F28/sensor/pm25'
        ], qos=1)
        
        print("\nWaiting for messages from different QoS levels...")
        print("(Publishers: L4/F414=QoS0, L3/F313=QoS1, L2/F28=QoS2)")
        print("-" * 70)
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopped by user")
            subscriber.print_statistics()
            subscriber.disconnect()


def skenario_3_multi_sensor():
    """Skenario 3: Multi-Sensor Monitoring"""
    print("\n" + "=" * 70)
    print("SKENARIO 3: Multi-Sensor Multi-Topic")
    print("=" * 70)
    
    subscriber = AQMSSubscriber(subscriber_id='subscriber_skenario3')
    
    if subscriber.connect():
        # Subscribe ke semua sensor dari semua ruangan
        subscriber.subscribe([
            'FILKOM/L4/F414/sensor/pm25',
            'FILKOM/L4/F414/sensor/temperature',
            'FILKOM/L4/F414/sensor/humidity',
            'FILKOM/L3/F313/sensor/pm25',
            'FILKOM/L3/F313/sensor/temperature',
            'FILKOM/L3/F313/sensor/humidity'
        ], qos=1)
        
        print("\nMonitoring multiple sensors...")
        print("-" * 70)
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopped by user")
            subscriber.print_statistics()
            subscriber.disconnect()


def skenario_4_single_level_wildcard():
    """Skenario 4: Single-Level Wildcard (+)"""
    print("\n" + "=" * 70)
    print("SKENARIO 4: Single-Level Wildcard (+)")
    print("=" * 70)
    
    subscriber = AQMSSubscriber(subscriber_id='subscriber_skenario4')
    
    if subscriber.connect():
        # Subscribe ke PM2.5 dari semua ruangan di semua lantai
        # Pattern: FILKOM/+/+/sensor/pm25
        topic = 'FILKOM/+/+/sensor/pm25'
        subscriber.subscribe(topic, qos=1)
        
        print(f"\nSubscribed to: {topic}")
        print("Ini akan match:")
        print("  - FILKOM/L4/F414/sensor/pm25")
        print("  - FILKOM/L3/F313/sensor/pm25")
        print("  - FILKOM/L2/F28/sensor/pm25")
        print("-" * 70)
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopped by user")
            subscriber.print_statistics()
            subscriber.disconnect()


def skenario_5_multi_level_wildcard():
    """Skenario 5: Multi-Level Wildcard (#)"""
    print("\n" + "=" * 70)
    print("SKENARIO 5: Multi-Level Wildcard (#)")
    print("=" * 70)
    
    subscriber = AQMSSubscriber(subscriber_id='subscriber_skenario5')
    
    if subscriber.connect():
        # Subscribe ke SEMUA topic dari FILKOM
        topic = 'FILKOM/#'
        subscriber.subscribe(topic, qos=1)
        
        print(f"\nSubscribed to: {topic}")
        print("Ini akan match SEMUA subtopic dari FILKOM:")
        print("  - FILKOM/L4/F414/sensor/pm25")
        print("  - FILKOM/L4/F414/sensor/temperature")
        print("  - FILKOM/L4/F414/sensor/humidity")
        print("  - FILKOM/L3/F313/sensor/pm25")
        print("  - FILKOM/L3/F313/sensor/temperature")
        print("  - FILKOM/L3/F313/sensor/humidity")
        print("  - FILKOM/L2/F28/sensor/pm25")
        print("  - FILKOM/L2/F28/sensor/temperature")
        print("  - FILKOM/L2/F28/sensor/humidity")
        print("-" * 70)
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopped by user")
            subscriber.print_statistics()
            subscriber.disconnect()


def main():
    """Main function untuk memilih skenario"""
    if len(sys.argv) < 2:
        print("Usage: python aqms_subscriber_FILKOM.py [skenario]")
        print("\nAvailable scenarios:")
        print("  1 - Basic Communication (L4 F414)")
        print("  2 - QoS Comparison (L4 F414, L3 F313, L2 F28)")
        print("  3 - Multi-Sensor Monitoring (L4 F414, L3 F313)")
        print("  4 - Single-Level Wildcard (FILKOM/+/+/sensor/pm25)")
        print("  5 - Multi-Level Wildcard (FILKOM/#)")
        return
    
    skenario = sys.argv[1]
    
    if skenario == '1':
        skenario_1_basic_communication()
    elif skenario == '2':
        skenario_2_qos_comparison()
    elif skenario == '3':
        skenario_3_multi_sensor()
    elif skenario == '4':
        skenario_4_single_level_wildcard()
    elif skenario == '5':
        skenario_5_multi_level_wildcard()
    else:
        print(f"Unknown scenario: {skenario}")


if __name__ == '__main__':
    main()