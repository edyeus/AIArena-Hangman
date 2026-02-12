import json
import os
from typing import Any, Dict, List, Optional

import ollama

from POI.POIAgent import add_poi, remove_poi, fetch_poi_images_stream
from POI.POIModel import POIModel
from Planner import plan
from Planner.PlanOptionModel import PlanOptionModel
from Planner.RequirementModel import RequirementModel

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral")
MAX_ATTEMPTS = 2

ORCHESTRATOR_SYSTEM_PROMPT = """\
You are a travel planning assistant that classifies user messages into structured intents.

Analyze the user's message and return a JSON object with an "intents" array. Each intent has:
- "intent": one of "Points_Of_Interest", "Schedule_Requirement", "Schedule_Option", "Not_Relevant", "General_Response"
- "action": one of "add", "remove", "modify"
- "value": a string describing the content

Intent types:
- Points_Of_Interest: The user mentions a city, region, landmark, or place they want to visit (action: "add") or no longer want (action: "remove").
- Schedule_Requirement: The user specifies trip constraints like duration, dates, budget, or travel style (action: "add" to set, "remove" to drop).
- Schedule_Option: The user wants to modify an existing itinerary option (action: "add", "modify", or "remove").
- General_Response: The user asks a general travel question or makes small talk. Use "value" for a helpful response.
- Not_Relevant: The message is not related to travel planning. Use "value" for a polite redirect.

Rules:
- A single message can produce multiple intents. For example, "plan a 3 day trip to Tokyo and Osaka" produces three intents: one Schedule_Requirement for "3 day trip", and two Points_Of_Interest for "Tokyo" and "Osaka".
- Always return valid JSON matching this schema: {"intents": [{"intent": "...", "action": "...", "value": "..."}]}
- Every intent must have all three fields: "intent", "action", and "value".
- For General_Response and Not_Relevant, use action "add".
"""

