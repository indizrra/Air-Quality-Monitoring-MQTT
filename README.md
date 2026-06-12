# Air Quality Monitoring System (AQMS) using MQTT

Sistem ini merupakan simulasi monitoring kualitas udara berbasis MQTT menggunakan Python dan Mosquitto Broker.

Sistem menggunakan konsep publish-subscribe:
- Publisher → mengirim data sensor
- Mosquitto Broker → mengatur distribusi pesan MQTT
- Subscriber → menerima data berdasarkan topic yang dipilih

Data sensor yang digunakan:
- PM2.5
- Temperature
- Humidity

---

## Persiapan

Pastikan Python dan Mosquitto MQTT Broker sudah terinstall.

Install library MQTT:

```bash
pip install paho-mqtt
```

Jalankan Mosquitto Broker pada:

```
Host : localhost
Port : 1883
```

---

# Cara Menjalankan Program

Program dijalankan menggunakan beberapa terminal.

## Terminal 1: Menjalankan Publisher

Jalankan:

```bash
python aqms_publisher.py
```

Publisher akan menjalankan tiga sensor:

| Sensor | Lokasi | QoS |
|---|---|---|
| sensor_FILKOM_L4_F414 | FILKOM L4 F414 | QoS 0 |
| sensor_FILKOM_L3_F313 | FILKOM L3 F313 | QoS 1 |
| sensor_FILKOM_L2_F28 | FILKOM L2 F28 | QoS 2 |

Publisher akan mulai mengirim data:

```
PM2.5
Temperature
Humidity
```

---

# Menjalankan Subscriber

Buka terminal baru untuk menjalankan subscriber.

Format command:

```bash
python aqms_subscriber.py <nomor_skenario>
```

Contoh:

```bash
python aqms_subscriber.py 1
```

---

## Skenario 1: Basic Communication

Menguji komunikasi dasar MQTT antara satu publisher dan satu subscriber.

Jalankan:

```bash
python aqms_subscriber.py 1
```

Topic:

```
FILKOM/L4/F414/sensor/pm25
```

---

## Skenario 2: QoS Comparison

Membandingkan pengiriman data menggunakan QoS 0, QoS 1, dan QoS 2.

Jalankan:

```bash
python aqms_subscriber.py 2
```

Topic:

```
FILKOM/L4/F414/sensor/pm25
FILKOM/L3/F313/sensor/pm25
FILKOM/L2/F28/sensor/pm25
```

---

## Skenario 3: Multi-Sensor Monitoring

Menguji penerimaan banyak data sensor secara bersamaan.

Jalankan:

```bash
python aqms_subscriber.py 3
```

Topic:

```
FILKOM/L4/F414/sensor/pm25
FILKOM/L4/F414/sensor/temperature
FILKOM/L4/F414/sensor/humidity

FILKOM/L3/F313/sensor/pm25
FILKOM/L3/F313/sensor/temperature
FILKOM/L3/F313/sensor/humidity
```

---

## Skenario 4: Single-Level Wildcard

Menguji penggunaan wildcard satu tingkat (+).

Jalankan:

```bash
python aqms_subscriber.py 4
```

Topic:

```
FILKOM/+/+/sensor/pm25
```

Subscriber akan menerima semua data PM2.5 dari seluruh lantai dan ruangan.

---

## Skenario 5: Multi-Level Wildcard

Menguji penggunaan wildcard banyak tingkat (#).

Jalankan:

```bash
python aqms_subscriber.py 5
```

Topic:

```
FILKOM/#
```

Subscriber akan menerima seluruh data sensor dari semua lokasi.

---

# Contoh Pengujian Banyak Terminal

Terminal 1:

```bash
python aqms_publisher.py
```

Terminal 2:

```bash
python aqms_subscriber.py 1
```

Terminal 3:

```bash
python aqms_subscriber.py 2
```

Terminal 4:

```bash
python aqms_subscriber.py 3
```

Terminal 5:

```bash
python aqms_subscriber.py 4
```

Terminal 6:

```bash
python aqms_subscriber.py 5
```

---

# Menghentikan Program

Tekan:

```bash
CTRL + C
```

pada terminal yang ingin dihentikan.