# Wake-on-LAN across subnets (UniFi)

Only needed when Home Assistant and the display are on **different** subnets. If they
share a subnet, leave the broadcast address at `255.255.255.255` and ignore this file.

## Why the default fails

`255.255.255.255` is the *limited* broadcast address. It is non-routable by definition:
the gateway drops it instead of forwarding it, so the magic packet never leaves Home
Assistant's own VLAN.

The fix is to send the packet to a **routable** address in the display's subnet, and have
the gateway resolve that address to the broadcast MAC. The gateway then floods the frame
across the display's VLAN, where the display's NIC picks it up.

## Connecting to the gateway

SSH to the gateway as `root`, using your **UniFi admin credentials** (the same ones you
use for the controller UI). Enable SSH first under `Settings > System > Advanced`.

```sh
ssh root@192.168.1.1   # your gateway's IP
```

## 1. Pick a beacon IP

Any unused address in the display's subnet, **outside the DHCP pool**, and **not the
gateway's own IP** — traffic to the gateway's address is delivered locally and never
forwarded, so it will silently do nothing.

One beacon IP serves every display on that VLAN. The frame is flooded to all ports, and
the target MAC lives inside the magic packet payload, so each display decides for itself
whether to wake.

Example below: display VLAN is `192.168.45.0/24` on `br45`, beacon is `192.168.45.250`.

## 2. Add the static ARP entry

```sh
ip neigh replace 192.168.45.250 lladdr ff:ff:ff:ff:ff:ff dev br45 nud permanent
```

Use `replace` rather than `add` — it is idempotent, so re-running it is safe.

> `set protocols static arp ...` is EdgeOS/VyOS syntax. It does not exist on UniFi OS
> (UDM / UDR), and on a USG the controller overwrites it on every provision unless it is
> placed in `config.gateway.json`.

Verify — the entry must read `PERMANENT`, not `STALE` or `FAILED`:

```sh
ip neigh show dev br45 | grep 192.168.45.250
```

## 3. Allow the traffic

In the controller, add a firewall rule permitting Home Assistant's subnet to reach the
display's subnet on **UDP port 9**. A blanket "block inter-VLAN traffic" rule or Device
Isolation on the display's network takes precedence over any allow rule placed below it.

## 4. Make it survive reboots

`ip neigh` entries are runtime-only. On UniFi OS, persist via a boot script (requires
`udm-boot`):

```sh
mkdir -p /data/on_boot.d
cat > /data/on_boot.d/10-wol-arp.sh <<'EOF'
#!/bin/sh
ip neigh replace 192.168.45.250 lladdr ff:ff:ff:ff:ff:ff dev br45 nud permanent
EOF
chmod +x /data/on_boot.d/10-wol-arp.sh
```

## 5. Configure the integration

Set the integration's **Wake-on-LAN broadcast address** to the beacon IP
(`192.168.45.250`), not to `255.255.255.255` and not to the display's own IP.

Pointing it at the display's real IP would also work, but every SICP control packet on
TCP 5000 would then be flooded across the whole VLAN.

## Troubleshooting

Watch the Home Assistant log — this line is only emitted on the Wake-on-LAN path, so its
absence means the display was never considered offline in the first place:

```
Sending Wake-on-LAN to <mac> via <broadcast>
```

Confirm the packets actually reach the display's VLAN:

```sh
tcpdump -ni br45 udp port 9
```
