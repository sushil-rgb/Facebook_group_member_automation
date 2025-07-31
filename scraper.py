from tools import make_requests, random_interval
from camoufox.async_api import AsyncCamoufox
from browserforge.fingerprints import Screen
from dotenv import load_dotenv
import aiosqlite
import asyncio
import json
import os
import re


# Load email and password from environment variables
load_dotenv()
EMAIL = os.getenv("FACEBOOK_EMAIL")
PASSWORD = os.getenv("FACEBOOK_PASSWORD")


# Define a custom browser fingerprint for Camoufox session
async def configurations():
    config = {
    'window.history.length': 4,
    'navigator.userAgent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0',
    'navigator.appCodeName': 'Mozilla',
    'navigator.appName': 'Netscape',
    'navigator.appVersion': '5.0 (Windows)',
    'navigator.oscpu': 'Windows NT 10.0; Win64; x64',
    'navigator.language': 'en-US',
    'navigator.languages': ['en-US'],
    'navigator.platform': 'Win32',
    'navigator.hardwareConcurrency': 12,
    'navigator.product': 'Gecko',
    'navigator.productSub': '20030107',
    'navigator.maxTouchPoints': 10,
    }
    return config


# Automate login with Camoufox and save cookies to SQLite
async def save_login_session(headless):
    config = await configurations()
    print("Getting new cookies...")
    constrains = Screen(max_width = 1920, max_height = 1080)
    async with AsyncCamoufox(os = ['windows', 'macos', 'linux'],
                             screen = constrains,
                             persistent_context = True,
                             user_data_dir = 'user-data-dir',
                             i_know_what_im_doing = True,
                             config = config,
                             headless = headless,
                             humanize = True,
                             ) as browser:

        page = await browser.new_page()

        print("Starting Camoufox automation...")
        await page.goto('https://www.facebook.com')
        await page.wait_for_selector('input[name="email"]')

        # Login process
        print(f"Entering email....")
        await page.locator('input[name="email"]').nth(0).fill(EMAIL)
        await asyncio.sleep(2)
        print("Entering password....")
        await page.locator('input[name="pass"]').nth(0).fill(PASSWORD)
        await asyncio.sleep(2)
        print(f"Logging in....")
        await page.locator('button[type="submit"]').click()

        try:
            # Wait for login to complete
            await page.wait_for_selector('li.html-li', timeout = 60 * 1000)
            print("We are inside. Saving sessions.....")
        except Exception as e:
            print(f"Unxpected error occured, but your login sessions are saved.")
        await page.close()


# Retrieve session cookies from Camoufox's SQLite storage to use in a GraphQL POST request
async def load_cookies_from_sqlite(db_path):
    cookies = {}
    async with aiosqlite.connect(db_path) as db:
        async with db.execute("""
            SELECT name, value, host, path, isSecure, isHttpOnly, expiry
            FROM moz_cookies
        """) as cursor:
            async for name, value, host, path, isSecure, isHttpOnly, expiry in cursor:
                cookies[name] = value
    return cookies


# Sets the cursor for pagination, and adds a random delay between each scroll
async def automate_members(url, time_interval, max_pages=1000000):
    all_listing_dicts = []
    random_delay = await random_interval(time_interval)
    cursor = None  # Start with no cursor for first page
    page_count = 0

    while True:
        if max_pages and page_count >= max_pages:
            break

        # Get current page
        listing_dicts, next_cursor = await extract_all_members(url, cursor)

        if not listing_dicts:
            print("No more data found")
            break

        all_listing_dicts.extend(listing_dicts)
        print(f"Page {page_count + 1}: Got {len(listing_dicts)} members")

        # Check if there's a next page
        if not next_cursor:
            print("No more pages available")
            break

        cursor = next_cursor
        page_count += 1

        await asyncio.sleep(random_delay)

    return all_listing_dicts


