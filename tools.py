from primp import AsyncClient
import pandas as pd
import random
import os


async def random_interval(interval):
    return random.uniform(3, interval + 1)


async def make_requests(url, headers, cookies, json_data):
    async with AsyncClient(impersonate = 'chrome_131', impersonate_os = 'windows') as client:
        response = await client.post(url, headers = headers, cookies = cookies, data = json_data)

        if response.status_code != 200:
            return f'Red alert: Status code = {response.status_code}!'

        return response

    return 'Failed after retries'


async def save_to_excel(dataframe, file_name):
    directory_name = "Facebook Group Member Datasets"
    os.makedirs(f"{directory_name}", exist_ok=True)

    df = pd.DataFrame(data = dataframe)
    df.to_excel(f"{directory_name}//{file_name}.xlsx", index = False)


