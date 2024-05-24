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

# def next_random_song(guild_id):
#     queue = get_queue(guild_id)
#     if len(queue) > 0:
#         song = queue.pop(0)
#         update_queue(guild_id, queue)
#     return song
def repeat_queue(guild_id, playing_song):
    queue = get_queue(guild_id)
    np_song = {'title': playing_song['title'], 'url': playing_song['original_url']}
    if len(queue) > 0:
        song = queue.pop(0)
        queue.append(np_song)
        update_queue(guild_id, queue)
    return song