import redis

pool = redis.ConnectionPool(host='deimos.lab.ds', port=6379, db=0, password="CAC4AqAu-ha.8c37CA")
redis = redis.Redis(connection_pool=pool)
#user_ids = [0, 110, 109, 107, 106, 104, 103, 102, 101, 100, 99, 98, 97, 96, 95, 94, 93, 92, 91, 90, 89, 88, 87, 86, 84,
#            83, 82, 81, 89, 79, 77, 76, 75, 74, 73, 72, 71, 70, 69, 68, 67, 66, 65, 64, 63, 61, 60, 59, 58, 57, 56, 55,
#            54, 53, 52, 51, 50, 49, 48, 47, 45, 44, 43, 42, 41, 40, 39, 38, 37, 36, 35, 34, 33, 32, 31, 29, 28, 27, 26,
#            25, 24, 23, 22, 21, 20, 19, 18, 17, 16]
user_ids = [17]

def purge_old_entries():
    keys = {}
    keys_ttl = {}
    for i in user_ids:
        print(i)
        tmp_keys = redis.keys(f'USER_*_{i}')
        key_ttl = 0
        for key in tmp_keys:
            r_ttl = redis.ttl(key)
            key_ttl += r_ttl
            if r_ttl > 15768000:
                print("-", end="")
                continue
            pipeline = redis.pipeline()
            dta_k = key.replace(b'USER_', b'').split(b'_')[0]
            print(".", end="")
            pipeline.expire(dta_k, 1)
            pipeline.expire(key, 1)
            pipeline.execute()
        try:
            keys_ttl[i] = int(key_ttl / len(tmp_keys))
        except ZeroDivisionError:
            keys_ttl[i] = -1
        keys[i] = len(tmp_keys)

    print(keys)
    print(keys_ttl)


def clear_images():
    keys = redis.keys("*")
    for key in keys:
        pipeline = redis.pipeline()
        # print(key)
        if b"-" in key:
            print("-", end="")
            continue
        r_ttl = redis.ttl(key)
        if r_ttl > 15768000:
            continue
        pipeline.expire(key, 1)
        pipeline.execute()
        print(".", end="")


purge_old_entries()
#clear_images()