# Example Orchestrator agent output (for "plan a 3 day trip to Tokyo and Osaka"):
# {
#   "intents": [
#     {
#       "intent": "Schedule_Requirement",
#       "action": "add",
#       "value": "3 day trip"
#     },
#     {
#       "intent": "Points_Of_Interest",
#       "action": "add",
#       "value": "Tokyo"
#     },
#     {
#       "intent": "Points_Of_Interest",
#       "action": "add",
#       "value": "Osaka"
#     }
#   ]
# }
#
# Notes:
# - Each intent uses "value" for all content (no separate "response" field).
# - "action" is always present for Points_Of_Interest and Schedule_Requirement.
# - Not_Relevant / General_Response intents also use "value" for their text.
#
# Example /chat response (JSON):
# {"intents":[{"action":"add","intent":"Points_Of_Interest","value":"Tokyo"},{"action":"add","intent":"Schedule_Requirement","value":"3 day trip"}],"plan":[],"pois":[{"address":"2 Chome-24-12 Shibuya, Shibuya-ku, Tokyo 150-0002, Japan","cost":"\\u00a52,000 (adult), \\u00a51,000 (children)","description":"An open-air observation deck offering 360-degree panoramic views of Tokyo from the top floors of Shibuya Scramble Square building.","geo_coordinate":{"lat":35.659,"lng":139.7004},"images":{"urls":["https://live.staticflickr.com/65535/55079269005_bf9fa4c1b7_c.jpg","https://live.staticflickr.com/65535/55077820054_4ec4e931e1_c.jpg","https://live.staticflickr.com/65535/55058801489_a565286af9_c.jpg","https://live.staticflickr.com/65535/55058730818_1fdf1538a9_c.jpg","https://live.staticflickr.com/65535/55036412099_166bbf78a4_c.jpg","https://live.staticflickr.com/65535/55035207817_d02455fd2f_c.jpg","https://live.staticflickr.com/65535/55022031031_8abb4647ae_c.jpg","https://live.staticflickr.com/65535/55021148097_033666487a_c.jpg","https://live.staticflickr.com/65535/55021118887_b6e744acc6_c.jpg","https://live.staticflickr.com/65535/55021118627_420528fae5_c.jpg"]},"name":"Shibuya Sky","opening_hours":"10:00-22:30 (last entry 21:20)","poi_type":"tourist_destination","special_instructions":"Book tickets online in advance to avoid queues. Sunset slots are most popular."},{"address":"6-1-16 Toyosu, Koto City, Tokyo 135-0061, Japan","cost":"\\u00a53,800 (adult)","description":"Immersive digital art museum where visitors walk through water and interact with light installations.","geo_coordinate":{"lat":35.654,"lng":139.7966},"images":{"urls":["https://live.staticflickr.com/65535/55078311056_6649da4333_c.jpg","https://live.staticflickr.com/65535/55078517714_4e4e46df20_c.jpg","https://live.staticflickr.com/65535/55036658647_85b45492db_c.jpg","https://live.staticflickr.com/65535/55026171561_b5ce71b865_c.jpg","https://live.staticflickr.com/65535/55026426004_4165f44669_c.jpg","https://live.staticflickr.com/65535/55025278932_c60341b939_c.jpg","https://live.staticflickr.com/65535/55005458713_a7c94e1db1_c.jpg","https://live.staticflickr.com/65535/55002912959_b6e18fdb66_c.jpg","https://live.staticflickr.com/65535/55002651656_aac31bbf9c_c.jpg","https://live.staticflickr.com/65535/55002912929_e3860074be_c.jpg"]},"name":"teamLab Planets Tokyo","opening_hours":"09:00-22:00","poi_type":"tourist_destination","special_instructions":"Shoes and socks must be removed for some exhibits. Book ahead as slots fill quickly."},{"address":"2-3-1 Asakusa, Taito City, Tokyo 111-0032, Japan","cost":"Free","description":"Tokyo's oldest and most colorful Buddhist temple, famed for its Kaminarimon Gate and vibrant shopping street.","geo_coordinate":{"lat":35.7148,"lng":139.7967},"images":{"urls":["https://live.staticflickr.com/65535/55079676772_8604a4872f_c.jpg","https://live.staticflickr.com/65535/55079437917_c145a6777f_c.jpg","https://live.staticflickr.com/65535/55077241046_222d950180_c.jpg","https://live.staticflickr.com/65535/55077440778_debbc0f7f_c.jpg","https://live.staticflickr.com/65535/55076337737_a9cb5d1891_c.jpg","https://live.staticflickr.com/65535/55075075092_2e2ea204ae_c.jpg","https://live.staticflickr.com/65535/55076233039_6ffdf4b797_c.jpg","https://live.staticflickr.com/65535/55075072727_ba13cd67dd_c.jpg","https://live.staticflickr.com/65535/55076229864_b12af2c039_c.jpg","https://live.staticflickr.com/65535/55076229804_f1c69449d6_c.jpg"]},"name":"Senso-ji Temple","opening_hours":"Temple: 06:00-17:00; grounds open 24 hours","poi_type":"tourist_destination","special_instructions":"Arrive early to avoid crowds. Nakamise Street offers street food and souvenirs leading to the temple."},{"address":"4-2-8 Shibakoen, Minato City, Tokyo 105-0011, Japan","cost":"\\u00a51,200-\\u00a53,000 depending on deck","description":"Iconic red-and-white communications tower with observation decks overlooking the city and Mount Fuji on clear days.","geo_coordinate":{"lat":35.6586,"lng":139.7454},"images":{"urls":["https://live.staticflickr.com/65535/55079676772_8604a4872f_c.jpg","https://live.staticflickr.com/65535/55080712155_554d593a02_c.jpg","https://live.staticflickr.com/65535/55080712080_73cde4db8b_c.jpg","https://live.staticflickr.com/65535/55079547200_f43a96cd14_c.jpg","https://live.staticflickr.com/65535/55078846771_d9b8876bb1_c.jpg","https://live.staticflickr.com/65535/55078120276_cde1fec6e8_c.jpg","https://live.staticflickr.com/65535/55077820054_4ec4e931e1_c.jpg","https://live.staticflickr.com/65535/55076651587_6a086355f4_c.jpg","https://live.staticflickr.com/65535/55077389494_5cbe5a6664_c.jpg","https://live.staticflickr.com/65535/55076305346_bf3c0fb1cb_c.jpg"]},"name":"Tokyo Tower","opening_hours":"09:00-23:00","poi_type":"tourist_destination","special_instructions":"Top Deck tours require advance reservation."},{"address":"1-1 Yoyogikamizonocho, Shibuya City, Tokyo 151-8557, Japan","cost":"Free","description":"A forested Shinto shrine dedicated to Emperor Meiji and Empress Shoken, located next to Yoyogi Park.","geo_coordinate":{"lat":35.6764,"lng":139.6993},"images":{"urls":["https://live.staticflickr.com/65535/55072715157_e023236719_c.jpg","https://live.staticflickr.com/65535/55068207798_acd90ec433_c.jpg","https://live.staticflickr.com/65535/55068272604_6732718523_c.jpg","https://live.staticflickr.com/65535/55068380890_374ae1fdb9_c.jpg","https://live.staticflickr.com/65535/55068380880_b0c5a3f34d_c.jpg","https://live.staticflickr.com/65535/55068272299_94d8910e5d_c.jpg","https://live.staticflickr.com/65535/55062040645_3674ff7b94_c.jpg","https://live.staticflickr.com/65535/55061862713_939445326e_c.jpg","https://live.staticflickr.com/65535/55061687251_3018983975_c.jpg","https://live.staticflickr.com/65535/55061687066_9c7be66a01_c.jpg"]},"name":"Meiji Shrine","opening_hours":"05:00-18:00 (seasonal variation)","poi_type":"tourist_destination","special_instructions":"Peaceful in the early morning; check for traditional weddings on weekends."},{"address":"Roppongi Hills Mori Tower, 6-10-1 Roppongi, Minato City, Tokyo 106-6150, Japan","cost":"\\u00a52,200-\\u00a52,800","description":"Contemporary art museum with a rooftop Sky Deck offering sweeping views of Tokyo.","geo_coordinate":{"lat":35.6605,"lng":139.7296},"images":{"urls":[]},"name":"Mori Art Museum + Tokyo City View","opening_hours":"10:00-22:00 (Sun: 10:00-20:00)","poi_type":"tourist_destination","special_instructions":"Sky Deck is weather-dependent; check for special art exhibitions."},{"address":"Sotokanda, Chiyoda, Tokyo 101-0021, Japan","cost":"Free","description":"World-famous district for electronics, anime, manga, and gaming culture, packed with stores and maid cafes.","geo_coordinate":{"lat":35.6984,"lng":139.773},"images":{"urls":["https://live.staticflickr.com/65535/55065444115_bf2cb5d434_c.jpg","https://live.staticflickr.com/65535/55058665689_9eaac6441d_c.jpg","https://live.staticflickr.com/65535/55005432351_35f5ed7ea6_c.jpg","https://live.staticflickr.com/65535/55005691024_739650cd7f_c.jpg","https://live.staticflickr.com/65535/55005426966_f806c0dc99_c.jpg","https://live.staticflickr.com/65535/55001285422_a5986db62a_c.jpg","https://live.staticflickr.com/65535/54973211996_a9fb351fef_c.jpg","https://live.staticflickr.com/65535/54935879280_ffd793281b_c.jpg","https://live.staticflickr.com/65535/54935823164_488c19fb4e_c.jpg","https://live.staticflickr.com/65535/54935526066_faf7868d99_c.jpg"]},"name":"Akihabara Electric Town","opening_hours":"Shops: Varies (10:00-21:00 typical)","poi_type":"tourist_destination","special_instructions":"Sundays feature pedestrianized main street. Explore side streets for retro gaming shops."},{"address":"4-13-17 Tsukiji, Chuo City, Tokyo 104-0045, Japan","cost":"Free (food/drink sold separately)","description":"Bustling marketplace selling fresh seafood, produce, and delicious street food.","geo_coordinate":{"lat":35.6655,"lng":139.7708},"images":{"urls":["https://live.staticflickr.com/65535/54981016926_375eaa498a_c.jpg","https://live.staticflickr.com/65535/54967153673_02e73f799c_c.jpg","https://live.staticflickr.com/65535/54966972481_d9e1734b45_c.jpg","https://live.staticflickr.com/65535/54966972431_d3e2b79275_c.jpg","https://live.staticflickr.com/65535/54966972286_170951c506_c.jpg","https://live.staticflickr.com/65535/54966078887_8bcf5e1c53_c.jpg","https://live.staticflickr.com/65535/54967277515_0b28f1f7a6_c.jpg","https://live.staticflickr.com/65535/54967153478_35206905a9_c.jpg","https://live.staticflickr.com/65535/54967229894_a6c83dda67_c.jpg","https://live.staticflickr.com/65535/54966078667_194aae3afa_c.jpg"]},"name":"Tsukiji Outer Market","opening_hours":"Typical shops: 05:00-14:00; Closed Sundays and some holidays","poi_type":"tourist_destination","special_instructions":"Arrive early for freshest food and least crowds. Many shops are closed on Sundays."},{"address":"9-83 Uenokoen, Taito City, Tokyo 110-8711, Japan","cost":"\\u00a5600 (adult), \\u00a5200 (children)","description":"Japan's oldest zoo, set within a sprawling city park featuring museums, shrines, and cherry blossoms in spring.","geo_coordinate":{"lat":35.7156,"lng":139.7714},"images":{"urls":["https://live.staticflickr.com/65535/54930288065_d51b2a422e_c.jpg","https://live.staticflickr.com/65535/54879052063_d7df109805_c.jpg","https://live.staticflickr.com/65535/54874154516_30a707348f_c.jpg","https://live.staticflickr.com/65535/54779352579_54dd1cf903_c.jpg","https://live.staticflickr.com/65535/54638056151_745dde9c96_c.jpg","https://live.staticflickr.com/65535/54634480824_70b25fd492_c.jpg","https://live.staticflickr.com/65535/54634385353_7e006db1fd_c.jpg","https://live.staticflickr.com/65535/54634150986_195f6a3ee8_c.jpg","https://live.staticflickr.com/65535/54634385348_a1cfe7b60d_c.jpg","https://live.staticflickr.com/65535/54634364554_389b969172_c.jpg"]},"name":"Ueno Zoo & Ueno Park","opening_hours":"Zoo: 09:30-17:00 (closed Mondays)","poi_type":"tourist_destination","special_instructions":"Cherry blossom season gets crowded. Ueno Park is open 24 hours."},{"address":"11 Naito-machi, Shinjuku City, Tokyo 160-0014, Japan","cost":"\\u00a5500 (adult)","description":"Beautiful landscaped garden that blends traditional Japanese, English, and French design elements.","geo_coordinate":{"lat":35.6852,"lng":139.71},"images":{"urls":["https://live.staticflickr.com/65535/55069310296_e7a7b847e5_c.jpg","https://live.staticflickr.com/65535/55069306656_2907c08f62_c.jpg","https://live.staticflickr.com/65535/55069660725_55ee8f1722_c.jpg","https://live.staticflickr.com/65535/55069491713_65286ef5a4_c.jpg","https://live.staticflickr.com/65535/55068199016_4d7f02e305_c.jpg","https://live.staticflickr.com/65535/55065209469_60803aa09f_c.jpg","https://live.staticflickr.com/65535/55061600277_e8238f3ec2_c.jpg","https://live.staticflickr.com/65535/55050137577_83f8f1b090_c.jpg","https://live.staticflickr.com/65535/55048972580_ee5d0f4eb8_c.jpg","https://live.staticflickr.com/65535/55048893584_14c3940929_c.jpg"]},"name":"Shinjuku Gyoen National Garden","opening_hours":"09:00-18:00 (varies seasonally), closed Mondays","poi_type":"tourist_destination","special_instructions":"Picnics allowed; alcohol and sports activities are prohibited."},{"address":"6-10-1 Ginza, Chuo City, Tokyo 104-0061, Japan","cost":"Free (shopping/dining optional)","description":"Luxury shopping complex with international brands, restaurants, art installations, and a rooftop garden.","geo_coordinate":{"lat":35.6692,"lng":139.7643},"images":{"urls":["https://live.staticflickr.com/65535/55010801747_9baf6e4a87_c.jpg","https://live.staticflickr.com/65535/55011687701_73e9413a1a_c.jpg","https://live.staticflickr.com/65535/55010798252_f587369bb4_c.jpg","https://live.staticflickr.com/65535/55011860573_76d9865587_c.jpg","https://live.staticflickr.com/65535/55002309896_8d5e080fde_c.jpg","https://live.staticflickr.com/65535/54983277421_ff95a95d18_c.jpg","https://live.staticflickr.com/65535/54947584594_bed5d8f0d1_c.jpg","https://live.staticflickr.com/65535/54909011665_d8e307e048_c.jpg","https://live.staticflickr.com/65535/54872533749_a10069041a_c.jpg","https://live.staticflickr.com/65535/54813826886_4c0fc9bdd3_c.jpg"]},"name":"Ginza Six","opening_hours":"Shops: 10:30-20:30, Restaurants: 11:00-23:00","poi_type":"tourist_destination","special_instructions":"Rooftop garden open to public. Check website for pop-up art events."},{"address":"1-1-10 Aomi, Koto City, Tokyo 135-0064, Japan","cost":"Free (shops, exhibits vary)","description":"Trendy bayfront island area with shopping, entertainment, and full-scale moving Gundam statue.","geo_coordinate":{"lat":35.6271,"lng":139.7764},"images":{"urls":["https://live.staticflickr.com/65535/55052132002_11aa098295_c.jpg","https://live.staticflickr.com/65535/55053212058_6694a71f46_c.jpg","https://live.staticflickr.com/65535/55053287834_a702590a6f_c.jpg","https://live.staticflickr.com/65535/55053379960_23732a7ff5_c.jpg","https://live.staticflickr.com/65535/55053379940_a5d02b20c4_c.jpg","https://live.staticflickr.com/65535/55053211953_e36237a1fa_c.jpg","https://live.staticflickr.com/65535/55053034011_7c2b90273f_c.jpg","https://live.staticflickr.com/65535/55053287759_a0bb11b1fa_c.jpg","https://live.staticflickr.com/65535/55052131852_494987b6c7_c.jpg","https://live.staticflickr.com/65535/55053211848_b54a1728ff_c.jpg"]},"name":"Odaiba (DiverCity Tokyo Plaza & Gundam Statue)","opening_hours":"10:00-21:00","poi_type":"tourist_destination","special_instructions":"Night illuminations for Gundam. Easily accessible by Yurikamome monorail."},{"address":"1-1 Maihama, Urayasu, Chiba 279-0031, Japan","cost":"\\u00a57,900-\\u00a59,400 (adult 1-day passport)","description":"Two world-renowned theme parks packed with attractions, shows, and unique Japanese entertainment.","geo_coordinate":{"lat":35.6329,"lng":139.8804},"images":{"urls":["https://live.staticflickr.com/65535/55007085776_a3ae56041b_c.jpg","https://live.staticflickr.com/65535/55007392300_05099e4dbf_c.jpg","https://live.staticflickr.com/65535/54840375311_eff2c5f55e_c.jpg","https://live.staticflickr.com/65535/54780073006_66bd198c69_c.jpg","https://live.staticflickr.com/65535/54067303212_69a8e56c64_c.jpg","https://live.staticflickr.com/65535/54067303027_132d4fc254_c.jpg","https://live.staticflickr.com/65535/54068176006_ca2b0d5738_c.jpg","https://live.staticflickr.com/65535/54068434653_5ef7cb1e5f_c.jpg","https://live.staticflickr.com/65535/54068175861_daf549c2de_c.jpg","https://live.staticflickr.com/65535/54050643392_bf0a23c830_c.jpg"]},"name":"Tokyo Disney Resort (Disneyland & DisneySea)","opening_hours":"Typically 09:00-21:00","poi_type":"tourist_destination","special_instructions":"Tickets must be purchased online in advance. Entry restrictions may apply during holidays."},{"address":"2-28-1 Asakusa, Taito City, Tokyo 111-0032, Japan","cost":"\\u00a51,200 (adult entry), rides extra","description":"Japan's oldest amusement park, blending classic carnival rides with Japanese retro charm.","geo_coordinate":{"lat":35.716,"lng":139.7941},"images":{"urls":["https://live.staticflickr.com/65535/55061532225_e92c44fc5f_c.jpg","https://live.staticflickr.com/65535/55056063484_d378791346_c.jpg","https://live.staticflickr.com/65535/55020936775_18f9173f54_c.jpg","https://live.staticflickr.com/65535/55020799593_d27e1c6674_c.jpg","https://live.staticflickr.com/65535/55020936745_51db1f48af_c.jpg","https://live.staticflickr.com/65535/55020799603_5e09d0c75a_c.jpg","https://live.staticflickr.com/65535/55020617056_48a1bb4fd8_c.jpg","https://live.staticflickr.com/65535/55020877339_cf43f52737_c.jpg","https://live.staticflickr.com/65535/54864860533_aa493650b9_c.jpg","https://live.staticflickr.com/65535/54777950147_8e02a944ba_c.jpg"]},"name":"Asakusa Hanayashiki","opening_hours":"10:00-19:00 (varies by season)","poi_type":"tourist_destination","special_instructions":"Great for families and nostalgia lovers. Located near Senso-ji."},{"address":"1 Chome Jingumae, Shibuya City, Tokyo 150-0001, Japan","cost":"Free","description":"Trendy, colorful pedestrian street famous for youth fashion, crepes, and unique pop culture shops.","geo_coordinate":{"lat":35.6703,"lng":139.7048},"images":{"urls":["https://live.staticflickr.com/65535/55048530827_dfa3cbb396_c.jpg","https://live.staticflickr.com/65535/55034632814_5d54f07d77_c.jpg","https://live.staticflickr.com/65535/55032278662_f4913b3c35_c.jpg","https://live.staticflickr.com/65535/55032278657_7f67f1c0d0_c.jpg","https://live.staticflickr.com/65535/55032278642_4a61c6ebdb_c.jpg","https://live.staticflickr.com/65535/55033182451_c3917c774c_c.jpg","https://live.staticflickr.com/65535/55002298638_50553425ac_c.jpg","https://live.staticflickr.com/65535/55001246117_e694c27b07_c.jpg","https://live.staticflickr.com/65535/55002298548_dbd15421b1_c.jpg","https://live.staticflickr.com/65535/55002132806_bc0b149d55_c.jpg"]},"name":"Harajuku Takeshita Street","opening_hours":"Shops typically open 11:00-20:00","poi_type":"tourist_destination","special_instructions":"Visit on weekdays to avoid extreme crowds. Best place for quirky street snacks."},{"address":"1 Chome Kabukicho, Shinjuku City, Tokyo 160-0021, Japan","cost":"Cover charges at bars (\\u00a5500-\\u00a51,000 typical)","description":"Historic alleyways packed with tiny themed bars and izakaya, a landmark of Tokyo nightlife.","geo_coordinate":{"lat":35.6944,"lng":139.7031},"images":{"urls":["https://live.staticflickr.com/65535/55065059402_0905709159_c.jpg","https://live.staticflickr.com/65535/55065059407_1e54caabb9_c.jpg","https://live.staticflickr.com/65535/55065059397_64232a4c39_c.jpg","https://live.staticflickr.com/65535/55065960926_c18a9fa34b_c.jpg","https://live.staticflickr.com/65535/55060402831_fe84cc68e3_c.jpg","https://live.staticflickr.com/65535/55054406156_295263c537_c.jpg","https://live.staticflickr.com/65535/55036426327_f871b1827a_c.jpg","https://live.staticflickr.com/65535/55034372670_a6829678a2_c.jpg","https://live.staticflickr.com/65535/55034034691_abfed0ed92_c.jpg","https://live.staticflickr.com/65535/55034211863_2740e4986a_c.jpg"]},"name":"Shinjuku Golden Gai","opening_hours":"Bars: usually 19:00-early morning","poi_type":"tourist_destination","special_instructions":"Some bars welcome foreigners; others are locals-only. Look for English menus."},{"address":"13-9 Uenokoen, Taito City, Tokyo 110-8712, Japan","cost":"\\u00a51,000 (adult)","description":"Japan's premier museum, showcasing art and artifacts from ancient to modern times.","geo_coordinate":{"lat":35.7188,"lng":139.7769},"images":{"urls":["https://live.staticflickr.com/65535/55079771745_60c34cde5d_c.jpg","https://live.staticflickr.com/65535/55068278078_29db31b841_c.jpg","https://live.staticflickr.com/65535/55061182875_2b9a596a73_c.jpg","https://live.staticflickr.com/65535/55052496948_ebc721e20e_c.jpg","https://live.staticflickr.com/65535/55052231466_59f247d9ab_c.jpg","https://live.staticflickr.com/65535/55047049509_a13e2ee0ff_c.jpg","https://live.staticflickr.com/65535/55039580234_5eb135d502_c.jpg","https://live.staticflickr.com/65535/55039504628_c68e53bd31_c.jpg","https://live.staticflickr.com/65535/55038419152_3e93317790_c.jpg","https://live.staticflickr.com/65535/55038419072_46ef693012_c.jpg"]},"name":"Tokyo National Museum","opening_hours":"09:30-17:00, closed Mondays","poi_type":"tourist_destination","special_instructions":"Museum complex features multiple buildings and special exhibitions."},{"address":"1 Chome Mukojima, Sumida City, Tokyo 131-0033, Japan","cost":"Free","description":"Recently-opened riverside walkway connecting Asakusa to Tokyo Skytree, lined with cafes and boutiques.","geo_coordinate":{"lat":35.7101,"lng":139.7993},"images":{"urls":[]},"name":"Sumida River Walk & Tokyo Mizumachi","opening_hours":"Open 24 hours (shops/cafes: 08:00-21:00)","poi_type":"tourist_destination","special_instructions":"Excellent spot for Tokyo Skytree photos. Trendy area for riverside strolls."},{"address":"1-1 Hamarikyuteien, Chuo City, Tokyo 104-0046, Japan","cost":"\\u00a5300 (adult)","description":"Beautiful Edo-period garden with seawater ponds and a historic teahouse.","geo_coordinate":{"lat":35.6618,"lng":139.7621},"images":{"urls":["https://live.staticflickr.com/65535/55037632794_4c2277025f_c.jpg","https://live.staticflickr.com/65535/55031744081_8fcf5b3bd0b_c.jpg","https://live.staticflickr.com/65535/54991141350_4d0c9bac15_c.jpg","https://live.staticflickr.com/65535/54990847646_0d4397870a_c.jpg","https://live.staticflickr.com/65535/54991107059_81eb3864af_c.jpg","https://live.staticflickr.com/65535/54990682721_e6964782e7_c.jpg","https://live.staticflickr.com/65535/54990682636_9d0b18e6eb_c.jpg","https://live.staticflickr.com/65535/54989800587_479dba39f1_c.jpg","https://live.staticflickr.com/65535/54990974070_3171afd5cc_c.jpg","https://live.staticflickr.com/65535/54954872489_e1fe88493d_c.jpg"]},"name":"Hamarikyu Gardens","opening_hours":"09:00-17:00","poi_type":"tourist_destination","special_instructions":"Can access directly via Sumida River cruise. Enjoy matcha in the teahouse."}],"requirements":[{"description":"3 day trip","priority":"preferred"}]}

