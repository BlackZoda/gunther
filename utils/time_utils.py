from datetime import datetime
import pytz
from dateutil.relativedelta import relativedelta
import openai
from config import OPEN_AI

oslo_tz = pytz.timezone('Europe/Oslo')
la_tz = pytz.timezone('America/Los_Angeles')
la_tz_33 = datetime.now(la_tz) - relativedelta(years=92)
oslo_time = datetime.now(oslo_tz).strftime('%Y-%m-%d %H:%M')
la_time = datetime.now(la_tz).strftime('_%Y-%m-%d %H:%M')
la_time_33 = la_tz_33.strftime('%Y-%m-%d %H:%M')
la_date_33 = la_tz_33.strftime("%B %d, %Y")

openai.api_key = OPEN_AI
    
def return_time():
    no_tabs = "\t" * 4
    norway = f"🇳🇴 **Time in the Socialist State of Frozen Oil:**{no_tabs}🐧 `{oslo_time}`"
    us_tabs = "\t" * 1
    la = f"🇺🇸 **Time in the Consumer Oligarchy of Trumpistan:**{us_tabs}ϟϟ `{la_time_33}`"
    return norway + "\n" + la

async def generate_history():
    prompt = f"Give me some relevant historical events that happened on or around {la_date_33}. Preferably related to fascism and/or nazi-germany, and write a fun comparison to the current political situation in the USA."
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a satirical history professor making fun of the Trump administration"},
                {"role": "user", "content": prompt}
            ]
        )
        reply = response.choices[0].message['content']
    except Exception as e:
        reply = f"Error fetching data from OpenAI: {e}"
    return reply