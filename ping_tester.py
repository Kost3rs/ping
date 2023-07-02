import ping3 as pn
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from matplotlib.animation import FuncAnimation


class PingTester:
    def __init__(self, addr, rtt):
        self.addr = addr
        self.round_trip_time = rtt
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

    def init_graph(self):
        # Set the FiveThirtyEight style
        plt.style.use('fivethirtyeight')

        # Create a figure and axis
        fig, ax = plt.subplots(figsize=(7, 5))

        # Adjust the size of the graph area within the figure
        left, bottom, right, top = .12, .11, .5, .8
        ax.set_position([left, bottom, right, top])

        # Create the animation
        _ = FuncAnimation(fig, self.ping_test, interval=1000, cache_frame_data=False)

        # Format x-axis tick labels as time in "hh:mm:ss" format
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))

        # Show plot
        plt.show()


    def update_graph(self):
        # Clear the previous plot
        plt.cla()

        # Convert string time (H:M:S) to numerical format
        today = datetime.today().date()

        # Change each element of array to datetime format
        lc_time = [datetime.combine(today, t) for t in self.graph_time_period]

        # Plot the data
        plt.plot(lc_time, self.graph_packets_rtt)

        # Create interruption period background
        for start, end in self.graph_interrupt_period:
            start_datetime = datetime.combine(today, start)
            end_datetime = datetime.combine(today, end)
            plt.axvspan(start_datetime, end_datetime, facecolor="tomato", alpha=0.3)

        # Set plot title and labels
        plt.xlabel("LOCAL TIME")
        plt.ylabel("RTT")
        plt.title(address)

        # Auto-adjust the x-axis tick labels
        plt.gcf().autofmt_xdate()


    @staticmethod
    def display_array(arr, text):
        for elem in arr:
            print(elem)
        print(text)

    # Identify continuous loss
    def is_host_unknown_error(self, exc):
        self.exception_events[0], self.exception_events[1] = self.exception_events[1], exc

    # Main ping method
    def ping_test(self, _):
        try:
            local_time = datetime.now().time().replace(microsecond=0)
            self.graph_time_period.append(local_time)

            rtt = int(pn.ping(self.addr) * 1000)
            if rtt > self.round_trip_time:
                self.packets_delayed.append(f"packet_number={self.packet_id}   RTT={rtt}ms   local_time_sent={local_time}")

            self.graph_packets_rtt.append(rtt)
            self.is_host_unknown_error(False)

        # Lost packet
        except pn.errors.Timeout:
            self.packets_lost.append(f"packet_number={self.packet_id}   Loss   local_time_sent={local_time}")
            self.graph_packets_rtt.append(np.nan)
            self.is_host_unknown_error(False)

        # Lost packets/Interruption (continuous)
        except pn.errors.HostUnknown:
            if self.packet_id > 2:
                self.graph_packets_rtt.append(np.nan)
                self.is_host_unknown_error(True)
            else:
                print(f"Ping request could not find host '{self.addr}'\nPlease check the name or try again later.")
                exit()

        finally:
            # Check for stream of lost packets(interruption) and save time data
            if self.exception_events == [False, True]:
                self.time_start = local_time

            elif self.exception_events == [True, False]:
                time_end = datetime.now().time().replace(microsecond=0)
                duration = datetime.combine(datetime.today(), time_end) - datetime.combine(datetime.today(), self.time_start)
                self.packets_cont_loss.append(f"intr_start={self.time_start}   intr_end={time_end}   duration={duration}")
                self.graph_interrupt_period.append((self.time_start, time_end))

            self.update_graph()
            self.packet_id += 1

    def run(self):
        print(f"Pinging {self.addr}...")

        self.init_graph()

        # Print captured data
        self.display_array(self.packets_delayed, f"Total delays: {len(self.packets_delayed)}\n")
        self.display_array(self.packets_lost, f"Total losses: {len(self.packets_lost)}\n")
        self.display_array(self.packets_cont_loss, f"Total interruptions: {len(self.packets_cont_loss)}\n")

        # Quit program
        input("Press Enter to exit...")
        exit()


if __name__ == '__main__':
    address = input("Enter address: ")
    round_trip_time = int(input("Enter maximum acceptable ping: "))

    tester = PingTester(address, round_trip_time)
    tester.run()
