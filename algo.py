import requests

API_KEY = {'X-API-Key': 'DanG'}
session = requests.Session()
session.headers.update(API_KEY)


def main():
    tick = update_tick()
    while tick < 300:
        find_calc_place()
        tick = update_tick()


# Updates the tick for the while loops to run
def update_tick():
    response = session.get('http://localhost:9999/v1/case').json()
    tick = response['tick']
    return tick


#Finds tenders, calculates if follows trend, if it does it places the tender
def find_calc_place():
    t = find_tender()
    print(t)
    p = price()
    print(p)
    long = moving_avg(40)
    short = moving_avg(10)
    place_tender(t, p, long, short)


#finds tenders and returns most important info
def find_tender():
    tick = 0
    while tick < 300:
        tick=update_tick()
        response = session.get('http://localhost:9999/v1/tenders')
        tenders = response.json()
        if tenders != []:
            id = tenders[0]['tender_id']
            action = tenders[0]['action']
            quantity = tenders[0]['quantity']
            price = tenders[0]['price']
            ticker = tenders[0]['ticker']
            return id, action, quantity, price, ticker
        else:
            print(tick)


#returns the price of both thor_m and thor_a
def price():
    m = session.get('http://localhost:9999/v1/securities/tas?ticker=THOR_M').json()
    m = m[0]['price']
    print('M:', m)
    a = session.get('http://localhost:9999/v1/securities/tas?ticker=THOR_A').json()
    a = a[0]['price']
    print('A:', a)
    return m, a


#combines thor_m and thor_a and calulates the average price of the underlying stock over the 40 and 10 tick intervals
def moving_avg(ticks):
    response_m = session.get('http://localhost:9999/v1/securities/history?ticker=THOR_M&period=1&limit={}'.format(ticks)).json()
    response_a = session.get('http://localhost:9999/v1/securities/history?ticker=THOR_A&period=1&limit={}'.format(ticks)).json()
    tot = 0
    for i in range(ticks):
        tot = tot + (response_m[i]['close'])
        i += 1
    for i in range(ticks):
        tot = tot + (response_a[i]['close'])
        i += 1
    avg = tot/(ticks*2)
    print(avg)
    return avg


#detemines whether to place tender or not
def place_tender(t, p, long, short):
    #if it is a buy tender: the price of the undlying being offered must be less than both thor_m and thor_a,
    # and the 40 tick avg must be less than 10 tick avg (uptrend)
    if (t[1] == 'BUY') and (t[3] < (p[0] and p[1])) and (long < short):
        session.post('http://localhost:9999/v1/tenders/{}'.format(t[0]))
    # if it is a sell tender: the price of the underlying being offered must be greater than both thor_m and thor_a,
    # and the 40 tick avg must be less than 10 tick avg (downtrend)
    elif (t[1] == 'SELL') and (t[3] > (p[0] and p[1])) and (long > short):
        session.post('http://localhost:9999/v1/tenders/{}'.format(t[0]))


main()

