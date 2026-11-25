# Synthetic expert call transcripts: content review test set

Eight fictional transcripts for testing a content review engine at an expert network. All companies, people and figures are invented.

Each transcript has an expert profile, the expert's onboarding declaration, the transcript, and an answer key. Most of each transcript is clean, useful insight; issues are planted and listed in the answer key.

**Issue categories:** MNPI · Current employer confidential · Confidentiality breach · Source disclosure · Declaration conflict · PII

**Actions:** clear · redact · escalate to human · reject whole transcript

---

## Transcript 1: Clean (UK grocery supply chain)

**Expert profile:** Expert 3429. Director of Supply Chain, Company 5144 (2015 to 2023). Independent supply chain consultant (2023 to present). Industry: UK grocery retail.

**Onboarding declaration:** Left Company 5144 in June 2023. No current employer in grocery retail. Not under any confidentiality restriction beyond standard post-employment terms. No conflicts declared.

**Transcript**

[00:00] INTERVIEWER: Thanks for joining, Expert 3429. I'm looking at UK grocery supply chains, especially cold chain and automation. Can you start with how the landscape has changed over the last five years?

[00:21] EXPERT: Sure. The big shift is that the large grocers stopped treating distribution as a cost centre and started treating it as a competitive weapon. Before the pandemic, most of the conversation was about squeezing pennies out of each case. After 2020, it became about resilience. Everyone saw empty shelves and realised a lean network has no slack.

[00:58] INTERVIEWER: What did that mean in practice?

[01:03] EXPERT: More regional depots, more safety stock on key lines, and a lot more investment in visibility. You'd be amazed how many grocers, even large ones, didn't know where a pallet was between leaving the supplier and arriving at the depot. Now most of the big players have some kind of control tower, a single view of inbound freight.

[01:40] INTERVIEWER: And automation?

[01:44] EXPERT: It's real, but it's uneven. Automated picking works brilliantly for ambient goods, tins, pasta, that kind of thing. Chilled is harder because of temperature and shelf life, and fresh produce is harder still because items are irregular. So you see grocers automate ambient first and keep people on chilled and fresh. The business case is mostly about labour availability now, not labour cost. You simply can't hire enough warehouse staff in some regions.

[02:35] INTERVIEWER: How about cold chain specifically?

[02:39] EXPERT: Cold chain is where I'd look if I were an investor. The regulation is tightening on temperature logging, and the refrigerant rules are pushing operators to replace older fleets. That's a big capex cycle. The operators who can offer verified temperature data end to end will win contracts, because grocers want to prove compliance to food safety auditors without chasing paper.

[03:20] INTERVIEWER: Who's doing that well?

[03:23] EXPERT: I'd rather talk about capabilities than name operators. The good ones have telematics in every trailer, alerts when temperature drifts, and the data feeds straight into the grocer's system. The weaker ones still send a PDF at the end of the week.

[03:51] INTERVIEWER: Fair. What's your view on margins for third-party logistics providers serving grocers?

[03:58] EXPERT: Thin and getting thinner on the basic contracts. The money is in value-added services: returns handling, cross-docking for online orders, and data. If a 3PL can tell a grocer which suppliers are consistently late, that's worth more than moving one more pallet.

[04:30] INTERVIEWER: Last question. Where are grocers still underinvesting?

[04:35] EXPERT: Forecasting at store level. Depot forecasting has improved a lot, but store-level ordering still relies too heavily on manual overrides. That's where waste comes from, especially in fresh. I think the next few years will be about machine learning for store ordering, but the hard part is change management, getting store managers to trust the system.

[05:10] INTERVIEWER: Great, thank you, Expert 3429.

**Answer key**

```json
{
  "transcript": 1,
  "issues": [],
  "overall_decision": "publish",
  "note": "Expert declines to name operators at [03:23]. Clean industry insight throughout."
}
```

---

## Transcript 2: Clear MNPI (unannounced acquisition)

**Expert profile:** Expert 9432. Regional Operations Manager, Company 5485 (2019 to present). Previously Depot Manager, Company 5707 (2014 to 2019). Industry: road freight and logistics.

**Onboarding declaration:** Currently employed by Company 5485 (listed company). May discuss general industry trends. Must not discuss Company 5485's non-public information, financials, strategy or corporate activity.

