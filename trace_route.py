import subprocess
import json
import requests
import re
import argparse
IP_RE = re.compile(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})")


def get_route_ips(domain: str, max_hops: int):
    """Returns list of ip addresses in route to a given destination"""
    ips = []
    with subprocess.Popen(["tracert", "-h", str(max_hops), domain],
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT) as tracer:
        for hop in tracer.stdout:
            hop = hop.decode("cp866")
            if ip := IP_RE.search(hop):
                ips.append(ip.group())
        if len(ips) < 2:
            print("Unable to trace route to that domain")
            return
        ips.append(ips.pop(0))

    return ips


def trace_route(ips: list[str]) -> None:
    """Prints out info about given ip addresses"""
    result = requests.post("http://ip-api.com/batch", data=json.dumps(ips), timeout=100).json()

    for item in result:
        if all(key in item for key in ("org", "city", "country")):
            output = f'"{item["org"]}" {item["city"]}, {item["country"]}:'
            print(output, end=" ", flush=True)
        print(item["query"])


def main():
    parser = argparse.ArgumentParser(description="Traces route to a given destination")
    parser.add_argument("--hops", action="store", type=int, default=30, help="max amount of hops")
    parser.add_argument("domain", action="store", help="destination")
    args = parser.parse_args()

    trace_route(get_route_ips(args.domain, args.hops))


if __name__ == "__main__":
    main()
