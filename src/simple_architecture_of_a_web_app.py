from diagrams import Diagram, Cluster, Edge
from diagrams.generic.network import Firewall
from diagrams.generic.os import Android, IOS, Windows, LinuxGeneral, Centos
from diagrams.oci.connectivity import DNS
from diagrams.onprem.database import MySQL
from diagrams.onprem.inmemory import Redis
from diagrams.onprem.network import Nginx, HAProxy
from diagrams.programming.framework import Laravel

NUM_APP_SERVERS = 1
NUM_MYSQL_REPLICAS = 2
NUM_PHP_FPM_FORKS = 2
NUM_REDIS_REPLICAS = 1

with Diagram('Simple architecture of a web app', show=False, direction='TB'):
    lb = Nginx('Load Balancer based on NGINX')
    lb_firewall = Firewall('Firewall of Load Balancer')
    dns = DNS('Any DNS server')

    redis_haproxy = HAProxy('HAProxy for Redis Cluster')
    db_haproxy = HAProxy('HAProxy for MySQL Cluster')

    with Cluster('Users') as users:
        with Cluster('Desktop users'):
            dns << LinuxGeneral() >> lb_firewall >> lb
            dns << Windows() >> lb_firewall >> lb

        with Cluster('Mobile users'):
            dns << IOS() >> lb_firewall >> lb
            dns << Android() >> lb_firewall >> lb

    with Cluster('Redis Cluster'):
        redis_nodes = []

        redis_main = Redis('Redis: main')
        redis_nodes.append(redis_main)

        for n in range(1, NUM_REDIS_REPLICAS + 1):
            replica = Redis(f'Redis: replica {n}')
            redis_nodes.append(replica)

            replica << redis_nodes[n - 1]

            redis_main << replica
            redis_main >> replica

            replica >> redis_haproxy
            redis_haproxy >> replica

        redis_haproxy.connect(
            redis_main,
            Edge(redis_haproxy, reverse=True, color='#5e73e5')
        )
        redis_main.connect(
            redis_haproxy,
            Edge(redis_main, reverse=True, color='#2ea44f')
        )

    with Cluster('MySQL Cluster'):
        mysql_nodes = []

        mysql_main = MySQL('MySQL: main')
        mysql_nodes.append(mysql_main)

        for n in range(1, NUM_MYSQL_REPLICAS + 1):
            replica = MySQL(f'MySQL: replica {n}')

            mysql_nodes.append(replica)

            mysql_main << replica
            mysql_main >> replica

            replica << db_haproxy
            replica >> db_haproxy

        db_haproxy.connect(
            mysql_main,
            Edge(db_haproxy, reverse=True, color='#5e73e5')
        )
        mysql_main.connect(
            db_haproxy,
            Edge(mysql_main, reverse=True, color='#2ea44f')
        )

    with Cluster('Servers Cluster'):
        for i in range(1, NUM_APP_SERVERS + 1):
            with Cluster(f'Server: node {i}'):

                server = Centos('Server')
                server_firewall = Firewall('Firewall')
                laravel_app = Laravel('PHP FPM: master')

                with Cluster(f'PHP FPM forks: node {i+1}'):
                    phpfpm_forks = [Laravel(f'PHP FPM: fork {n}') for n in range(1, NUM_PHP_FPM_FORKS + 1)]
                    laravel_app >> phpfpm_forks

                    for y, phpfpm_fork in enumerate(phpfpm_forks):
                        phpfpm_fork << db_haproxy
                        phpfpm_fork >> db_haproxy

                        phpfpm_fork << redis_haproxy
                        phpfpm_fork >> redis_haproxy

                lb >> server_firewall
                server_firewall >> server
                server >> laravel_app