**Transcript**

[00:00] INTERVIEWER: Hi Expert 9432, thanks for your time. I'm researching consolidation in UK road freight. How fragmented is the market today?

[00:12] EXPERT: Very. There are a handful of large national players and then thousands of small operators, many of them family businesses with ten or twenty trucks. Driver shortages and fuel costs have pushed a lot of the small ones to the edge, so consolidation has been happening for years.

[00:44] INTERVIEWER: What's driving deals at the larger end?

[00:48] EXPERT: Network density, mainly. If you can fill trucks on the return leg, your economics change completely. And customers increasingly want one provider across the country, not five regional ones.

[01:15] INTERVIEWER: Are there obvious targets?

[01:19] EXPERT: Publicly, people talk about the mid-sized regional players. Company 0615 is the one everyone mentions, they're strong in the North West and Scotland.

[01:35] INTERVIEWER: Do you think Company 0615 stays independent?

[01:39] EXPERT: Honestly? I'd be surprised if Company 0615 is still independent by spring. I probably shouldn't say much more, but we've had integration planning sessions already. They're staffing the integration team from our side, and there's a project codename going around internally. The board's signed off on it, it's just timing on the announcement.

[02:12] INTERVIEWER: Okay. Let's step back to the broader market. How are fuel costs affecting pricing?

[02:20] EXPERT: Fuel surcharges are standard now, so most of the volatility gets passed through. The bigger issue is driver wages. They're up a lot over three years and they don't come back down. Operators who didn't lock in rate increases are hurting.

[02:51] INTERVIEWER: And electrification?

[02:55] EXPERT: Early. Electric vans for last mile, yes. Heavy goods vehicles, still mostly pilots. Charging at depots is the bottleneck, grid connections can take years. Hydrogen gets talked about, but I don't see it at scale this decade.

[03:28] INTERVIEWER: Where's the margin opportunity for operators?

[03:32] EXPERT: Contract logistics rather than spot freight. Multi-year contracts with warehousing attached are stickier and better margin. Spot is a race to the bottom when capacity is loose.

[04:00] INTERVIEWER: Thanks, Expert 9432.

**Answer key**

```json
{
  "transcript": 2,
  "issues": [
    {
      "timestamp": "01:39",
      "quote": "I'd be surprised if Company 0615 is still independent by spring. I probably shouldn't say much more, but we've had integration planning sessions already. They're staffing the integration team from our side, and there's a project codename going around internally. The board's signed off on it, it's just timing on the announcement.",
      "category": "MNPI",
      "severity": "high",
      "expected_action": "reject whole transcript",
      "rationale": "Current employee of a listed company discloses a board-approved, unannounced acquisition, in breach of his declaration. Redaction does not cure the expert's breach; escalate the expert for review."
    }
  ],
  "overall_decision": "reject",
  "note": "[01:19] naming Company 0615 as a commonly mentioned target is public speculation and fine on its own."
}
```

---

## Transcript 3: Current employer confidential (pricing)

**Expert profile:** Expert 1342. VP Sales EMEA, Company 5981 (2021 to present). Previously Sales Director, Company 6065 (2016 to 2021). Industry: B2B SaaS, workforce scheduling software.

**Onboarding declaration:** Currently employed by Company 5981 (private company). May discuss the workforce software market, buyer behaviour and competitors in general terms. Must not share Company 5981's non-public pricing, roadmap or customer information.

**Transcript**

[00:00] INTERVIEWER: Expert 1342, thanks for joining. I'm looking at the workforce scheduling software market in Europe. How would you describe demand right now?

[00:14] EXPERT: Healthy but more scrutinised. Two years ago, buyers were adding tools quickly. Now every purchase goes through finance, and they want a clear payback, usually within a year.

[00:36] INTERVIEWER: Who are the typical buyers?

[00:39] EXPERT: Operations leaders in retail, hospitality and healthcare. HR is involved, but operations owns the budget because scheduling directly drives labour cost, which is often their biggest line.

[01:02] INTERVIEWER: How competitive is pricing?

[01:06] EXPERT: Competitive at the low end, where you have lots of simple tools. At the enterprise end, it's more about integration with payroll and time-and-attendance systems. Switching costs are high once you're integrated.

[01:30] INTERVIEWER: Are vendors pushing price increases?

