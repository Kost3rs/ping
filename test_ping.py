import ping3
from time import sleep, strftime, localtime, time, gmtime
from os import system

ping3.EXCEPTIONS = True

exception = [False, False]


def is_host_unknown_error(exc):
    global exception
    exception[0], exception[1] = exception[1], exc


# noinspection PyUnboundLocalVariable
def ping_test(pkt_delay, pkt_loss, interr, time_max):
    if not hasattr(ping_test, "packet_count"):
        ping_test.packet_count = 1

    try:
        sleep(1)
        if (rtt := int(ping3.ping(addr) * 1000)) > time_max:
            pkt_delay += [
                f"packet_number={ping_test.packet_count}   RTT={rtt}ms   local_time={strftime('%H:%M:%S', localtime())}"]
            is_host_unknown_error(False)
        else:
            is_host_unknown_error(False)

    except ping3.errors.Timeout:
        pkt_loss += [f"packet_number={ping_test.packet_count}   Loss   local_time={strftime('%H:%M:%S', localtime())}"]
        is_host_unknown_error(False)

    except ping3.errors.HostUnknown:
        if ping_test.packet_count > 2:
            is_host_unknown_error(True)
        else:
            print(f"Ping request could not find host '{addr}'\nPlease check the name and try again.")
            exit()
        sleep(1)

    finally:
        global start_time
        if exception == [False, True]:
            start_time = time()
        elif exception == [True, False]:
            end_time = time()
            interr += [
                f"start={strftime('%H:%M:%S', gmtime(start_time))}   end={strftime('%H:%M:%S', gmtime(end_time))}   duration={strftime('%H:%M:%S', gmtime(end_time - start_time))}"]

    ping_test.packet_count += 1


packets_delayed = []
packets_lost = []
packets_cont_loss = []
cnt = 0

addr = input("Enter address: ")
rtt_max = int(input("Enter maximum acceptable ping: "))
print(f"Pinging {addr} ...   (ctrl+c to terminate)")

try:
    while True:
        ping_test(packets_delayed, packets_lost, packets_cont_loss, rtt_max)
        cnt += 1

except KeyboardInterrupt:
    for delay in packets_delayed:
        print(delay)
    print(f"Total delays: {len(packets_delayed)}\n")

    for loss in packets_lost:
        print(loss)
    print(f"Total losses: {len(packets_lost)}\n")

    for inter in packets_cont_loss:
        print(inter)
    print(f"Total interruptions: {len(packets_cont_loss)}")

system("pause")
