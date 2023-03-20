import requests
import urllib3
import concurrent.futures

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

AUTH = ("Crawler1", "BestNonencryptedPasswordEver!!!")
ENDPOINT = "https://127.0.0.1:5000"

print(requests.get(ENDPOINT + "/db/get_values", verify=False, auth=AUTH).json())


def increase_db_values(counter_id, increases):
    for i in range(increases):
        requests.post(ENDPOINT + f"/db/increase/{counter_id}", verify=False, auth=AUTH)


def increase_db_values_locking(counter_id, increases):
    for i in range(increases):
        requests.post(ENDPOINT + f"/db/increase_locking/{counter_id}", verify=False, auth=AUTH)


# reset_db_values
requests.post(ENDPOINT + "/db/reset", verify=False, auth=AUTH).json()
# print_db_values
print(requests.get(ENDPOINT + "/db/get_values", verify=False, auth=AUTH).json())

with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
    print(f"\n ... executing workers ...\n")
    for _ in range(3):
        executor.submit(increase_db_values, 1, 1000)
    for _ in range(3):
        executor.submit(increase_db_values_locking, 2, 1000)

# print_db_values
print(requests.get(ENDPOINT + "/db/get_values", verify=False, auth=AUTH).json())