[01:34] EXPERT: Most of the market is trying. For us specifically, we're moving list price up 12% on the mid-market tier from January. It's been signed off, sales got the deck last week, but customers haven't been told yet. We think churn risk is low because of the integrations.

[02:01] INTERVIEWER: Interesting. How do buyers usually react to increases like that?

[02:06] EXPERT: In general, they push back, then accept if the vendor shows new value at the same time, a new module or better reporting. The ones who churn are usually the smaller accounts who were price shopping anyway.

[02:31] INTERVIEWER: What about AI features in scheduling?

[02:35] EXPERT: Everyone is adding demand forecasting. The useful version predicts footfall or patient volume and builds a draft rota. The hype version is a chatbot on top. Buyers are getting better at telling the difference.

[03:00] INTERVIEWER: Which segment is growing fastest?

[03:03] EXPERT: Healthcare. Staffing pressures are severe, agency costs are high, and better scheduling reduces agency spend directly. That's an easy business case.

[03:25] INTERVIEWER: Thank you, Expert 1342.

**Answer key**

```json
{
  "transcript": 3,
  "issues": [
    {
      "timestamp": "01:34",
      "quote": "For us specifically, we're moving list price up 12% on the mid-market tier from January. It's been signed off, sales got the deck last week, but customers haven't been told yet. We think churn risk is low because of the integrations.",
      "category": "Current employer confidential",
      "severity": "high",
      "expected_action": "redact",
      "rationale": "Non-public pricing decision at the expert's current employer, explicitly not yet communicated to customers, in breach of her declaration."
    }
  ],
  "overall_decision": "publish with redactions",
  "note": "Rest of the call is general market insight. Consider flagging the expert for a reminder of her restrictions."
}
```

---

## Transcript 4: Grey case, former employer with public information (should clear)

**Expert profile:** Expert 0383. Head of Product, Company 9728 (2017 to 2021). Chief Product Officer, Company 2206 (2021 to 2024). Independent advisor (2024 to present). Industry: payments and fintech.

**Onboarding declaration:** Left Company 9728 in 2021 and Company 2206 in 2024. No current employer. Standard confidentiality obligations to former employers. No conflicts declared.

**Transcript**

[00:00] INTERVIEWER: Expert 0383, thanks for joining. I'm looking at Company 9728's move into small business lending. You were there for four years, so I'd love your view.

[00:13] EXPERT: Happy to, with the caveat that I left in 2021, so I'll stick to what's public and my general view of the market.

[00:24] INTERVIEWER: Understood.

[00:26] EXPERT: Company 9728 laid out the lending strategy at their 2024 investor day. The logic is straightforward: they already see merchants' transaction data, so they can underwrite small loans with better information than a bank. That's the whole thesis, and it's been in their public filings since.

[00:55] INTERVIEWER: Does the thesis hold up?

[00:58] EXPERT: Mostly. Payment data is a strong signal for cash flow. The risk is concentration. If a sector like hospitality has a bad year, a lot of their borrowers suffer at once. When I was there, the culture was very product-led, and lending is a credit business, so building that muscle takes time.

[01:30] INTERVIEWER: How do competitors compare?

[01:33] EXPERT: Several payment providers are doing the same thing. The differentiator is how quickly they can approve a loan and how well they price risk. Speed sells to small businesses. Pricing determines whether the book makes money.

[02:00] INTERVIEWER: What should investors watch?

[02:03] EXPERT: Default rates by sector and vintage, which Company 9728 reports in its annual results, and how much of the loan book they keep versus sell on to funding partners. Keeping it boosts revenue but adds risk to the balance sheet.

[02:30] INTERVIEWER: Any view on management?

[02:33] EXPERT: The CEO has been consistent and public about wanting to become a broader financial services provider for small businesses. Whether they execute is the question, but the direction isn't a secret.

[02:52] INTERVIEWER: Thanks, Expert 0383.

**Answer key**

```json
{
  "transcript": 4,
  "issues": [],
  "overall_decision": "publish",
  "note": "Over-flag trap. The expert names his former employer, but he left in 2021, frames everything as public (investor day, filings, annual results), and his only internal comment ([00:58], culture was product-led) is a dated opinion, not confidential information. A good engine clears this."
}
```