INTENT_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "intents": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "intent": {
                        "type": "string",
                        "enum": [
                            "Points_Of_Interest",
                            "Schedule_Requirement",
                            "Schedule_Option",
                            "Not_Relevant",
                            "General_Response",
                        ],
                    },
                    "action": {
                        "type": "string",
                        "enum": ["add", "remove", "modify"],
                    },
                    "value": {"type": "string"},
                },
                "required": ["intent", "action", "value"],
            },
        }
    },
    "required": ["intents"],
}


def analyze_intents(
    message: str,
    existing_pois: Any = None,
    existing_requirements: Any = None,
    existing_plan: Any = None,
) -> Dict[str, Any]:
    print(f"[Orchestrator] analyze_intents: {message}")
    last_error: Optional[str] = None
    for attempt in range(1, MAX_ATTEMPTS + 1):
        output_text = _call_orchestrator_agent(message)
        print(f"[Orchestrator] intent raw response: {output_text}")

        try:
            payload = json.loads(output_text)
        except json.JSONDecodeError as exc:
            last_error = f"invalid_json: {exc}"
            continue

        errors = _validate_intents(payload)
        if not errors:
            print("[Orchestrator] intent validation successful")
            return _build_and_plan(
                payload,
                existing_pois=existing_pois,
                existing_requirements=existing_requirements,
                existing_plan=existing_plan,
            )

        last_error = "; ".join(errors)

    print(f"[Orchestrator] intent validation failed: {last_error}")
    return {
        "intents": [
            {"intent": "General_Response", "value": "We're working on it."}
        ],
        "pois": existing_pois if isinstance(existing_pois, list) else [],
        "requirements": existing_requirements if isinstance(existing_requirements, list) else [],
        "plan": existing_plan if isinstance(existing_plan, list) else [],
    }


