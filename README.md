# Air Quality Monitoring System (AQMS) using MQTT


**Nama:** Sekar Indriani Dzakirah  
**NIM:** 235150300111039  
**Program Studi:** Teknik Komputer  
**Fakultas:** Fakultas Ilmu Komputer  
**Universitas:** Universitas Brawijaya  

**Mata Kuliah:** Cyber Physical System  
**Proyek:** Implementasi MQTT pada Air Quality Monitoring System (AQMS)

---

# Deskripsi Project

Sistem ini merupakan simulasi monitoring kualitas udara berbasis MQTT menggunakan Python dan Mosquitto Broker.

Sistem menggunakan konsep publish-subscribe:

- **Publisher** → mengirim data sensor kualitas udara
- **Mosquitto Broker** → mengatur komunikasi dan distribusi pesan MQTT
- **Subscriber** → menerima data berdasarkan topic yang dipilih

Data sensor yang digunakan:

- PM2.5
- Temperature
- Humidity

---

# Teknologi yang Digunakan

- Python
- Eclipse Mosquitto MQTT Broker
- Eclipse Paho MQTT Client

---

# Persiapan Environment

Sebelum menjalankan program, pastikan beberapa komponen berikut sudah terinstall.

---

## 1. Install Python

Download dan install Python:

```
https://www.python.org/downloads/
```

Cek instalasi Python:

```bash
python --version
```

---

# 2. Install Mosquitto MQTT Broker

Download Mosquitto:

```
https://mosquitto.org/download/
```

Install sesuai sistem operasi yang digunakan.

Setelah instalasi selesai, cek Mosquitto dengan:

```bash
mosquitto -v
```

Jika berhasil, akan muncul informasi broker seperti:

```txt
mosquitto version x.x.x starting
Opening ipv4 listen socket on port 1883
```

Secara default sistem menggunakan konfigurasi:

```txt
Broker Host : localhost
Broker Port : 1883
```

---

# 3. Install Library Python MQTT

Install library Paho MQTT:

```bash
pip install paho-mqtt
```

Cek instalasi:

```bash
pip show paho-mqtt
```

---

# Cara Menjalankan Program

Program dijalankan menggunakan beberapa terminal.

Pastikan Mosquitto Broker sudah aktif sebelum menjalankan publisher dan subscriber.

---

# Terminal 1: Menjalankan Publisher

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

Publisher akan melakukan publish data:

```txt
PM2.5
Temperature
Humidity
```

dengan format topic:

```txt
FILKOM/Lantai/Ruangan/sensor/parameter
```

Contoh:

```txt
FILKOM/L4/F414/sensor/pm25
```

---

# Menjalankan Subscriber

Buka terminal baru.

Format menjalankan subscriber:

```bash
python aqms_subscriber.py <nomor_skenario>
```

Contoh:

```bash
python aqms_subscriber.py 1
```

---

# Skenario Pengujian

## Skenario 1: Basic Communication

Pengujian komunikasi dasar antara satu publisher dan satu subscriber.

Run:

```bash
python aqms_subscriber.py 1
```

Topic:

```txt
FILKOM/L4/F414/sensor/pm25
```

---

## Skenario 2: QoS Comparison

Pengujian komunikasi MQTT dengan QoS 0, QoS 1, dan QoS 2.

Run:

```bash
python aqms_subscriber.py 2
```

Topic:

```txt
FILKOM/L4/F414/sensor/pm25
FILKOM/L3/F313/sensor/pm25
FILKOM/L2/F28/sensor/pm25
```

---

## Skenario 3: Multi-Sensor Monitoring

Pengujian subscriber menerima banyak sensor secara bersamaan.

Run:

```bash
python aqms_subscriber.py 3
```

Topic:

```txt
FILKOM/L4/F414/sensor/pm25
FILKOM/L4/F414/sensor/temperature
FILKOM/L4/F414/sensor/humidity

FILKOM/L3/F313/sensor/pm25
FILKOM/L3/F313/sensor/temperature
FILKOM/L3/F313/sensor/humidity
```

---

## Skenario 4: Single-Level Wildcard

Pengujian wildcard satu tingkat menggunakan simbol `+`.

Run:

```bash
python aqms_subscriber.py 4
```

Topic:

```txt
FILKOM/+/+/sensor/pm25
```

Subscriber menerima seluruh data PM2.5 dari berbagai lantai dan ruangan.

---

## Skenario 5: Multi-Level Wildcard

Pengujian wildcard banyak tingkat menggunakan simbol `#`.

Run:

```bash
python aqms_subscriber.py 5
```

Topic:

```txt
FILKOM/#
```

Subscriber menerima seluruh data sensor dari semua lokasi FILKOM.

---

# Contoh Pengujian Banyak Terminal

## Terminal 1

Publisher:

```bash
python aqms_publisher.py
```

## Terminal 2

Skenario 1:

```bash
python aqms_subscriber.py 1
```

## Terminal 3

Skenario 2:

```bash
python aqms_subscriber.py 2
```

## Terminal 4

Skenario 3:

```bash
python aqms_subscriber.py 3
```

## Terminal 5

Skenario 4:

```bash
python aqms_subscriber.py 4
```

## Terminal 6

Skenario 5:

```bash
python aqms_subscriber.py 5
```

---

# Menghentikan Program

Untuk menghentikan publisher atau subscriber:

```bash
CTRL + C
```

---

# Struktur Project

```txt
Air-Quality-Monitoring-MQTT/

├── aqms_publisher.py
├── aqms_subscriber.py
├── README.md
└── requirements.txt
```
