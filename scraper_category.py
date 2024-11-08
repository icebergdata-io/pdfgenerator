
import requests, os, json

from aux_scraper import get_proxy_new
main_folder = 'output'



def get_category(skuid):
    
    headers = {
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'no-cache',
        'content-type': 'application/json',
        # 'cookie': '_vwo_uuid_v2=D8C8F6F47156C818EA2068B205F4041C2|f5f6af1f83092450ea922ce07bd779cc; _vwo_uuid=D8C8F6F47156C818EA2068B205F4041C2; _gcl_au=1.1.1142744407.1723941991; _ga_transaction_ids=; _vis_opt_s=1%7C; _vis_opt_test_cookie=1; _vis_opt_exp_1001_exclude=1; _vis_opt_exp_928_combi=2; _gid=GA1.2.674767386.1723941991; _pin_unauth=dWlkPU5tRmlPV1prWVRFdE1EQmpOaTAwT0dRNExXSTFZakV0WkRnek4yUTJOVGMzWWpGaw; AF_DEFAULT_MEASUREMENT_STATUS=true; _tt_enable_cookie=1; _ttp=81M9mTkyLNaiZf9R1CGoJRvtuDH; _vis_opt_exp_928_goal_3=1; _fbp=fb.1.1723943098695.654702887657976642; _clck=1k2q9sa%7C2%7Cfof%7C0%7C1691; afUserId=903be7b6-fee9-4a21-86ee-0f937963dd85-p; AF_SYNC=1723943099184; sn_medallia=0; mdLogger=false; COPPEL_SHOW_GEO_CONFIRM=false; COPPEL_USER_HAS_LOCATION=true; COPPEL_CITY=IZTAPALAPA; COPPEL_STATE=CIUDAD%20DE%20MEXICO; COPPEL_REGIONTELCEL=2; COPPEL_LOCATION_SERVICE_EXPIRY=true; COPPEL_GEOLOC_COOKIE=IZTAPALAPA%2C%20CIUDAD%20DE%20MEXICO%7C107%7C10054%7C2; WC_physicalStores=11419%2C11396; CompareItems_10151=; ak_bmsc=C9C849D63ACBCCE162F7E23BF862034B~000000000000000000000000000000~YAAQ0Zx6XEHs9V+RAQAApU/fZhhG29NTGCI8Ne8LSEDioP7Oy6BMAElQzEHwt7Z55ppJeHdbMaR9t9xmzWej19F9NDOEtLoHnyDIeBuJjMxRDzY/h+MuAmoBrHaoeIW2jlEJ/ykW4vx/wGsH2nZOen0bA9o5BAfnGHO4I3nQfXkWI3MZyRL70ZuPOnvvqsQ8U9CSNq8XqdIX7tYkEGLqI28IkUR/C6duAF76jQ7gDxfTwGpJKpbMbZT7edyTI+5YQeuV5aEX5XZuR6WmHnZhKGz4bzE2Efp9jRIp+vSk0RL+yvXvCRq7xlswGaGrdEgdC7Y3DPttxkufRuor+1ponlFE1loO1BamH5YeIJ0vGhXawy4gLZgwS7xzIcE1eQDVcQtp6hTm1LBnQIzFSoXywpKoJbTDvAVopFa1ivSt0pRUU8npAyTPhjyk0FGBdk4tHlSm7tJdJZnIow==; attr_source_cookie=direct; LAST_INVITATION_VIEW=1724010160304; DECLINED_DATE=1724010162158; JSESSIONID=0000k7f3FMMuvRgVeBrAl8eLZ4C:-1; WC_SESSION_ESTABLISHED=true; WC_PERSISTENT=upxJQB8fyJUEqaOAmALAoddKfPFXyUQtRAbkYjVqr0I%3D%3B2024-08-18+13%3A43%3A46.472_1724010226465-8220_10151_-1002%2C-5%2CMXN%2C2024-08-18+13%3A43%3A46.472_10151; WC_AUTHENTICATION_-1002=-1002%2CJdh5JVzqovGDGuZIS9A0yAc11LCiDPi1CWNOoTX%2B9xo%3D; WC_ACTIVEPOINTER=-5%2C10151; priceMode=1; amp_e89823=2LjmeL2xxyUsyv1pbnAsfs...1i5jg8pr5.1i5jg8pr5.0.0.0; scarab.visitor=%22402357E68D8F997A%22; WC_USERACTIVITY_-1002=-1002%2C10151%2C0%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2C1586520367%2Cver_null%2C917rcxYWH0P6sx8wrM%2B7nwzNZ9PJ%2FscnYBu%2FhSbaQHknYX6oBm6%2BVOrImx9hz9iP9BqbebtnjfjkMtpE5ewlyrK%2F28R1zaznMnzvbTHH3UQHI9G1LMbS5bxGg5ZM1axXw6fK5MB9PFmwUFM%2BouuVWwVH1OHWh%2FH34ao%2BeJC%2FSdHCJp%2FVy2XqEgPDb32n%2FdDj2ZCb4s8dO68YsGbuAnPGYWpTdD2VkIdwnyM7Pmv6OmH%2BUjfC7jVzJnLAzN7BCca9; WC_ACTIVITYDATA_-1002=G%2C-5%2CMXN%2C10051%2C4000000000000000003%2C-2000%2C1724010226465-8220%2C-5%2CMXN%2C5%2F9rTSOmNz37EiURELKnxftcU96IUrTo5FMyk4G2KVods%2FxjecHHytfJhlfLe%2FGFcOTWQqHuxOPM2kBnKR8l3g6mi1SEU7aYx31FYUfI0HJq%2FMiKfMlLurW09i2LgQyxYCtDGwjS%2B4RDq6q%2FvU%2FSYcOdSEyPeA4vZJ277a7f3WXLELYQPNRONE7OdU4KTSaSDiAQ520gHggbR6ClDmQ0%2F8chOpuubuICqrr%2Fi6l5ti0%3D; searchTermHistory=; bm_sz=A9B1339C96BB3ECB1520FAF904A5ECA5~YAAQ0Zx6XNAw91+RAQAAxrcEZxhTZQXrIIHCKrAFo7YDS0+Z5tuUvRpgSL1ej+3yGO4QSr1Eu3K0FWsLwGipBZrhmr2HBgo6E013/E0C7GH/hZS9ppvDY+5wlWTXQbeK/+h/dFHVM2osiExkqVTF/6KSSbCt2KyPDfdDtvzs3nLwbzJCiuKquPqdqKi/8px0Z0DnhT6IUhwNe2pQJsX3SaKr1o2DpRnwDsFyYhfc73+Kdm8wMHIhJxHCJl8ap7OjDsMwKwy6L5/amPx4eaFbaZh0oF4Y8TdGsodhaoptT15ZevC34WDB3pqLAESZJCd+enuntqnW9Pmsvhzb/zqyo4z8ANtUbpnAg/n40wT/xCwzVU9ZXmxjSQBkfVkAZdiK8WSQrF/JFl4hvM5B5ueMR/v/LAoqaDlt6duzkGDo668kBxZUnA==~3617593~3488068; _abck=CA99D52C2809330A7960C2F80FEE0E96~0~YAAQ0Zx6XN0w91+RAQAARbkEZwwTyv6LJpwuSa8fb7TNMXXe6mNZULIst7TOOIDaNQ28N/kewtoFfUebet2NZMp6ilzgVjTs9ewgxR2sk1dddzbuoXPRr2Aeaah6FjjYvHfWKUO7rsHk3v2mSxpJeGbcWyuA2p0oTKw9k0KyGNGlgpTma33V1o8ujX86v/KcKEj9NQ5YwSRLkF5Zhnbh6sFZ2sZbBaZpfnU0PjEfzMhghutBsKYNrJPQ7YRYhx0LfhL2W7XIeSPX6K+rvD+GHz69VRzAKSjW8t/XQwtUxYOtK+hIVY6LnLAhV9RSEOhGWiYR16LYZXvZ5gj7fSCq37Zk8pipIikuhbuKdwEfodPsF1jwzoRQRiffgehEfM7xFv9ENJnvYbxpp4eBxJeBnkGBGd3tVKqJ9BxMD4ulSPaZoXa0MoqwPiIzp1J+BvBpWNLXVOnpup237XBWZZrodOER284=~-1~||0||~1724011875; referrer=; _ga=GA1.2.2073334240.1723941991; _uetsid=4fa14d305cfb11ef9e52a19cee4d89d2; _uetvid=d6905530c50511ed8c49914a1dc7c507; RT="z=1&dm=coppel.com&si=0c29cedd-f968-4d91-b300-2652b93b1738&ss=lzzz4t5v&sl=7&tt=d5z&bcn=%2F%2F17de4c1d.akstat.io%2F&obo=2&ld=f1zv"; _vwo_ds=3%3Aa_0%2Ct_0%3A0%241723941990%3A55.13211659%3A628_0_0_0_10%3A11_0%2C12_0%2C13_0%2C14_0%2C29_0%2C31_0%3A102_0%2C77_0%3A1108; kampyleUserSession=1724010857488; kampyleUserSessionsCount=10; kampyleSessionPageCounter=1; kampyleUserPercentile=82.07999505646757; _clsk=bksrl9%7C1724010857787%7C21%7C0%7Cj.clarity.ms%2Fcollect; _gat_UA-11434205-16=1; _ga_L8MJGBT6R4=GS1.1.1724007797.4.1.1724010937.60.0.0; _vwo_sn=65805%3A22%3A%3A%3A1',
        'pragma': 'no-cache',
        'priority': 'u=1, i',
        'sec-ch-ua': '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
    }

    params = {
        'operationName': 'GetSearchResults',
        'variables': '{"pageNumber":"1","pageSize":"1","orderBy":"0","filter":[],"searchTerm":"SKUID"}'.replace("SKUID", str(skuid)),
        'extensions': '{"persistedQuery":{"version":1,"sha256Hash":"688ca29fde750ccd49c5a108718a636d69b8aa2d453b5422aba045b4ab404d37"}}',
    }

    response = requests.get('https://www.coppel.com/graphql'
        , params=params
        , headers=headers
        , proxies=get_proxy_new()
        )

    principal_category = response.json()['data']['search']['categories'][0]['category']

    secondary_category = response.json()['data']['search']['categories'][1]['category'] if len(response.json()['data']['search']['categories']) > 1 else None


    with open(f'output/search/{skuid}.json', 'w') as f:
        json.dump(response.json(), f, indent=4)

    taxanomy = [principal_category, secondary_category]

    return taxanomy

skuid = 2050533

if __name__ == '__main__':
    taxanomy = get_category(skuid)
    print(taxanomy)