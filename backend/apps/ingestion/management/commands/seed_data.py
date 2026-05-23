import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.ingestion.models import LogEntry

class Command(BaseCommand):
    help = "Seeds the database with realistic synthetic network log entries for testing."

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding database with log entries...")
        
        protocols = ["TCP", "UDP", "ICMP"]
        attack_labels = [
            "DDoS", "PortScan", "BruteForce", "WebAttack-BruteForce", 
            "WebAttack-XSS", "Infiltration", "Bot", "DoS-Hulk"
        ]
        
        # Commonly used IPs
        source_ips = [f"192.168.1.{i}" for i in range(10, 250)] + [
            "10.0.0.15", "10.0.0.16", "172.16.0.5", "172.16.0.6"
        ]
        dest_ips = ["192.168.1.1", "10.0.0.1", "172.16.0.1", "8.8.8.8", "1.1.1.1"]

        created_count = 0
        now = timezone.now()

        for i in range(1000):
            is_attack = random.random() < 0.20  # 20% attack logs
            
            src_ip = random.choice(source_ips)
            dst_ip = random.choice(dest_ips)
            proto = random.choice(protocols)
            
            # Attacking signatures
            if is_attack:
                label = random.choice(attack_labels)
                if label == "PortScan":
                    # Port scans target many destination ports
                    dst_port = random.randint(1, 65535)
                    src_port = random.randint(1024, 65535)
                    bytes_sent = random.randint(40, 120)
                    bytes_received = 0
                    duration_ms = random.randint(1, 50)
                    packet_count = 1
                elif label == "DDoS":
                    # DDoS has high volume same dest port
                    dst_port = 80
                    src_port = random.randint(1024, 65535)
                    bytes_sent = random.randint(500, 1500)
                    bytes_received = random.randint(500, 1500)
                    duration_ms = random.randint(5, 500)
                    packet_count = random.randint(10, 50)
                elif label == "BruteForce":
                    dst_port = 22 if random.random() < 0.5 else 3389
                    src_port = random.randint(1024, 65535)
                    bytes_sent = random.randint(150, 400)
                    bytes_received = random.randint(150, 400)
                    duration_ms = random.randint(100, 2000)
                    packet_count = random.randint(5, 15)
                else:
                    dst_port = random.choice([80, 443, 8080])
                    src_port = random.randint(1024, 65535)
                    bytes_sent = random.randint(1000, 50000)
                    bytes_received = random.randint(1000, 200000)
                    duration_ms = random.randint(10, 5000)
                    packet_count = random.randint(2, 200)
            else:
                label = "BENIGN"
                dst_port = random.choice([80, 443, 53, 123])
                src_port = random.randint(1024, 65535)
                bytes_sent = random.randint(50, 10000)
                bytes_received = random.randint(50, 50000)
                duration_ms = random.randint(5, 2000)
                packet_count = random.randint(2, 50)

            # Randomize timestamp over the last 3 hours to create nice time-series
            time_offset = random.randint(0, 10800)
            log_time = now - timezone.timedelta(seconds=time_offset)

            try:
                LogEntry.objects.create(
                    timestamp=log_time,
                    source_ip=src_ip,
                    destination_ip=dst_ip,
                    source_port=src_port,
                    destination_port=dst_port,
                    protocol=proto,
                    bytes_sent=bytes_sent,
                    bytes_received=bytes_received,
                    duration_ms=duration_ms,
                    packet_count=packet_count,
                    tcp_flags="0x02" if proto == "TCP" else "",
                    label=label,
                    source="synthetic_seed",
                )
                created_count += 1
            except Exception as e:
                self.stderr.write(f"Error seeding row {i}: {e}")

        self.stdout.write(self.style.SUCCESS(f"Successfully seeded {created_count} LogEntry records!"))
