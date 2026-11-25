# Source guide

All primary responses and exact retrieval timestamps are indexed in `data/sources.csv` and the raw JSONL ledger.

## Official event and payout sources

| Event | Official standings page | Published payout schedule | Latest completed round |
| --- | --- | --- | ---: |
| atlanta-friday | [511646](https://locator.riftbound.uvsgames.com/events/511646) | [Atlanta](https://uvsgames.com/rq-atlanta-schedule/) | 6 |
| atlanta-sunday | [513852](https://locator.riftbound.uvsgames.com/events/513852) | [Atlanta](https://uvsgames.com/rq-atlanta-schedule/) | 6 |
| atlanta-saturday | [513817](https://locator.riftbound.uvsgames.com/events/513817) | [Atlanta](https://uvsgames.com/rq-atlanta-schedule/) | 10 |
| sydney-friday | [559263](https://locator.riftbound.uvsgames.com/events/559263) | [Sydney](https://uvsgames.com/rq-sydney-schedule/) | 5 |
| sydney-saturday | [568005](https://locator.riftbound.uvsgames.com/events/568005) | [Sydney](https://uvsgames.com/rq-sydney-schedule/) | 10 |
| sydney-sunday | [580432](https://locator.riftbound.uvsgames.com/events/580432) | [Sydney](https://uvsgames.com/rq-sydney-schedule/) | 6 |
| vancouver-friday | [602175](https://locator.riftbound.uvsgames.com/events/602175) | [Vancouver](https://uvsgames.com/rq-vancouver-schedule/) | 5 |
| vancouver-saturday | [613450](https://locator.riftbound.uvsgames.com/events/613450) | [Vancouver](https://uvsgames.com/rq-vancouver-schedule/) | 10 |
| vancouver-sunday | [625573](https://locator.riftbound.uvsgames.com/events/625573) | [Vancouver](https://uvsgames.com/rq-vancouver-schedule/) | 6 |
| utrecht-friday | [663545](https://locator.riftbound.uvsgames.com/events/663545) | [Utrecht](https://uvsgames.com/rq-utrecht-schedule/) | 5 |
| utrecht-saturday | [667933](https://locator.riftbound.uvsgames.com/events/667933) | [Utrecht](https://uvsgames.com/rq-utrecht-schedule/) | 10 |
| utrecht-sunday | [668004](https://locator.riftbound.uvsgames.com/events/668004) | [Utrecht](https://uvsgames.com/rq-utrecht-schedule/) | 6 |
| hartford-friday | [683274](https://locator.riftbound.uvsgames.com/events/683274) | [Hartford](https://uvsgames.com/rq-hartford-schedule/) | 5 |
| hartford-saturday | [683480](https://locator.riftbound.uvsgames.com/events/683480) | [Hartford](https://uvsgames.com/rq-hartford-schedule/) | 10 |
| hartford-sunday | [683485](https://locator.riftbound.uvsgames.com/events/683485) | [Hartford](https://uvsgames.com/rq-hartford-schedule/) | 6 |
| barcelona-friday | [857745](https://locator.riftbound.uvsgames.com/events/857745) | [Barcelona](https://uvsgames.com/rq-barcelona-schedule/) | 5 |
| barcelona-saturday | [857824](https://locator.riftbound.uvsgames.com/events/857824) | [Barcelona](https://uvsgames.com/rq-barcelona-schedule/) | 10 |
| barcelona-sunday | [857858](https://locator.riftbound.uvsgames.com/events/857858) | [Barcelona](https://uvsgames.com/rq-barcelona-schedule/) | 6 |
| singapore-friday | [889707](https://locator.riftbound.uvsgames.com/events/889707) | [Singapore](https://uvsgames.com/rq-singapore-schedule/) | 6 |
| singapore-saturday | [891984](https://locator.riftbound.uvsgames.com/events/891984) | [Singapore](https://uvsgames.com/rq-singapore-schedule/) | 8 |
| singapore-sunday | [892029](https://locator.riftbound.uvsgames.com/events/892029) | [Singapore](https://uvsgames.com/rq-singapore-schedule/) | 6 |
| los-angeles-friday | [892089](https://locator.riftbound.uvsgames.com/events/892089) | [Los Angeles](https://uvsgames.com/rq-los-angeles-schedule/) | 5 |
| los-angeles-saturday | [892222](https://locator.riftbound.uvsgames.com/events/892222) | [Los Angeles](https://uvsgames.com/rq-los-angeles-schedule/) | 7 |
| los-angeles-sunday | [892341](https://locator.riftbound.uvsgames.com/events/892341) | [Los Angeles](https://uvsgames.com/rq-los-angeles-schedule/) | 6 |

The public API base is `https://api.cloudflare.riftbound.uvsgames.com/hydraproxy/api/v2`.
Read-only routes used: `/events/{id}/`, `/events/{id}/registrations/`,
`/tournament-rounds/{round_id}/standings/paginated/`, and `/tournament-rounds/{round_id}/matches/paginated/`.
Page-specific URLs, raw response hashes, and row pointers are preserved in the CSVs.

## Historical policy and secondary leads

- [discovery](https://openrift.app/meta/pre-regional-challenge-rq-atlanta-friday-1pm-2026), retrieved 2026-11-24T23:40:01.375518+00:00; raw `data/raw/objects/640924790ac44f61b5b2b828f0b4cd6720f35f2863eb87ba0e0c1586a7c1470f.html`.
- [historical_tournament_rules](https://cmsassets.rgpub.io/sanity/files/dsfx7636/news_live/d77651bcaa7ca5a5b41a0ac0ea8112725a635680.pdf), retrieved 2026-11-24T23:41:06.727032+00:00; raw `data/raw/objects/5ff49739907be52f1256606d3c74743f620bafe50ca0bf3d7490c155fe404793.bin`.
- [community_split_report](https://www.reddit.com/r/riftboundtcg/comments/1vxb7j8/regionals_in_singapore_solo/), retrieved 2026-11-24T23:50:44.833999+00:00; raw `data/raw/objects/aae3b0d8e85adbbab2d24e9baed84b4b43c924d63e4d13ac07f3c876e7042fd7.html`.
- [historical_rules_discovery](https://riftref.org/pages/riftbound-tournament-rules-2026-07-16/), retrieved 2026-11-24T23:56:11.493244+00:00; raw `data/raw/objects/f258f4a667654dd403f05ea6b7286ca8ffb2c7b4172ce07c3b07bd0cf4f33a8f.html.gz`.

The Reddit HTTP snapshot is a JavaScript challenge, not the post contents; its HTTP 200 is not successful content verification.
The separately preserved web-search excerpt in `data/observations.json` corroborates only a reported split practice.
Third-party sites were discovery leads; official standings/payout sources own all normalized calculations.