def analyze_intents_stream(
    message: str,
    existing_pois: Any = None,
    existing_requirements: Any = None,
    existing_plan: Any = None,
):
    """Generator that yields progressive updates as dicts during intent analysis and planning."""
    try:
        print(f"[Orchestrator] analyze_intents_stream: {message}")
        last_error: Optional[str] = None

        # Step 1: Call orchestrator agent to classify intents
        for attempt in range(1, MAX_ATTEMPTS + 1):
            output_text = _call_orchestrator_agent(message)
            print(f"[Orchestrator] intent raw response: {output_text}")

            try:
                payload = json.loads(output_text)
            except json.JSONDecodeError as exc:
                last_error = f"invalid_json: {exc}"
                continue

            errors = _validate_intents(payload)
            if not errors:
                print("[Orchestrator] intent validation successful")
                break

            last_error = "; ".join(errors)
        else:
            # Step 2: Validation failed after retries
            print(f"[Orchestrator] intent validation failed: {last_error}")
            yield {
                "type": "error",
                "message": f"Intent validation failed: {last_error}"
            }
            return

        intents = payload.get("intents", [])

        # Step 3: Yield classified intents
        yield {"type": "intents", "data": intents}

        # Step 4: Hydrate existing state from client data
        if existing_pois is not None:
            poi_model = POIModel.from_json(
                existing_pois, require_images=False, allow_empty=True)
        else:
            poi_model = POIModel(items=[])

        if existing_requirements is not None:
            requirement_model = RequirementModel.from_json(
                existing_requirements, allow_empty=True)
        else:
            requirement_model = RequirementModel(items=[])

        if existing_plan is not None:
            plan_model = PlanOptionModel.from_json(existing_plan, allow_empty=True)
        else:
            plan_model = None

        # Classify intents into buckets
        poi_add = [i for i in intents if i.get(
            "intent") == "Points_Of_Interest" and i.get("action") == "add"]
        poi_remove = [i for i in intents if i.get(
            "intent") == "Points_Of_Interest" and i.get("action") == "remove"]
        req_add = [i for i in intents if i.get(
            "intent") == "Schedule_Requirement" and i.get("action") == "add"]
        req_remove = [i for i in intents if i.get(
            "intent") == "Schedule_Requirement" and i.get("action") == "remove"]

        # Step 5: If no actionable intents, yield unchanged state and done
        has_actionable = poi_add or poi_remove or req_add or req_remove
        if not has_actionable:
            yield {"type": "pois", "data": poi_model.to_list()}
            yield {"type": "requirements", "data": requirement_model.to_list()}
            yield {"type": "plan", "data": plan_model.to_list() if plan_model else []}
            yield {"type": "done"}
            return

        # Step 6: Process POI removes
        for intent in poi_remove:
            poi_name = intent.get("value", "")
            if poi_name:
                poi_model = remove_poi(poi_model.to_list(), poi_name)

        # Step 7: Process POI adds (skip images — they stream later)
        existing_poi_names = {item.poi.name for item in poi_model.items}
        for intent in poi_add:
            poi_name = intent.get("value", "")
            if poi_name:
                poi_model = add_poi(poi_model.to_list(), poi_name, skip_images=True)

        # Step 8: Yield POIs
        yield {"type": "pois", "data": poi_model.to_list()}
        print(
            f"[Orchestrator] poi: {json.dumps(poi_model.to_list(), ensure_ascii=True)}")

        # Step 9: Process requirement removes and adds
        for intent in req_remove:
            desc = intent.get("value", "")
            if desc:
                requirement_model = RequirementModel.remove_requirement(
                    requirement_model, desc)

        for intent in req_add:
            desc = intent.get("value", "")
            if desc:
                new_reqs = RequirementModel.from_json([{"description": desc}])
                requirement_model = RequirementModel(
                    requirement_model.items + new_reqs.items)

        # Step 10: Yield requirements
        yield {"type": "requirements", "data": requirement_model.to_list()}
        print(
            f"[Orchestrator] requirements: {json.dumps(requirement_model.to_list(), ensure_ascii=True)}")

        # Step 11: Call the planner
        planner_result = plan(poi_model, requirement_model,
                              existing_plan=plan_model)

        # Step 12: Yield plan
        yield {"type": "plan", "data": planner_result.to_list()}

        # Step 13: Stream images for newly added POIs
        new_pois = POIModel([item for item in poi_model.items if item.poi.name not in existing_poi_names])
        if new_pois.items:
            for poi_name, image_urls in fetch_poi_images_stream(new_pois):
                yield {"type": "poi_images", "data": {"name": poi_name, "images": {"urls": image_urls}}}

        # Step 14: Yield done
        yield {"type": "done"}

    except Exception as exc:
        print(f"[Orchestrator] stream error: {exc}")
        yield {"type": "error", "message": str(exc)}


