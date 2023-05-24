import ping3 as pn
from time import sleep
from os import system
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime


class PingTester:
    def __init__(self, addr, round_trip_time):
        self.addr = addr
        self.round_trip_time = round_trip_time
        self.packets_delayed = []
        self.packets_lost = []
        self.packets_cont_loss = []
        self.graph_time_period = []
        self.graph_packets_rtt = []
        self.graph_interrupt_period = []
        self.exception_events = [False, False]
        self.time_start = None
        self.packet_id = 1

        pn.EXCEPTIONS = True  # Enable exceptions from the ping3 lib

    def create_graph(self):
        # Convert string time (H:M:S) to numerical format
        today = datetime.today().date()
        lc_time = [datetime.combine(today, t) for t in self.graph_time_period]

        # Convert datetime objects to numerical format
        lc_num = mdates.date2num(lc_time)

        # Create figure and axes
        fig, ax = plt.subplots()

        # Create interruption period background
        for start, end in self.graph_interrupt_period:
            start_datetime = datetime.combine(today, start)
            end_datetime = datetime.combine(today, end)
            ax.axvspan(start_datetime, end_datetime, facecolor="tomato", alpha=0.3)

        # Set date format for x axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))

        # Plot graph
        ax.plot(lc_num, self.graph_packets_rtt)

        # Graph labels
        plt.xlabel("LOCAL TIME")
        plt.ylabel("RTT")
        plt.title("Round Trip Time Over Time")

        plt.show()

    def display_array(self, arr, text):
        for elem in arr:
            print(elem)
        print(text)

    def is_host_unknown_error(self, exc):
        self.exception_events[0], self.exception_events[1] = self.exception_events[1], exc

    def ping_test(self):
        try:
            local_time = datetime.now().time().replace(microsecond=0)
            self.graph_time_period.append(local_time)

            rtt = int(pn.ping(self.addr) * 1000)
            if rtt > self.round_trip_time:
                self.packets_delayed.append(
                    f"packet_number={self.packet_id}   RTT={rtt}ms   local_time_sent={local_time}")

            self.graph_packets_rtt.append(rtt)
            self.is_host_unknown_error(False)

        except pn.errors.Timeout:
            self.packets_lost.append(f"packet_number={self.packet_id}   Loss   local_time_sent={local_time}")
            self.graph_packets_rtt.append(np.nan)
            self.is_host_unknown_error(False)

        except pn.errors.HostUnknown:
            if self.packet_id > 2:
                self.graph_packets_rtt.append(np.nan)
                self.is_host_unknown_error(True)
            else:
                print(f"Ping request could not find host '{self.addr}'\nPlease check the name or try again later.")
                exit()

        finally:
            if self.exception_events == [False, True]:
                self.time_start = local_time

            elif self.exception_events == [True, False]:
                time_end = datetime.now().time().replace(microsecond=0)
                duration = datetime.combine(datetime.today(), time_end) - datetime.combine(datetime.today(),
                                                                                           self.time_start)
                self.packets_cont_loss.append(
                    f"intr_start={self.time_start}   intr_end={time_end}   duration={duration}")
                self.graph_interrupt_period.append((self.time_start, time_end))

            sleep(1)
            self.packet_id += 1

    def run(self):
        print(f"Pinging {self.addr} ...   (ctrl+c to terminate)")

        try:
            while True:
                self.ping_test()

        except KeyboardInterrupt:
            self.display_array(self.packets_delayed, f"Total delays: {len(self.packets_delayed)}\n")
            self.display_array(self.packets_lost, f"Total losses: {len(self.packets_lost)}\n")
            self.display_array(self.packets_cont_loss, f"Total interruptions: {len(self.packets_cont_loss)}\n")

        self.create_graph()

        system("pause")


if __name__ == '__main__':
    addr = input("Enter address: ")
    round_trip_time = int(input("Enter maximum acceptable ping: "))

    tester = PingTester(addr, round_trip_time)
    tester.run()
