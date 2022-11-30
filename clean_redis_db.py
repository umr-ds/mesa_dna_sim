import redis

pool = redis.ConnectionPool(host='10.0.1.207', port=6379, db=0, password="CAC4AqAu-ha.8c37CA")
redis = redis.Redis(connection_pool=pool)
user_ids = [0]


def purge_old_entries():
    keys = {}
    keys_ttl = {}
    for i in user_ids:
        print(i)
        tmp_keys = redis.keys(f'USER_*_' + str(i))
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
        keys_ttl[i] = int(key_ttl / len(tmp_keys))
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


clear_images()