def _call_orchestrator_agent(message: str) -> str:
    response = ollama.chat(
        model=OLLAMA_MODEL,
        messages=[
            {"role": "system", "content": ORCHESTRATOR_SYSTEM_PROMPT},
            {"role": "user", "content": message},
        ],
        format="json",
        options={"temperature": 0.1},
    )
    return response["message"]["content"]


def _validate_intents(payload: Any) -> List[str]:
    errors: List[str] = []
    if not isinstance(payload, dict):
        return ["payload must be an object"]
    intents = payload.get("intents")
    if not isinstance(intents, list) or not intents:
        return ["intents must be a non-empty list"]

    for idx, intent in enumerate(intents):
        if not isinstance(intent, dict):
            errors.append(f"intent[{idx}] must be an object")
            continue
        intent_type = intent.get("intent")
        action = intent.get("action")
        value = intent.get("value")

        if intent_type not in {
            "Points_Of_Interest",
            "Schedule_Requirement",
            "Schedule_Option",
            "Not_Relevant",
            "General_Response",
        }:
            errors.append(f"intent[{idx}].intent is invalid")
            continue

        if not isinstance(value, str) or not value:
            errors.append(f"intent[{idx}].value must be a non-empty string")

        if intent_type == "Points_Of_Interest":
            if action not in {"add", "remove"}:
                errors.append(f"intent[{idx}].action must be add/remove")
        elif intent_type == "Schedule_Requirement":
            if action not in {"add", "remove"}:
                errors.append(f"intent[{idx}].action must be add/remove")
        elif intent_type == "Schedule_Option":
            if action not in {"add", "modify", "remove"}:
                errors.append(
                    f"intent[{idx}].action must be add/modify/remove")
        elif intent_type in ("Not_Relevant", "General_Response"):
            # Agent uses "value" for all content; "response" is not produced.
            if not isinstance(value, str) or not value:
                errors.append(
                    f"intent[{idx}].value is required for {intent_type}"
                )

    return errors


