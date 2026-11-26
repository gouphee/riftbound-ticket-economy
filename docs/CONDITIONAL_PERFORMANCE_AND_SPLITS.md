# Conditional performance and historical prize splits

Research date: **2026-11-26, America/Indianapolis**. This is an additive analysis; prior Phase 2–5 results are preserved.

The reward for reaching a strong checkpoint is much lower in Vegas under the stated models. But **difficulty of reaching a record, cut conversion, expected reward and a guaranteed award are different quantities**. The cumulative difficulty comparison reverses for a sufficiently strong hypothetical player. Unknown historical sharing practices prevent a universal claim about actual receipts.

## The checkpoints are before the final Swiss round

All eight historical Saturday schedules specify **seven Swiss rounds then Top 8**. Therefore 5–1 and 6–0 refer here to the end of Round 6, entering Round 7; they are not final Swiss records. Vegas 8–2, 9–1 and 10–0 refer to the end of Round 10, entering Round 11. They are useful requested comparisons, not matched finishing percentiles.

New official checkpoint captures contain **3,165 entries at each round, across 16 complete pagination groups**. Round-specific `match_record` is used; `record` and nested status totals can include subsequent elimination matches. The latter must not be treated as checkpoint results. Source URLs, timestamps, hashes and raw objects are in [the isolated source index](../data/conditional_rewards/sources.csv), [ledger](../data/raw/conditional_rewards/retrievals.jsonl) and [replayable checkpoint manifest](../data/conditional_rewards/round_standings.json.gz). Historical schedules and official event identifiers remain linked through each row and [the original source inventory](SOURCES.md).

## Exact record difficulty

Assume independent outcomes with constant hypothetical match win probability p, no byes or drops. Without draws:

- Exact 5–1: `6 p^5 (1−p)`; exact 8–2: `45 p^8 (1−p)^2`.
- 5–1 or better: `6 p^5 (1−p) + p^6`.
- 8–2 or better: `45 p^8 (1−p)^2 + 10 p^9 (1−p) + p^10`.
- Perfect checkpoints: `p^6` versus `p^10`; probability ratio is `p^(−4)`.

| Match p | Exact 5–1 | Exact 8–2 | 5–1 or better | 8–2 or better | 6–0 | 10–0 |
|---:|---:|---:|---:|---:|---:|---:|
| 40% | 3.686400% | 1.061683% | 4.096000% | 1.229455% | 0.409600% | 0.010486% |
| 50% | 9.375000% | 4.394531% | 10.937500% | 5.468750% | 1.562500% | 0.097656% |
| 60% | 18.662400% | 12.093235% | 23.328000% | 16.728975% | 4.665600% | 0.604662% |
| 70% | 30.252600% | 23.347444% | 42.017500% | 38.278279% | 11.764900% | 2.824752% |
| 80% | 39.321600% | 30.198989% | 65.536000% | 67.779953% | 26.214400% | 10.737418% |

At p=50%, the exact probabilities are **3/32 versus 45/1,024**, the tails **7/64 versus 7/128**, and perfect runs **1/64 versus 1/1,024**. The no-draw exact 8–2 and perfect 10–0 are less likely throughout p=40–80%. The tails are not uniformly ordered: at p=80%, Vegas 8–2 or better is **67.779953%**, exceeding **65.536%** for historical 5–1 or better. A fixed p is a sensitivity parameter, not a rating estimate; Swiss pairings can change opponent strength.

## Vegas gate and draws