# Grabs group ID from the URL, Facebook API generates a new cursor with each scroll; this function captures the cursor and extracts member info after every scroll
async def extract_all_members(url, cursor=None):
    member_id = ''.join(re.findall(r'\d+', url))
    """
    Get a single page of posts, returns (data, next_cursor)    """

    listing_dicts = []

    cookies = await load_cookies_from_sqlite('user-data-dir//cookies.sqlite')
    headers = {
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.7',
        'content-type': 'application/x-www-form-urlencoded',
        'origin': 'https://www.facebook.com',
        'priority': 'u=1, i',
        'referer': 'https://www.facebook.com/groups/743441212784623/members',
        'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Brave";v="138"',
        'sec-ch-ua-full-version-list': '"Not)A;Brand";v="8.0.0.0", "Chromium";v="138.0.0.0", "Brave";v="138.0.0.0"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-model': '""',
        'sec-ch-ua-platform': '"Windows"',
        'sec-ch-ua-platform-version': '"10.0.0"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'sec-gpc': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
        'x-asbd-id': '359341',
        'x-fb-friendly-name': 'GroupsCometMembersPageNewMembersSectionRefetchQuery',
        'x-fb-lsd': 'ysxmseYuGUqtKLhT9M0QEC',
        'cookie': 'datr=kBKCaO8-oahH2wDbvHLjXyZ_; ps_l=1; ps_n=1; sb=kBKCaLzPM4PkfJX-_FAHsiQW; c_user=100026981150575; xs=17%3ABrbY8Dhx9Gan-A%3A2%3A1753354918%3A-1%3A-1; fr=0dfXev0Clcq69YIjR.AWfcGiFVYHpstBinpjrUL3LBIbkkfqcj-Z4Aq9kFJm6b9omQxSI.BoghKQ..AAA.0.0.BoghKo.AWc7J1R5irINIAqTE54bgyz2ryw; wd=1600x377; presence=C%7B%22t3%22%3A%5B%5D%2C%22utc3%22%3A1753355212171%2C%22v%22%3A1%7D',
    }

    # Build variables - cursor is optional for first page
    variables = {
        "count": 10,
        "groupID": f"{member_id}",
        "recruitingGroupFilterNonCompliant": False,
        "scale": 1,
        "id": f"{member_id}"
    }

    # Add cursor if provided (for subsequent pages)
    if cursor:
        variables["cursor"] = cursor

    # These are the payloads that is required for the POST api call:
    data = {
        'av': '100026981150575',
        '__aaid': '0',
        '__user': '100026981150575',
        '__a': '1',
        '__req': 'r',
        '__hs': '20293.HYP:comet_pkg.2.1...0',
        'dpr': '1',
        '__ccg': 'EXCELLENT',
        '__rev': '1025097974',
        '__s': '8oizk1:w65mz5:sucjv3',
        '__hsi': '7530603536234448774',
        '__dyn': '7xeUjGU5a5Q1ryaxG4Vp41twWwIxu13wFwkUKewSwAyUco2qwJyE24wJwpUe8hwaG0Z82_CxS320qa321Rwwwqo462mcw5Mx62G5Usw9m1YwBgK7o6C0Mo4G17yovwRwlE-U2exi4UaEW2G1jwUBwJK14xm3y11xfxmu3W3y261eBx_wHwfC2-awLyESE2KwwwOg2cwMwrUK2K2WEjxK2B08-269wkopg6C13xecwBwWwjHDzUiBG2OUqwjVqwLwHwa211wo83KwHwOyUqxG',
        '__csr': 'ghgR3InexYn5NccsJT96NlO8Ytdb9qiHYAh4QWdiHb69ndtkjlEAABh4OcCDlEzdsLt9PRFHBbuGHKjOipa9-KpWhGrbT_AaAJ49X-lvFUgACThKhHHhGCGih5XqF29AuumAAXK8Hjyeu8GUyqdhkilkF9XyahWCABV8CayFFWDAFokQ48OuHy9pHQWwQKUlQqEhyUWcCzp8iG9HgyfCAxCm-5V9bzqxKUlUWcAVo9HwNABxCu6FEnzUnDxei7ErF2EiUmxy9AxO2a9DG3u444ah8eEW2qFG8uU4SeF0PwFyEjxu1pwMzVodpUCq58O5EK2-nwGxy78hDzEmy8lz8c86u4k3u1UwFwVzeEbE8Usx90VyQfwhox0uU1Eo1toeK0M43W1rK0ia68kUb8y056Egw7ECt1-0Po2VwrA17w3iF4Xx-1gx8wCcg24wyw43w68G1Xxy2O7Utw9y1HwkEsqw-g074e024q00KAm0A6E3Mw8kwtg1Y9oeU0TO1JK0ht1W027mt01md0ik0egw1u50Mggw4KyoKkw1hU1RA04xE-02iG2l0n40F41_zE0t-wMw14q0qG0nV07Mwmon80So7G9wea074YE7W0oC0aLAw5Kwh46o5q',
        '__hsdp': 'hW6EMuxc9acAjEUGgy8AA8FEFa8bi698y4BA48x91eytQBcwAyBawwMIJ7lAh0xawSl8CajcylpB88mpkCAO2i9GIhq8Zi4h2hiFF4iaiG9LjagGx6WJPuWCRpEsgBflm4325cNsZqe-CfjtNN3H24YPdZrqF9A68aYVaPhhRdI_A7FgMQNOqbkcYrEExmLagS8cYwCGaHgB1BiFmAehVHyCAqi6uqbaXzuxhucAXVp25ApejKDsGWG4GB8sy4dqi4kHIDa82c-yFBNGleGONl5QUZFo-6yah998FQmoVczN1H8P9BKsCRn8HgwWF5gH8wwydIXhzGfGil28phh2V8KAp4JaCtqqhAtmKJN4E8-Eww4-UlUYER0IgCu4oCu6UhxcgCU96cKajDxi4EboAFWghJn7xSEB2oojyCehm8yUOFyBl1uii7E4Ve3-um5UCchbwKy8mxO5UJ32x10iEGUmgmgcQESahk0HU8UfU42ewd6222O1OwAAgEm6P0_zUpgjF14q1KxS4ouzoS1Qxi3O4E2Fh8y7MMh040zU2ug4Ex-2q0KUK1fweC1Iwey1wwDw8C3Fwa10VDwh82DBghgB0oE7W0dTwdW3G0A82_wbyE4O0KU7q6E5O265826w63waa13wqU4q0eCwqopw44w3U80Ay9w7ew6Lw8q0fWw4ow',
        '__hblp': '09mewjEf8morwmUbU8EnwQy81bU1qEG0maU2CDK2ei1ZyECfyoaEK6E4ObDQ1KwFwdy5Ey482PwhU5S0Z8vAwrHw_DBwQwXxq2a7omwlU3qxowW0Co4Wew8a0Ao27yo4K10g4S0w8ux27EcE5yi589o4e0H86e1Rwlo-1eU1AEO2e6FE7e1Rw6nwaS2a0zE9oC1Uxe2u0Co27wvEe81WUdE16U16o2gwhU7u2K0N83jg8RVo663C2acxi5826wko2Bwh8Oewxy8cUfEbU4e3O2W16weG8xm0W812U2Cg6C6o8o3yw9u8AwCwgEaE7KbyU885efxiawm8iw40BxO0FUK6U2cCwc65E2kwQw9N0mo3ewe22iu2O2O0NUG0Go8o2Cw5SwZyU1398',
        '__sjsp': 'hW6EMuxc9acAjEUGgy8AA8FEFa8bi698y4BA48x93lHjt9j8KkOakGr5cbbgzppfNkG3e99yXcGQFRoHClaagHijGODGli2yhbAGl8FaFu-i885rCoGqryUsgB5l1iQbABUgBaqC48jgG2IEO3Kfgm8Uly4Ub4ieCUmQaoyVQufckwg8Hg9Qaxe4EOFV88EIFUTEknz99umnxeimLYEG4GByJ8gjCcVXm36FZGdxOq7efxGm8KOy9owwnyycCC9DjJbO6gxdaAl3AWgjUx1ifDBg8A5EKEyiifmCAp7nHAUW2y1rxDzOzk2N2opypUrwFgbS6QVU5m9auA4rlEs7qyEC64eUV5oybz8AEx1Oi1KK1ByoN4K1HwhA1lK5A5A3dadyAl0a-2e3-1fwd6222O1OwAAgEm1MwKF14q0OU3kxa0Gki8xYc4g0wy2q0NU0L20oZ0VDw45gB01TSE4O0ja6E',
        '__comet_req': '15',
        'fb_dtsg': 'NAft3zEVCThB9lDoQdDcOQ94EC7wFAqKyp2m6sAEwirzZVQaW6kTiLQ:17:1753354918',
        'jazoest': '25453',
        'lsd': 'ysxmseYuGUqtKLhT9M0QEC',
        '__spin_r': '1025097974',
        '__spin_b': 'trunk',
        '__spin_t': '1753355268',
        '__crn': 'comet.fbweb.CometGroupMembersRoute',
        'fb_api_caller_class': 'RelayModern',
        'fb_api_req_friendly_name': 'GroupsCometMembersPageNewMembersSectionRefetchQuery',

        # Variable for cursor (next page), and member id:
        'variables': json.dumps(variables),

        'server_timestamps': 'true',
        'doc_id': '24178555205141107',
    }

    try:
        response = await make_requests(
            'https://www.facebook.com/api/graphql/',
            headers,
            cookies,
            data
        )
        json_response = response.json()

        # Extract current page data
        raw_datas = json_response['data']['node']['new_members']['edges']

        for idx in range(len(raw_datas)):
            infos = raw_datas[idx]
            name = infos['node']['name']
            join_status = infos['join_status_text']['text']
            group_user_id = infos['node']['id']
            group_url = f"https://www.facebook.com/groups/{member_id}/user/{group_user_id}"
            profile_url = infos['node']['url']

            datas = {
                'Name': name,
                'Join Status': join_status,
                'group_url': group_url,
                'profile_url': profile_url
            }

            listing_dicts.append(datas)

        # Extract next cursor for pagination
        page_info = json_response['data']['node']['new_members']['page_info']
        next_cursor = None

        if page_info.get('has_next_page', False):
            next_cursor = page_info.get('end_cursor')

        return listing_dicts, next_cursor

    except Exception as e:
        print(f"Error occurred: {e}")
        return [], None

