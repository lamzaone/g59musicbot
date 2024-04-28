import discord
import json
import os
from config import config


def get_queue(guild_id):
    with open(f"{config.queues}", "r") as f:
        queues = json.load(f)
    return queues.get(str(guild_id), {})

def update_queue(guild_id, queue):
    with open(f"{config.queues}", "r") as f:
        queues = json.load(f)
    queues[str(guild_id)] = queue
    with open(f"{config.queues}", "w") as f:
        json.dump(queues, f, indent=4)

def next_song(guild_id):
    queue = get_queue(guild_id)
    if len(queue) > 0:
        song = queue.pop(0)
        update_queue(guild_id, queue)
    return song