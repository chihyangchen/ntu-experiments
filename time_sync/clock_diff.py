import csv

def clock_diff():
    server = []
    client = []
    with open("sync_client_before.csv", newline='') as f:
        reader = csv.reader(f)
        client = list(reader)
    with open("sync_client_after.csv", newline='') as f:
        reader = csv.reader(f)
        client.append(list(reader))
    with open("sync_server_before.csv", newline='') as f:
        reader = csv.reader(f)
        server = list(reader)
    with open("sync_server_after.csv", newline='') as f:
        reader = csv.reader(f)
        server.append(list(reader))

    diff1 = 0.0
    diff2 = 0.0
    ref_time1 = 0.0
    ref_time2 = 0.0
    cnt1 = 0
    cnt2 = 0

    for i in range(len(client[0])):
        RTT = float(client[0][i][1]) - float(client[0][i][0])
        if(RTT > 0.01):
            continue
        cen_client = (float(client[0][i][1]) + float(client[0][i][0]))/2
        cen_server = (float(server[0][i][1]) + float(server[0][i][0]))/2
        diff1 += cen_server - cen_client
        cnt1 = cnt1+1
    diff1 /= cnt1

    for i in range(len(client[1])):
        RTT = float(client[1][i][1]) - float(client[1][i][0])
        if(RTT > 0.01):
            continue
        cen_client = (float(client[1][i][1]) + float(client[1][i][0]))/2
        cen_server = (float(server[1][i][1]) + float(server[1][i][0]))/2
        diff2 += cen_server - cen_client
        cnt2 = cnt2+1
    diff2 /= cnt2

    ref_time1 = float(server[50][0])
    ref_time2 = float(server[-50][0])

    return ref_time1, ref_time2, diff1, diff2


def server_time_to_client_time(server_time, ref_time1, ref_time2, diff1, diff2):
    return server_time - (diff1*(ref_time2-server_time)+diff2*(server_time-ref_time1))/(ref_time2-ref_time1)