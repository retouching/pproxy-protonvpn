<h1>PProxy ProtonVPN</h1>
<h4>Use ProtonVPN servers as proxy</h4>

- This project is derived from [proton-privoxy](https://github.com/walterl/proton-privoxy), we just use PProxy instead of Privoxy to handle authentication possibility.

## Basic usage:

```sh
docker run -d \
     --device=/dev/net/tun \
     --cap-add=NET_ADMIN \
     -v /etc/localtime:/etc/localtime:ro \
     -e "PVPN_USERNAME=xxx" \
     -e "PVPN_PASSWORD=xxx" \
     -e "PVPN_TIER=3" \
     -e "PPROXY_ARGS=-l http+socks4+socks5://:7070 -v" \
     -e "PVPN_ARGS=--cc jp" \
     -p 7070:7070 \
     retouch1ng/pproxy-protonvpn
```


This will start a Docker container that

1. Initializes a `protonvpn` CLI configuration
2. Refreshes ProtonVPN server data (connects to https://api.protonvpn.ch)
3. Sets up an OpenVPN connection to ProtonVPN with your ProtonVPN account details, and
4. Starts a PProxy server, that directs traffic over your VPN connection.

Test:

```
curl --proxy http://127.0.0.1:7070 https://ipinfo.io/ip
```

To expose the PProxy server outside, you can setup another pproxy like this (because by default only host can have access to the proxy):

```sh
docker run -p 9999:9999 \
     mosajjal/pproxy:latest \
     -l http+socks4+socks5://:9999#user:password
     -r http+socks4+socks5://127.0.0.1:7070
     -v
```

## Features

### Multiple VPN connections on the same machine

While not impossible, it is quite the networking feat to route traffic over
specific VPN connections. With this Docker image you can run multiple
containers, each setting up a different VPN connection _which doesn't affect
your host's networking_. Routing traffic over a specific VPN connection is then
as simple as configuring a target application's proxy server.

## Configuration

You can set any of the following container environment variables with
`docker run`'s `-e` options.

### `PVPN_USERNAME` and `PVPN_PASSWORD`

**Required.** This is your ProtonVPN OpenVPN username and password. It's the
username and password you would normally provide to `protonvpn init`.

### `PVPN_TIER`

**Required.** Your ProtonVPN account tier, called "your ProtonVPN Plan" in `protonvpn init`.
The value must be the number corresponding to your tier from the following
list (from `protonvpn init`):

```
0) Free
1) Basic
2) Plus
3) Visionary
```

### `PVPN_ARGS`

Any arguments you want to pass to `protonvpn connect`. For example, if you want
`protonvpn` to connect to a random server, set this to `--random`.

See the [`protonvpn` docs](https://github.com/ProtonVPN/linux-cli-community/blob/master/USAGE.md) for supported commands and arguments.

Default: `--fastest` (_Select the fastest ProtonVPN server._)

### `PPROXY_ARGS`

Any arguments you want to pass to `pproxy`. For example, if you want
`pproxy` to run with http, socks4 and socks5 support with verbose (so you can see usage), set it to `http+socks4+socks5://:8080`

See the [`pproxy` docs](https://github.com/qwj/python-proxy) for supported commands and arguments.

Default: `http+socks4+socks5://:8080`