# DHCP Starvation - Laboratorio de Seguridad de Redes

**Ambiente:** GNS3 (Controlado) | **Herramienta:** Python 3 + Scapy | **Capa OSI:** Capa 2/3/7

## Aviso Legal

Uso **exclusivamente educativo** en laboratorio controlado (GNS3). El uso no autorizado es **ilegal**.

## 1. Objetivo del Laboratorio

Demostrar el ataque DHCP Starvation: el atacante agota el pool de direcciones IP del servidor DHCP legitimo enviando masivamente solicitudes DHCP Discover con MACs fuente falsas y aleatorias. Una vez agotado el pool, ningun cliente legitimo puede obtener una IP, causando una denegacion de servicio (DoS) en la capa de red.

## 2. Objetivo del Script

`dhcp_starvation.py` genera continuamente DHCP Discover con MACs unicas aleatorias, forzando al servidor DHCP a crear una entrada de lease por cada solicitud hasta agotar su pool de IPs.

## 3. Parametros del Script

| Parametro | Flag | Tipo | Default | Descripcion |
|-----------|------|------|---------|-------------|
| Interfaz | `-i` | str | eth0 | Interfaz de red |
| Cantidad | `-c` | int | 200 | Numero de Discovers a enviar |
| Delay | `-d` | float | 0.05 | Pausa entre paquetes (segundos) |

### Ejemplo de uso

```bash
sudo python3 dhcp_starvation.py
sudo python3 dhcp_starvation.py -c 1000 -d 0
sudo python3 dhcp_starvation.py -i eth1 -c 500 -d 0.02
```
![Texto alternativo](https://github.com/DarkyGhost107/network-security-dhcp-starvation/blob/main/screenshots/ej%20dhcp%20starvation.png)

## 4. Requisitos

```bash
Python 3.8+
pip install scapy
root (sudo)
```

## 5. Funcionamiento del Script

```
Servidor DHCP tiene pool: 192.168.1.100 - 192.168.1.200 (100 IPs)

Atacante envia:  Discover (MAC: aa:bb:cc:11:11:11) -> Lease 1
                 Discover (MAC: aa:bb:cc:22:22:22) -> Lease 2
                 ...
                 Discover (MAC: aa:bb:cc:64:64:64) -> Lease 100 <- POOL AGOTADO

Cliente legitimo: Discover (MAC real) -> No IP Available
```

Para cada iteracion:
1. Genera MAC aleatoria unica (fake_mac)
2. Convierte MAC a bytes para campo chaddr (BOOTP)
3. Genera XID aleatorio (identificador de transaccion)
4. Construye paquete DHCP Discover con flags=0x8000 (broadcast)
5. Envia via sendp() por la interfaz

## 6. Topologia de Red (GNS3)

![Texto alternativo](https://github.com/DarkyGhost107/network-security-dhcp-starvation/blob/main/screenshots/topologia%20dhcp%20starvation.png)

### Direccionamiento

| Dispositivo | IP | Rol |
|-------------|-----|-----|
| Servidor DHCP | 192.168.1.1/24 | Victima del ataque |
| Atacante | 192.168.1.50/24 | IP estatica (no usa DHCP) |
| Clientes legitimos | Sin IP (DoS) | Afectados |

## 7. Captura

```
show ip dhcp binding
```
![Texto alternativo](https://github.com/DarkyGhost107/network-security-dhcp-starvation/blob/main/screenshots/dhcp%20binding.png)

```
show ip dhcp pool
```
![Texto alternativo](https://github.com/DarkyGhost107/network-security-dhcp-starvation/blob/main/screenshots/dhcp%20pool.png)


## 8. Contramedidas

| Contramedida | Implementacion | Descripcion |
|---|---|---|
| DHCP Snooping | `ip dhcp snooping` | Valida MACs en mensajes DHCP |
| Rate-limit DHCP | `ip dhcp snooping limit rate 15` | Max 15 paquetes DHCP/seg por puerto |
| Port Security | `switchport port-security maximum 1` | Solo 1 MAC por puerto de acceso |

```cisco
ip dhcp snooping
ip dhcp snooping vlan 1
interface range GigabitEthernet0/2 - 24
 ip dhcp snooping limit rate 15
 switchport mode access
 switchport port-security
 switchport port-security maximum 2
 switchport port-security violation restrict
```
![Texto alternativo](https://github.com/DarkyGhost107/network-security-dhcp-starvation/blob/main/screenshots/contramedida%20dhcp%20starvation.png)

## 9. Referencias

- [MITRE ATT&CK T1498 - Network DoS](https://attack.mitre.org/techniques/T1498/)
- [RFC 2131 - DHCP Protocol](https://datatracker.ietf.org/doc/html/rfc2131)

## 10.Enlaces
Video: https://youtu.be/azOq5a9P29c

---
*Laboratorio de Seguridad de Redes | GNS3 | Uso educativo exclusivo*
