import random
import os

def get_proxy_new()-> dict:
    """
    It returns a dictionary with the keys 'http' and 'https' and the values are the proxy address to use the datacenter proxy
    :return: A dictionary with the keys 'http' and 'https' and the values are the entry variable.
    """

    #3victors
    username = os.getenv('PROXYUSERNAME')
    password = os.getenv('PROXYPASSWORD')
    #PICK ONE LATAM COUNTRY, SPANISH SPEACKING
    country = ['MX','CO']
    country = random.choice(country)

    port = 22225
    super_proxy_url = ('http://%s-country-%s:%s@zproxy.lum-superproxy.io:%d' %
        (username, country, password, port))
    proxy_handler = {
        'http': super_proxy_url,
        'https': super_proxy_url,
    } 
    return proxy_handler


headersX = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'en-US,en;q=0.9',
    'Cache-Control': 'no-cache',
    'Pragma': 'no-cache',
    'Priority': 'u=0, i',
    'Sec-CH-UA': '"Not.A/Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
    'Sec-CH-UA-Mobile': '?0',
    'Sec-CH-UA-Platform': '"macOS"',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
}