The [fresh official schedule](https://teamfighttactics.leagueoflegends.com/en-us/news/esports/convergence-fest-side-events-and-the-encore-details/) specifies six rounds, at least 12 match points to continue, then five more rounds, with no elimination cut. Its obsolete Round 10 prize-settlement prose is retained as a source inconsistency; the explicit 6+5 structure and previously verified primary announcement govern this analysis. The new snapshot’s gate, round counts and full point table are checked against the preserved rules on every build.

The exact dynamic program applies the gate **after Round 6**, and carries stopped probability separately. All requested strong R10 states necessarily pass: four intervening rounds add at most 12 points, so a 24-point checkpoint requires at least 12 points at R6. Thus the gate does not remove any path to 8–2, 9–1 or 10–0; it still governs which lower-record players get to play ten rounds. At p=50% without draws, qualification is 34.375%; reaching exact 8–2 is 4.39453125% per entry, or 12.784091% conditional on qualification. Those denominators are separately exported.

For draw probability d, `P(W)=(1−d)p`, `P(D)=d`, `P(L)=(1−d)(1−p)`; p is conditional on a decisive match. Exact W–L records require zero prior draws. The multinomial model uses d=0%, 1%, 2%, 5%; these are independent-outcome scenarios, not estimates of strategic drawing. With draws, “or better” is ambiguous, so both **wins ≥8** and **points ≥24** are exported. The latter also includes 7–0–3. Historical wins ≥5 and points ≥15 coincide after six rounds.

| Draw rate d, p=50% | Exact 8–2 | ≥8 wins | ≥24 points | R6 qualification |
|---:|---:|---:|---:|---:|
| 0% | 4.394531% | 5.468750% | 5.468750% | 34.375000% |
| 1% | 3.974335% | 5.125883% | 5.125970% | 33.442492% |
| 2% | 3.590652% | 4.800032% | 4.800683% | 32.521125% |
| 5% | 2.631168% | 3.918975% | 3.927158% | 29.838994% |

## Historical cut conversion and conditional published rewards

The following pooled fractions are **descriptive observations across these eight events**, weighted by cohort entries. They are not p-dependent forecasts, confidence intervals or estimates of a particular player’s tiebreak chances. Standings eligibility is R7 rank ≤8; archived quarterfinal pairing and completed-match evidence are separate fields. DROPPED status does not automatically remove a qualifying entry. Byes and administrative credits can be in observed records; the hypothetical probability model excludes them.

| Event | 5–1 at R6: into Top 8 | 6–0 at R6: into Top 8 |
|---|---:|---:|
| Atlanta | 2 / 30 (6.67%) | 5 / 5 (100.00%) |
| Barcelona | 0 / 37 (0.00%) | 6 / 6 (100.00%) |
| Hartford | 2 / 27 (7.41%) | 4 / 5 (80.00%) |
| Los Angeles | 2 / 26 (7.69%) | 5 / 5 (100.00%) |
| Singapore | 1 / 35 (2.86%) | 6 / 6 (100.00%) |
| Sydney | 4 / 7 (57.14%) | 1 / 1 (100.00%) |
| Utrecht | 1 / 35 (2.86%) | 6 / 6 (100.00%) |
| Vancouver | 4 / 19 (21.05%) | 3 / 3 (100.00%) |
| **Pooled** | 16 / 216 (7.41%) | 36 / 37 (97.30%) |

Hartford supplies the observed exception: one R6 6–0 player ended 6–1 outside Top 8. Thus an undefeated checkpoint did not establish a secured cut slot. Final Swiss record alone also does not settle all cuts:

| Final R7 record | Top 8 standings eligibility |
|---|---:|
| 7-0-0 | 1 / 1 (100.00%) |
| 6-0-1 | 44 / 44 (100.00%) |
| 6-1-0 | 16 / 88 (18.18%) |
| 5-0-2 | 1 / 9 (11.11%) |
| 5-1-1 | 2 / 94 (2.13%) |
| 5-2-0 | 0 / 274 (0.00%) |

**Sydney reconciliation:** the new R7 standings place one player eighth and another ninth, but the archived QF pairing contains the ninth-ranked player and excludes the eighth. The cause is unknown. Both observations remain; no replacement, disqualification or particular sharing agreement is inferred. The reward model follows archived bracket participation where all eight slots are available. Los Angeles and Vancouver lack archived QF pairings, so their reward slots are standings-implied. For the two requested R6 cohorts, Sydney’s swap does not change the cohort counts.

Published placement awards are **432 / 288 / 216 / 144** for champion / finalist / semifinalists / quarterfinalists, then 72 for 9–16, 48 for 17–32, 24 for 33–64 and 18 for 65–128. A secured Top 8 slot has a **144-ticket published floor and 432 ceiling**, conditional on eligibility and settlement. Neither is automatically guaranteed merely by reaching 6–0 at R6.

| R6 cohort | Cut fraction | Reconstructed published mean, with unresolved placement bounds | Hybrid EV at future cut q=50% | Hypothetical 216-each Top 8 mean |
|---|---:|---:|---:|---:|
| 5-1-0 | 7.41% | 54.806–59.472 | 57.139 | 57.139 |
| 6-0-0 | 97.30% | 202.378–237.405 | 212.108 | 212.108 |

The published-mean bounds conserve the 1,728-ticket Top 8 pool within each event and respect resolved awards and win-evidenced minimums. They range over remaining compatible placement assignments; they are not claims that all unfinished matches were played. Six 5–1 and eighteen 6–0 entries lack fully resolved individual cut prizes. A known-subset mean is exported separately and is not substituted for the whole cohort. In Singapore, the 6–0 cohort’s aggregate published mean is inferable as 240 even though four individual awards remain unresolved.

The **hybrid conditional EV** fixes each cohort’s observed R6→R7 cut/noncut outcomes and noncut awards, then models the future bracket afresh from Top 8 using per-round decisive win chance q. It does not fit a Swiss tiebreak model, change the empirical cut fraction when q changes, or infer q from the observed Swiss record. At q=40–80%, its means span **55.475–64.947** after 5–1 and **190.251–314.667** after 6–0. These are model sensitivities, not historical receipt intervals. The formula is `observed noncut ticket sum / cohort N + cut fraction × bracket EV(q)`.

## Published placement progression versus explicit sharing scenarios

Conditional on a secured Top 8 slot, published bracket EV is `144 + 72q + 72q² + 144q³`. Three separate hypothetical agreements conserve the same pool:

| Arrangement | Remaining pool and equal share at agreement | EV from the initial Top 8 slot | Guaranteed / maximum from that slot |
|---|---|---|---:|
| Published play-out | No equal sharing assumed | 144 + 72q + 72q² + 144q³ | 144 / 432 |
| Top 8 equal | 1,728 / 8 = 216 | 216 | 216 / 216 |
| Top 4 equal, after quarterfinals | 1,152 / 4 = 288; QF losers retain 144 | 144 + 144q | 144 / 288 |
| Top 2 equal, after semifinals | 720 / 2 = 360; earlier losers retain 144 or 216 | 144 + 72q + 144q² | 144 / 360 |

At q=50%, all four means equal **216** by pool conservation and exchangeability. At q=80%, the means are **321.408 published / 216 Top 8 split / 259.2 Top 4 split / 293.76 Top 2 split**. Consequently, an equal split can remove the additional expected reward for being stronger than the other cut players. It does not create tickets. Top 4 and Top 2 are **later** stages within a Top 8 bracket; they do not establish an earlier/larger cut such as Top 16 or Top 32.

The owner reports personally receiving **216 tickets after an undefeated Swiss run and a Top 8 split**. This is firsthand anecdotal evidence of that receipt, with event, date and precise final Swiss record unknown. It is not linked to an archive participant or used as a practice-frequency estimate. The older community excerpt is retained, but the fresh [Reddit retrieval](https://www.reddit.com/r/riftboundtcg/comments/1vxb7j8/regionals_in_singapore_solo/) returned a challenge page, not independent confirmation.

A bounded search found related **Sunday 2v2** reports: a [Barcelona participant-team report](https://www.magmachamberriftbound.com/articles/champions-of-the-rift-2026-08-23) labels a Top 4 split and reports 396 tickets per team, 198 per person. A [Singapore event recap](https://www.magmachamberriftbound.com/tournaments/rq-singapore-2026-09-06) describes the same Top 4 sharing amounts. These share a publisher and are not independent confirmation; the Singapore recap also has inconsistent round/record labels. They are preserved as community reports, not imported into Saturday probabilities, solo awards or issuance totals. They provide examples of a different cut size in a related historical format, not evidence of Top 16/32 Saturday agreements.

No event-specific Saturday Top 4, Top 2 or larger-cut agreement was established in this search. Unknown is not evidence that none occurred. The Top 8/4/2 mathematical scenarios are not weighted into a synthetic “typical actual payout.” Current general sharing provisions and historical applicability are discussed in the [Phase 5 policy review](PHASE5_GROUP_AND_TEAM_ECONOMICS.md); no blanket permission is inferred here.

## Vegas conditional rewards entering Round 11

| R10 record | Points | Final loss | Final draw | Final win | EV at p=50% | Guaranteed if completed/eligible | Maximum possible |
|---|---:|---:|---:|---:|---:|---:|---:|
| 8–2 | 24 | 30 | 35 | 40 | 35 | 30 | 40 |
| 9–1 | 27 | 40 | 50 | 60 | 50 | 40 | 60 |
| 10–0 | 30 | 60 | 70 | 80 | 70 | 60 | 80 |

For final-match p and draw rate d, the exact EVs are **30 + 10(1−d)p + 5d**, **40 + 20(1−d)p + 10d**, and **60 + 20(1−d)p + 10d**. At p=40–80% and d=0, these range **34–38 / 48–56 / 68–76**. At p=50%, the draw award is exactly the midpoint, so these particular conditional means stay 35/50/70 as d changes. The probability of arriving at a no-prior-draw record still falls with d.

A final draw locally gives 35/50/70 tickets. It changes the match record and point-band award; a historical split reallocates a fixed placement prize pool. **They are not equivalent mechanisms.** The model does not assert that a desired pairing or agreed draw is available, estimate strategic-draw frequency or authorize outcome-contingent agreements. Floors assume completion/eligibility, and all physical issuance remains unverified.

## What survives the unknowns

- **Robust within the stated p=40–80% iid range:** exact 8–2 is rarer than exact 5–1; 10–0 is rarer than 6–0. The cumulative “or better” claim depends on p and reverses at 80%.
- **Independent of skill and unknown split frequency:** the historical published Top 8 floor of 144 exceeds Vegas’s 80 ceiling once a cut slot is secured. The six-round checkpoint itself did not guarantee Top 8 in the observed sample.
- **Model dependent:** the hybrid historical conditional rewards use observed event sizes, draws and tiebreak outcomes, held fixed across q; they are not a causal estimate of the format change or a matched-skill field forecast.
- **Split dependent:** actual receipts, how often players stopped playing, and the reward for superior cut-stage skill. No universal historical splitting frequency or earlier-stage agreement is established.
- **Not established:** whole-weekend decline, physical ticket issuance, inventory availability, Metal Legend redemption or stronger/weaker Vegas field composition.

## Deliverables and reproduction

Two 1920×1080 PNGs and vector SVGs:

- [Record difficulty](../outputs/figures/conditional_record_difficulty.png) / [SVG](../outputs/figures/conditional_record_difficulty.svg).
- [Conditional reward curve](../outputs/figures/conditional_reward_curve.png) / [SVG](../outputs/figures/conditional_reward_curve.svg). Historical shading varies future q with observed cut conversion fixed; Vegas shading varies final-match p. Shading is not a guarantee or an observed payout interval.

Eight machine tables under `outputs/tables/conditional_*.csv`:

| File suffix | Meaning |
|---|---|
| `record_probabilities` | 20 p/d scenarios; exact rational and decimal probabilities; per-entry and qualification-conditioned denominators |
| `vegas_R10_record_pmf` | 680 record-state rows including explicit gate-failure probability |
| `vegas_final_round_rewards` | 60 conditional final-round W/D/L payout calculations |
| `secured_cut_rewards` | 20 published-versus-sharing bracket sensitivities |
| `historical_checkpoint_rows` | 3,165 identity-linked R6/R7 entries with row provenance, bracket evidence and unknowns |
| `historical_record_cohorts` | 708 event/pooled record cohorts, cut fractions and pool-conserving award bounds |
| `historical_hybrid_rewards` | 360 cohort/future-q/agreement model rows |
| `historical_R7_transitions` | 39 record/result transition cohorts; credit is not automatically a played match |

Model fractions are serialized with `_exact` strings alongside decimals. Blank values mean unknown. Source/evidence review and the owner observation are in `data/conditional_rewards/`; new raw captures have a separate ledger. No display names are included in the new row export. Earlier results, raw evidence, code, figures and execution records are protected by the 979-file manifest from commit `c596588`.

```sh
PYTHONPATH=src python3.12 -m riftbound_tickets.conditional_rewards collect   # network, separate evidence set
PYTHONPATH=src python3.12 -m riftbound_tickets.conditional_rewards build
PYTHONPATH=src .venv-figures/bin/python -m riftbound_tickets.conditional_rewards figures
PYTHONPATH=src python3.12 -m riftbound_tickets.conditional_rewards audit
python3.12 scripts/validate_conditional_rewards.py
```

The isolated runner executes the full unittest suite; legacy build, verify, audit and validate-pilot; Phase 2/3A/3B/4/5 audits; and this analysis’s build/figures/audit. Results and per-command logs are stored in `outputs/tables/conditional_execution_validation.json` and `outputs/conditional_rewards/validation/`. Executed results are recorded below after validation.

**Executed validation:** on 2026-11-26 (America/Indianapolis), the full suite passed **172 tests** and **all 13 recorded commands**. The before/after preservation checks confirmed all **979 protected prior files unchanged**. Both 1920×1080 figures were visually inspected for readable labels, legends, ranges and footnotes; figure hashes passed the offline audit. See [the execution report](../outputs/tables/conditional_execution_validation.json) and [artifact audit](../outputs/tables/conditional_validation.json). No commit or push was performed.
