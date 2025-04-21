from datetime import datetime
import pytz
from dateutil.relativedelta import relativedelta
import openai
from config import OPEN_AI

oslo_tz = pytz.timezone('Europe/Oslo')
la_tz = pytz.timezone('America/Los_Angeles')
la_tz_33 = datetime.now(la_tz) - relativedelta(years=92)
oslo_time = datetime.now(oslo_tz).strftime('_%Y-%m-%d_\t%H:%M')
la_time = datetime.now(la_tz).strftime('_%Y-%m-%d_\t%H:%M')
la_time_33 = la_tz_33.strftime('_%Y-%m-%d_\t%H:%M')
la_date_33 = la_tz_33.strftime("%B %d, %Y")

openai.api_key = OPEN_AI
    
def return_time():
    return f"🇳🇴 **Time in Norway:**\t\t\t{oslo_time}\n🇺🇸 **Time in Trumpistan:**\t{la_time_33}"

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