def _build_and_plan(
    payload: Dict[str, Any],
    existing_pois: Any = None,
    existing_requirements: Any = None,
    existing_plan: Any = None,
) -> Dict[str, Any]:
    intents = payload.get("intents", [])

    # Classify intents into buckets
    poi_add = [i for i in intents if i.get(
        "intent") == "Points_Of_Interest" and i.get("action") == "add"]
    poi_remove = [i for i in intents if i.get(
        "intent") == "Points_Of_Interest" and i.get("action") == "remove"]
    req_add = [i for i in intents if i.get(
        "intent") == "Schedule_Requirement" and i.get("action") == "add"]
    req_remove = [i for i in intents if i.get(
        "intent") == "Schedule_Requirement" and i.get("action") == "remove"]

    # Hydrate existing state from client data (or start empty)
    if existing_pois is not None:
        poi_model = POIModel.from_json(
            existing_pois, require_images=False, allow_empty=True)
    else:
        poi_model = POIModel(items=[])

    if existing_requirements is not None:
        requirement_model = RequirementModel.from_json(
            existing_requirements, allow_empty=True)
    else:
        requirement_model = RequirementModel(items=[])

    if existing_plan is not None:
        plan_model = PlanOptionModel.from_json(existing_plan, allow_empty=True)
    else:
        plan_model = None

    # If no actionable intents, return unchanged state immediately
    has_actionable = poi_add or poi_remove or req_add or req_remove
    if not has_actionable:
        return {
            "intents": intents,
            "pois": poi_model.to_list(),
            "requirements": requirement_model.to_list(),
            "plan": plan_model.to_list() if plan_model else [],
        }

    # Process removes before adds
    for intent in poi_remove:
        poi_name = intent.get("value", "")
        if poi_name:
            poi_model = remove_poi(poi_model.to_list(), poi_name)

    for intent in req_remove:
        desc = intent.get("value", "")
        if desc:
            requirement_model = RequirementModel.remove_requirement(
                requirement_model, desc)

    for intent in poi_add:
        poi_name = intent.get("value", "")
        if poi_name:
            poi_model = add_poi(poi_model.to_list(), poi_name)

    for intent in req_add:
        desc = intent.get("value", "")
        if desc:
            new_reqs = RequirementModel.from_json([{"description": desc}])
            requirement_model = RequirementModel(
                requirement_model.items + new_reqs.items)

    print(
        f"[Orchestrator] poi: {json.dumps(poi_model.to_list(), ensure_ascii=True)}")
    print(
        f"[Orchestrator] requirements: {json.dumps(requirement_model.to_list(), ensure_ascii=True)}")

    planner_result = plan(poi_model, requirement_model,
                          existing_plan=plan_model)
    return {
        "intents": intents,
        "pois": poi_model.to_list(),
        "requirements": requirement_model.to_list(),
        "plan": planner_result.to_list(),
    }
