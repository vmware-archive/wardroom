import re
import socket


class FilterModule(object):

    def filters(self):
        return {
            'kube_lookup_hostname': self.kube_lookup_hostname,
        }

    def kube_lookup_hostname(self, ip, hostname, many=False):
        ips = set()

        ip = ip.split(':')[0]
        if ip and ip != "":
            if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", ip):
                ips.add(ip)
        try:
            (_, _, iplist) = socket.gethostbyname_ex(hostname)
            ips |= set(iplist)
        except socket.error as e:
            pass

        if many:
            ips.add(hostname)
            return sorted(list(ips))
        else:
            return sorted(list(ips))[0]
