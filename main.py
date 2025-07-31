from scraper import automate_members, save_login_session, extract_all_members
from tools import save_to_excel
from playsound import playsound
import asyncio
import time


async def main():

    # First run this;
    return await save_login_session(False)
    member_url = ""

    # random interval between 3 and 8 seconds:
    time_interval = 8
    file_name = ""
    member_datas = await automate_members(member_url, time_interval)
    return await save_to_excel(member_datas, f"{file_name} members")


if __name__ == "__main__":
    start_time = time.time()
    results = asyncio.run(main())
    print(results)
    end_time = time.time()
    execution_time = round(end_time - start_time, 2)
    playsound('c-chord.mp3')
    print(f"\nExecution time:\n---------------\n{execution_time} second/s.\n{round(execution_time / 60, 2)} minute/s.\n{round(execution_time / 3600, 2)} hour/s")

