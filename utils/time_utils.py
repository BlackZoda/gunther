from datetime import datetime
import pytz
from dateutil.relativedelta import relativedelta
import openai
from config import OPEN_AI

def return_time():
    oslo_tz = pytz.timezone('Europe/Oslo')
    la_tz = pytz.timezone('America/Los_Angeles')
    la_tz_33 = datetime.now(la_tz) - relativedelta(years=92)
    oslo_time = datetime.now(oslo_tz).strftime('%Y-%m-%d %H:%M')
    # la_time = datetime.now(la_tz).strftime('_%Y-%m-%d %H:%M')
    la_time_33 = la_tz_33.strftime('%Y-%m-%d %H:%M')
    no_tabs = "\t" * 4
    norway = f"🇳🇴 **Time in the Socialist State of Frozen Oil:**{no_tabs} 🐧 `{oslo_time}`"
    us_tabs = "\t" * 1
    la = f"🇺🇸 **Time in the Consumer Oligarchy of Trumpistan:**{us_tabs}🪖 `{la_time_33}`"
    return norway + "\n" + la

openai.api_key = OPEN_AI

async def generate_history():
    la_tz = pytz.timezone('America/Los_Angeles')
    la_tz_33 = datetime.now(la_tz) - relativedelta(years=92)
    la_date_33 = la_tz_33.strftime("%B %d, %Y")
    prompt = f"Give me a relevant historical event that happened on or around {la_date_33}. Preferably related to fascism and/or nazi-germany, and write a fun comparison to the current political situation in the USA. You should keep the answer short enough to fit within a single discord message, and end it with a sardonic homage to the Consumer Oligarchy of Trumpistan"
    system = f"You are a satirical and sarcastic history professor making fun of the Trump administration by comparing it to the historical absurdities from the interwar period in Europe"
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt}
            ]
        )
        reply = response.choices[0].message['content']
    except Exception as e:
        reply = f"Error fetching data from OpenAI: {e}"
    return reply