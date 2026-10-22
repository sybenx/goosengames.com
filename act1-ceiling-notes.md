# Act 1: the regular-conversion ceiling

Notes on why a stand run stalls below 100 regulars, and what is worth
documenting in the source. Findings apply to **v3 and v4 equally** — the
relevant code is byte-identical between them.

---

## The short version

A run that never touches the price board plateaus below the 100-regular
ending. **Price is the lever that resolves it**, not the line rate.

At the $6.50 start price with the careful line ("Take the time"), both
griddles and Maya, the stand caps at **~69 regulars** and stops converting
permanently. Raising the price to **$7.75–$8.25** lifts the ceiling past 100
while keeping every quality tier at its best and every regular's trust
drifting upward.

---

## Why it stalls

New regulars are created in exactly one place, in `resolveWeekAct1()`:

```js
if (fq >= CFG.convertQualityMin && S.turnedAway < 8 && S.regulars.length < 120){
```

`S.turnedAway` is `max(0, round(demand − capacity))`. The trap is that
existing regulars generate the demand:

```
demand   = regulars × visitRate + strangers
capacity = 150 × handling.cap × 1.5 (griddle) × 1.35 (griddle2) × 1.4 (Maya)
```

Every regular gained pushes demand up, and once the line runs long by 8 or
more a week the gate latches and no further regulars are ever created. The
stand settles at an equilibrium of `(capacity + 8 − strangers) / visitRate`.

Raising the price attacks both terms at once: strangers fall off steeply
(`elasticityStrangers: 1.9`) and each regular visits less often
(`elasticityRegulars: 0.55`). That frees the capacity the gate needs.

### Ceilings, "Take the time" + both griddles + Maya

| Price | Fair price | Strangers/wk | Visits/regular | Ceiling |
|------:|-----------:|-------------:|---------------:|--------:|
| $6.50 | $7.90 | 145 | 3.25 | **69** |
| $7.00 | $7.90 | 126 | 3.12 | 78 |
| $7.50 | $7.90 | 110 | 2.66 | 97 |
| $7.75 | $7.90 | 104 | 2.61 | **101** |
| $8.00 | $7.90 | 98 | 2.57 | 105 |
| $8.25 | $7.90 | 92 | 2.53 | 109 |

`fairPrice()` is `6.20 × (0.60 + 0.72 × fullQuality/100)` — at top tiers with
the careful line that is **$7.90**, well above Patty Palace's $6.20. Trust
keeps drifting *up* as long as `price <= fair × 1.06`, i.e. up to **$8.37**.
So the whole useful range sits inside the trust-safe band.

### The trap in the other direction

Line rate also works — "Peak throughput" reaches ~119 at the start price —
but it is the wrong answer. It drops `fullQuality` from 93.7 to 86.5 and
makes the least careful burger in the game the price of the ending that is
about knowing everyone's name.

### The 80-regular arc lowers your own ceiling

The block-association arc fires at 80 regulars and its reward is
`S.walkins += 20` — twenty more strangers competing for the same griddle.
At $6.50 that costs roughly six regulars off the ceiling. Getting deep into
the local path actively pushes the ending further away.

---

## Fixing a stalled save

1. Confirm the diagnosis: the receipt shows *"The line ran long — about N
   people gave up waiting this week."* If N is 8 or more, conversion is off.
2. Buy anything missing from the capacity ladder: second griddle ($900),
   third burner ($1,400), and Maya (free, +40%, offered from 16 regulars).
3. Raise the price toward **$8.00**, in $0.25 steps.

Raise it *gradually*. `priceRaiseTrustCost: 7` is an instant trust hit per
$0.25 step — $6.50 → $8.00 in one go costs 42 trust across every regular.
Trust recovers at `trustDriftUp: 0.7`/week while quality holds and price
stays under fair × 1.06, so step up and let it settle. Lower trust also means
fewer visits per regular, which raises the ceiling further in the short run.

Once the gate reopens conversion runs at roughly 1–2 regulars/week.

---

## Was it a bug?

**No — the mechanism is deliberate and the price board is the intended
answer.** The evidence that settles it is `demandDeltaForPrice()`
(v3:1283, v4:1450), whose only use is rendering, in Act 1, the line
*"Counter demand est. −X% · walk-ins est. −Y%"* on the raise-price control.
That helper exists to teach exactly this loop. The header already surfaces
`N walked off (capacity C)`; the answer it invites is the price board.

A first pass at this concluded the opposite — that the ending was only
reachable on the fastest line rate — because it held price frozen at the
$6.50 start value and read the resulting plateau as a property of the
system. It is an artifact of one untouched parameter. A grid search over
price × handling tier × upgrade set × claims × seeds finds careful
configurations reaching 100 comfortably: "Standard pace" gets there even
*below* fair price, and "Take the time" gets there at 1.04–1.07 × fair
across every upgrade set, including with no griddle upgrade at all.

