1. `uv sync`
2. `uv run bot.py`


Future notes:
- It might be worth to just use discord uuid as the primary key id of the discord account table
- Maybe create multiple pools for the requestor, i.e. a background pool and a active pool, so that command-issued requests dont have to wait on possible background tasks
- check for accidental non-silent mentions