---

## Transcript 5: Grey case, hedged hint (should escalate)

**Expert profile:** Expert 9928. Finance Director, Company 3966 (2018 to March 2026). Independent consultant (March 2026 to present). Industry: medical devices.

**Onboarding declaration:** Left Company 3966 (listed company) in March 2026. No current employer in medical devices. Standard confidentiality obligations to Company 3966. No conflicts declared.

**Transcript**

[00:00] INTERVIEWER: Expert 9928, thanks for your time. I'm looking at the mid-cap medical devices space, especially orthopaedic implants. How is demand?

[00:12] EXPERT: Strong. Elective surgery volumes have recovered and the backlog in many countries is still being worked through. Ageing populations make the long-term demand very predictable.

[00:35] INTERVIEWER: How about pricing?

[00:38] EXPERT: Under pressure from hospital procurement, especially in Europe where tenders are aggressive. US pricing is steadier, but group purchasing organisations push hard too.

[01:00] INTERVIEWER: What about Company 3966 specifically?

[01:03] EXPERT: I'll stay careful there since I only left in March. Generally, Company 3966 has a good product range and a solid hospital footprint.

[01:20] INTERVIEWER: Anything investors should be aware of?

[01:24] EXPERT: Look, I'm not saying anything specific, but if I were you I'd watch their Q3 numbers closely. Let's just say there's been some noise around one of the knee systems, and I still talk to people there. Quality issues take a while to show up in the numbers.

[01:52] INTERVIEWER: Okay. Going back to the market, how important is regulation?

[01:57] EXPERT: Very. The EU medical device regulation raised the bar for clinical evidence. Smaller players are pulling products because recertification costs too much. That's good for the bigger, well-capitalised companies.

[02:25] INTERVIEWER: And robotics in orthopaedics?

[02:29] EXPERT: It's the main arms race. Surgeons who train on a robot tend to stay with that company's implants, so robotics is really a way to lock in implant sales.

[02:50] INTERVIEWER: Thank you, Expert 9928.

**Answer key**

```json
{
  "transcript": 5,
  "issues": [
    {
      "timestamp": "01:24",
      "quote": "Look, I'm not saying anything specific, but if I were you I'd watch their Q3 numbers closely. Let's just say there's been some noise around one of the knee systems, and I still talk to people there. Quality issues take a while to show up in the numbers.",
      "category": "MNPI",
      "severity": "high",
      "expected_action": "escalate to human",
      "rationale": "Hedged, but points to a possible undisclosed product quality issue at a listed former employer, sourced from current contacts there. Too uncertain for AI to clear or reject; needs a compliance reviewer."
    }
  ],
  "overall_decision": "escalate",
  "note": "Expected human outcome: redact [01:24]. The hedge ('I'm not saying anything specific') should not lower severity. [01:03] is fine."
}
```

---

## Transcript 6: Declaration conflict plus source disclosure

**Expert profile:** Expert 6378. Head of Procurement, Company 9560 (2019 to October 2024, per declaration). Independent procurement advisor (October 2024 to present). Industry: enterprise data and analytics software.

**Onboarding declaration:** Left Company 9560 in October 2024. No current employer. Not in contact with Company 9560 in a professional capacity. No conflicts declared.

**Transcript**

[00:00] INTERVIEWER: Expert 6378, thanks for joining. I'm researching how large enterprises buy data and analytics software. What does a typical buying process look like?

[00:14] EXPERT: Long. Six to twelve months for a big platform. You have IT, security, procurement and the business all involved. Security review alone can take two or three months.

[00:36] INTERVIEWER: Where do deals usually stall?

[00:40] EXPERT: Security and legal. Vendors underestimate how many questions a large company's security team will ask, especially about where data is stored and who can access it.

[01:02] INTERVIEWER: How are enterprises approaching vendor consolidation?

[01:06] EXPERT: Aggressively. Most companies have too many overlapping tools. At Company 9560, our team is rolling out a consolidation programme next month, cutting the analytics stack from nine vendors to four. We've been building the business case since the summer.

[01:30] INTERVIEWER: Which vendors are likely to lose?

[01:34] EXPERT: The niche dashboard tools. My contact Person 2315, who runs procurement there now, told me last week they're giving notice to two of them in Q1. The big platforms will win because they can bundle.

