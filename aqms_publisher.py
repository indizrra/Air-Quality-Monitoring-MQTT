#!/usr/bin/env python3

import paho.mqtt.client as mqtt
import json
import time
import random
import threading
from datetime import datetime
import sys

class AQMSPublisher:
    """Publisher untuk Air Quality Monitoring System"""
    
    def __init__(self, broker_host='localhost', broker_port=1883, 
                 sensor_id='sensor_001', location='floor1_roomA', qos=1):
        """
        Inisialisasi MQTT Publisher
        
        Args:
            broker_host (str): Hostname atau IP address dari MQTT Broker
            broker_port (int): Port MQTT Broker (default: 1883)
            sensor_id (str): Identifier unik untuk sensor
            location (str): Lokasi fisik sensor
            qos (int): Quality of Service level (0, 1, atau 2)
        """
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.sensor_id = sensor_id
        self.location = location
        self.qos = qos
        self.connected = False
        self.message_count = 0
        
        # Inisialisasi MQTT Client
        self.client = mqtt.Client(client_id=f"{sensor_id}_publisher")
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_publish = self._on_publish
        self.client.on_message = self._on_message
        
        # Parse location untuk struktur topic
        # Parse location FILKOM_L4_F414 -> FILKOM/L4/F414
        parts = location.split('_')

        self.building = parts[0] if len(parts) > 0 else 'UNKNOWN'
        self.floor = parts[1] if len(parts) > 1 else 'UNKNOWN'
        self.room = parts[2] if len(parts) > 2 else 'UNKNOWN'
    
    def _on_connect(self, client, userdata, flags, rc, properties=None):
        """Callback untuk connection event"""
        if rc == 0:
            self.connected = True
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Publisher {self.sensor_id} terhubung ke broker {self.broker_host}:{self.broker_port}")
        else:
            print(f"[ERROR] Gagal terhubung. Return code: {rc}")
    
    def _on_disconnect(self, client, userdata, rc, properties=None):
        """Callback untuk disconnection event"""
        self.connected = False
        if rc != 0:
            print(f"[WARNING] Unexpected disconnection. Return code: {rc}")
    
    def _on_publish(self, client, userdata, mid, properties=None):
        """Callback untuk publish confirmation"""
        pass  # Silent untuk performance
    
    def _on_message(self, client, userdata, msg):
        """Callback untuk received message"""
        pass  # Publisher tidak expect menerima message
    
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
    
    def generate_sensor_data(self, sensor_type='pm25'):
        """
        Generate simulasi data sensor
        
        Args:
            sensor_type (str): Tipe sensor ('pm25', 'temperature', 'humidity')
            
        Returns:
            dict: Data sensor yang di-generate
        """
        if sensor_type == 'pm25':
            # Simulasi PM2.5 dengan normal distribution centered di 45 (tidak sehat)
            value = max(0, random.gauss(45, 15))
            unit = 'µg/m³'
            if value < 12:
                status = 'good'
            elif value < 35.4:
                status = 'moderate'
            elif value < 55.4:
                status = 'unhealthy_for_sensitive'
            elif value < 150.4:
                status = 'unhealthy'
            else:
                status = 'very_unhealthy'
                
        elif sensor_type == 'temperature':
            # Simulasi temperature dengan daily variation
            base_temp = 25
            hour = datetime.now().hour
            daily_variation = 5 * (1 - abs(hour - 12) / 12)
            value = base_temp + daily_variation + random.uniform(-2, 2)
            unit = '°C'
            status = 'normal'
            
        elif sensor_type == 'humidity':
            # Simulasi humidity dengan normal distribution
            value = max(0, min(100, random.gauss(70, 15)))
            unit = '%'
            status = 'normal'
        else:
            raise ValueError(f"Unknown sensor type: {sensor_type}")
        
        return {
            'value': round(value, 2),
            'unit': unit,
            'status': status
        }
    
    def publish_data(self, sensor_type='pm25', interval=5):
        """
        Publish data sensor ke MQTT Broker
        
        Args:
            sensor_type (str): Tipe sensor yang akan di-publish
            interval (int): Interval publish dalam detik
        """
        topic = f"{self.building}/{self.floor}/{self.room}/sensor/{sensor_type}"
        
        try:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Mulai publish ke topic: {topic}")
            
            while self.connected:
                sensor_data = self.generate_sensor_data(sensor_type)
                
                payload = {
                    'sensor_id': self.sensor_id,
                    'location': self.location,
                    'parameter': sensor_type,
                    'value': sensor_data['value'],
                    'unit': sensor_data['unit'],
                    'timestamp': datetime.now().isoformat() + 'Z',
                    'status': sensor_data['status']
                }
                
                # Publish ke broker dengan specified QoS
                result = self.client.publish(
                    topic=topic,
                    payload=json.dumps(payload),
                    qos=self.qos
                )
                
                self.message_count += 1
                
                if self.message_count % 10 == 0:  # Print setiap 10 message
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {self.sensor_id}: Published {self.message_count} messages (last: {sensor_data['value']} {sensor_data['unit']})")
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Publisher stopped by user")
        except Exception as e:
            print(f"[ERROR] Publishing error: {e}")
    
    def publish_multi_sensors(self, sensors=['pm25', 'temperature', 'humidity'], interval=5):
        """
        Publish multiple sensor types secara concurrent
        
        Args:
            sensors (list): List sensor types to publish
            interval (int): Interval antara publish
        """
        threads = []
        
        for sensor in sensors:
            thread = threading.Thread(
                target=self.publish_data,
                args=(sensor, interval),
                daemon=True
            )
            thread.start()
            threads.append(thread)
            time.sleep(0.5)  # Stagger thread starts
        
        try:
            for thread in threads:
                thread.join()
        except KeyboardInterrupt:
            print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Multi-sensor publishing stopped")


def main():
    """Main function untuk test publisher"""
    
    # Configuration
    BROKER_HOST = 'localhost'
    BROKER_PORT = 1883
    
    # Test dengan berbagai configuration
    publishers = [
        {
            'sensor_id': 'sensor_FILKOM_L4_F414',
            'location': 'FILKOM_L4_F414',
            'qos': 0
        },
        {
            'sensor_id': 'sensor_FILKOM_L3_F313',
            'location': 'FILKOM_L3_F313',
            'qos': 1
        },
        {
            'sensor_id': 'sensor_FILKOM_L2_F28',
            'location': 'FILKOM_L2_F28',
            'qos': 2
        }
    ]
    
    publisher_instances = []
    
    print("=" * 70)
    print("Air Quality Monitoring System - MQTT Publisher")
    print("=" * 70)
    print(f"Target Broker: {BROKER_HOST}:{BROKER_PORT}")
    print("=" * 70)
    
    # Start publishers
    for config in publishers:
        pub = AQMSPublisher(
            broker_host=BROKER_HOST,
            broker_port=BROKER_PORT,
            sensor_id=config['sensor_id'],
            location=config['location'],
            qos=config['qos']
        )
        
        if pub.connect():
            publisher_instances.append(pub)
            # Start publishing dalam separate thread
            thread = threading.Thread(
                target=pub.publish_multi_sensors,
                args=(['pm25', 'temperature', 'humidity'], 5),
                daemon=True
            )
            thread.start()
            time.sleep(1)
        else:
            print(f"Failed to start publisher: {config['sensor_id']}")
    
    # Keep running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nShutting down publishers...")
        for pub in publisher_instances:
            pub.disconnect()
        print("All publishers stopped")


if __name__ == '__main__':
    main()
