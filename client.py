import requests


URL = 'http://localhost:5000'


def get_response():
    url = URL + '/api?pots=1'
    return requests.get(url).json()


def parse_response(response):
    tea = response['pots'][0]['tea']
    brewer = response['pots'][0]['brewer']
    datetime = response['pots'][0]['datetime']
    return tea, brewer, datetime


def main():
    res = get_response()
    data = parse_response(res)
    print data


if __name__ == '__main__':
    main()