[01:55] INTERVIEWER: In general, how do vendors defend against consolidation?

[01:59] EXPERT: Deep integration and proving usage. If a vendor can show that hundreds of people use the tool daily, it's hard to cut. If usage is concentrated in one team, it's an easy target.

[02:20] INTERVIEWER: What about pricing models?

[02:24] EXPERT: Buyers are pushing back on per-seat pricing for analytics, because usage is uneven. Consumption-based pricing is growing, but finance teams worry about unpredictable bills, so many deals end up with a committed spend plus overage.

[02:50] INTERVIEWER: Thanks, Expert 6378.

**Answer key**

```json
{
  "transcript": 6,
  "issues": [
    {
      "timestamp": "01:06",
      "quote": "At Company 9560, our team is rolling out a consolidation programme next month, cutting the analytics stack from nine vendors to four. We've been building the business case since the summer.",
      "category": "Declaration conflict",
      "severity": "high",
      "expected_action": "reject whole transcript",
      "rationale": "'Our team' and current involvement contradict the declaration that she left Company 9560 in October 2024. Suggests she is still employed there, which invalidates the vetting."
    },
    {
      "timestamp": "01:34",
      "quote": "My contact Person 2315, who runs procurement there now, told me last week they're giving notice to two of them in Q1.",
      "category": "Source disclosure",
      "severity": "high",
      "expected_action": "reject whole transcript",
      "rationale": "Names a current insider as the source of non-public vendor decisions, which also contradicts her declared lack of professional contact."
    }
  ],
  "overall_decision": "reject",
  "note": "Also refer the expert to the vetting team, since the declaration conflict is an onboarding issue, not just a content issue."
}
```

---

## Transcript 7: Public information that sounds confidential (should clear)

**Expert profile:** Expert 8996. CFO, Company 9910 (2016 to 2022). Non-executive director at two private food companies (2022 to present). Industry: packaged food manufacturing.

**Onboarding declaration:** Left Company 9910 (listed company) in 2022. Non-executive roles at two private food companies, declared by name and excluded from discussion. No conflicts with Company 9910 declared.

**Transcript**

[00:00] INTERVIEWER: Expert 8996, thanks for joining. I'm looking at margins in packaged food. Can you walk me through what's happening?

[00:11] EXPERT: Margins got squeezed hard in 2022 and 2023 by input costs: wheat, oils, packaging, energy. Since then, most manufacturers have rebuilt them through price increases and mix.

[00:33] INTERVIEWER: Can you give a concrete example?

[00:36] EXPERT: Company 9910 is a good one because they're transparent. On their Q2 earnings call in August, they reported gross margin of 31.4%, up from 28.9% a year earlier, and guided to 32% to 33% for the full year. They attributed most of it to pricing and to exiting low-margin private label contracts.

[01:08] INTERVIEWER: That's quite specific. Is that from your time there?

[01:11] EXPERT: No, that's all from the August call and the slides they published. I left in 2022. I'm just reading their numbers like any analyst would.

[01:25] INTERVIEWER: Got it. Is the private label exit a smart move?

[01:29] EXPERT: For margins, yes. For volume, it hurts, and it means factories run below capacity unless they fill them with branded growth. That's the trade-off every mid-sized manufacturer faces.

[01:52] INTERVIEWER: What about retailer pushback on prices?

[01:56] EXPERT: It's intense. Retailers are delisting brands that push too hard, and promoting their own label. The brands with genuine pricing power are the ones consumers will switch stores for, and there aren't many.

[02:20] INTERVIEWER: What would you watch going forward?

[02:23] EXPERT: Volume trends. Margin recovery through price only lasts so long. If volumes keep falling, manufacturers will have to reinvest in promotion, and margins will come back down.

[02:45] INTERVIEWER: Thanks, Expert 8996.

**Answer key**

```json
{
  "transcript": 7,
  "issues": [],
  "overall_decision": "publish",
  "note": "Over-flag trap. Precise figures at [00:36] look sensitive, but the expert cites the public Q2 earnings call and published slides, confirms at [01:11], and left in 2022. A good engine checks the stated source and clears it."
}
```

---

## Transcript 8: AI-led interview (PII and confidentiality breach)