Worth keeping anyway: **nothing in the game says any of this.** The
mechanism is discoverable only by inference, and the failure is silent.

---

## Worth documenting in the source

Ordered by how much confusion each one causes.

1. **The warning fires on the wrong threshold.** The feed prints "the line
   ran long" at `turnedAway > 3`; the gate that ends the run latches at
   `>= 8`, silently. A player gets a warning for a number that does not
   matter and nothing at the one that does. This is the single highest-value
   fix in Act 1 — arguably a real bug rather than a doc gap.

2. **The capacity ↔ conversion ↔ regular-demand loop has no comment
   anywhere.** `capacity()` (v3:879), the conversion block (v3:983–996) and
   `S.turnedAway` (v3:949) form a negative feedback loop spread across three
   functions with nothing tying them together. Nothing records that price is
   the intended release valve — the one thing a reader most needs to know.

3. **The literal `8`** in `S.turnedAway < 8` is an inline magic number, not
   even in `CFG`. It decides whether Act 1's ending is reachable.

4. **`CFG.localEndRegulars: 100` is dead code** — never read in either
   version. The ending fires off the last entry of `localMilestones`. Either
   wire it up or delete it; right now it reads as the authoritative constant
   and is not.

5. **`practice: true`** marks seasoning, handling and kitchen — the three
   attributes whose best tier costs time rather than money. Grep finds no
   code path that reads it. It is a moral axis that was declared and never
   wired up. Intentional placeholder, or forgotten?

6. **`S.regulars.length < 120`** sits next to a 100 that no code consults,
   with no note on which is the real ceiling. Also: 16 `CORE_REGULARS` + 96
   `NAME_POOL_FIRST` = 112 unique names, so runs past 112 recycle first
   names silently.

7. **`committedLocal = true` is a hidden side effect of the 46-regular Rosa
   arc** (v3:1782), and v3:1207 uses it to permanently suppress Marlowe's
   offer. Catering a retirement party deletes Acts 2 and 3 for that run.
   Neither side comments on it; the only hint is a toast about calls going
   to voicemail.

8. **The conversion expectation formula** (v3:984–988) has five
   undocumented constants: `0.16 + strangerUnits × 0.006`, then
   `× (fq − 76 + 6)/20`, then `×1.5` specials, `×1.2` awning, then
   `min(3, converts)`. At Act 1 walk-in volume the `0.006` term runs ~4×
   larger than `convertChance` itself, which makes the named constant
   nearly decorative. Nothing says what the `+6`/`/20` shaping normalises to.

9. **`regularExpectation: 74` vs `convertQualityMin: 76`**, plus the inline
   bands at v3:965–968 (trust rises at `fq >= 74 && price <= fair×1.06`,
   falls at `fq < 70 || price > fair×1.12`). A deliberate-looking 2-point
   gap between "keeps regulars" and "gains regulars", unexplained.

10. **Acts 2–3 demand is one uncommented expression** (`resolveWeekScale`,
    v3:1034–1044): `retention = clamp(0.52 + (fq−70)×0.004 + sop×0.045 −
    max(0, price−marketPrice)×0.02, 0.30, 0.92)`, then
    `loyal = loyal×retention + strangers×0.22` and
    `units = strangers + loyal×0.85`. This is half the game's simulation.
    A reader cannot recover the steady state or what `0.22` and `0.85` mean.

---

## Method

- Equilibrium figures come from a reimplementation of `capacity()`,
  `fullQuality()`, `fairPrice()`, `regularVisitRate()` and
  `strangerDemandPerStore()` with constants extracted verbatim from the
  source, then solved for the `turnedAway < 8` boundary.
- Validated against a full week-loop simulation with visit rolls, ±8%
  stranger noise, trust drift, price-raise trust cost, all seven
  `LOCAL_ARCS` effects and cost-pressure events. Grid searched over price
  $5.00–$12.00 in 25¢ steps × handling tier × upgrade set × claims ×
  oil/kitchen tiers, 9–20 seeds per cell.
- The walk-in figure of 162 was confirmed by grid search as
  `walkinBase 118 + awning 10 + market stall 14 + block association 20`.
- v3/v4 equivalence established by md5 on `resolveWeekAct1()`, `capacity()`,
  the `ATTRS` block, `LOCAL_ARCS` and every Act-1 `CFG` constant. The whole
  Act 1 weekly resolution differs by one line: a write-only `S.servedTotal`
  accumulator feeding v4's `tier3Units` interface threshold, which Act 1
  cannot reach.
