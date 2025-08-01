# SpamKick Discord Bot

A _very_ simple Discord bot in Python that kicks people if they post messages in too many channels within a too small time window, and deletes those messages.


## Running directly

First, copy the `.env.sample` file to `.env`, and fill it out.

Then install dependencies then run `main.py`:
```bash
pip install -r requirements.txt
./run.sh
```

## Running with Docker

First, get the `.env.sample` file, and fill it out.

Then, run the bot with:

```bash
docker run --rm --env-file=[path_to_dotenv] --name spamkick-discordbot max480/spamkick
```