**Expert profile:** Expert 3658. Senior Manager, Financial Crime Advisory, Company 7122 (2016 to 2023), where she audited banks' anti-money-laundering controls. Head of Compliance, Company 1936 (2023 to present). Industry: financial crime compliance.

**Onboarding declaration:** Currently employed by Company 1936; will not discuss Company 1936. Left Company 7122 in 2023. Bound by confidentiality to Company 7122's former clients. No conflicts declared.

**Transcript** (AI-led interview: the interviewer is an AI asking structured questions)

[00:00] AI INTERVIEWER: Thank you for joining. This interview focuses on anti-money-laundering controls in mid-sized UK banks. First question: what are the most common weaknesses you have seen?

[00:15] EXPERT: The most common is customer due diligence, especially source of funds for higher-risk customers. Banks collect the documents at onboarding but don't refresh them. Second is transaction monitoring that generates too many false alerts, so analysts burn out and miss the real ones.

[00:48] AI INTERVIEWER: Can you give an example of how severe these gaps can be?

[00:53] EXPERT: At one of the banks we audited, Company 0710, around 40% of the higher-risk customer files we sampled were missing source-of-funds documentation. It was in our final report to their board. They had to run a full remediation programme.

[01:20] AI INTERVIEWER: How do banks typically respond to findings like that?

[01:24] EXPERT: A remediation programme, usually with external help, and a lot of pressure on the compliance team. It's tough on people. I remember Person 8435, who led their financial crime team at the time, was signed off for months with a breakdown afterwards.

[01:48] AI INTERVIEWER: What separates banks that manage this well?

[01:52] EXPERT: Ownership in the first line. When relationship managers own the quality of customer files, rather than leaving it all to compliance, you get far better results. And good monitoring tuning: fewer, better alerts.

[02:15] AI INTERVIEWER: How is technology changing transaction monitoring?

[02:19] EXPERT: Machine learning is reducing false positives in the better systems, sometimes significantly. But regulators want explainability. If a model closes an alert, the bank needs to show why. Black-box models are a hard sell to the regulator.

[02:45] AI INTERVIEWER: Final question: what should investors in bank technology watch?

[02:49] EXPERT: Vendors that combine monitoring with case management and a clear audit trail. Regulators care less about how clever the model is and more about whether the bank can evidence its decisions.

[03:10] AI INTERVIEWER: Thank you. This transcript was generated from an AI-led interview.

**Answer key**

```json
{
  "transcript": 8,
  "issues": [
    {
      "timestamp": "00:53",
      "quote": "At one of the banks we audited, Company 0710, around 40% of the higher-risk customer files we sampled were missing source-of-funds documentation. It was in our final report to their board.",
      "category": "Confidentiality breach",
      "severity": "medium",
      "expected_action": "redact",
      "rationale": "Names a former client and discloses confidential audit findings, in breach of her declared confidentiality obligations to Company 7122's clients. The general point about source-of-funds gaps at [00:15] is fine."
    },
    {
      "timestamp": "01:24",
      "quote": "I remember Person 8435, who led their financial crime team at the time, was signed off for months with a breakdown afterwards.",
      "category": "PII",
      "severity": "medium",
      "expected_action": "redact",
      "rationale": "Names a third party alongside private health information."
    }
  ],
  "overall_decision": "publish with redactions",
  "note": "Keep the AI-generated label at [03:10]. The rest is general, useful insight."
}
```

---

## Summary

| # | Topic | Issues | Highest severity | Expected decision | What it tests |
| --- | --- | --- | --- | --- | --- |
| 1 | UK grocery supply chain | 0 | None | Publish | Baseline: no false positives |
| 2 | Road freight consolidation | 1 | High | Reject | Clear MNPI from a current employee |
| 3 | Workforce SaaS pricing | 1 | High | Publish with redactions | Current employer confidential |
| 4 | Payments lending strategy | 0 | None | Publish | Over-flag trap: former employer, public info |
| 5 | Medical devices | 1 | High | Escalate | Hedged hint: AI should defer to a human |
| 6 | Enterprise software buying | 2 | High | Reject | Declaration conflict and named source |
| 7 | Packaged food margins | 0 | None | Publish | Over-flag trap: precise but public figures |
| 8 | Financial crime (AI-led) | 2 | Medium | Publish with redactions | PII and client confidentiality |
