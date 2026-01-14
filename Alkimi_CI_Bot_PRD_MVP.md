# Product Requirements Document
## Competitive Intelligence Bot (CI-Bot)
### MVP Release — v1.0

**Daily AI & AdTech Market Intelligence via Slack**

---

| Field | Value |
|-------|-------|
| Document Version | 1.0 (MVP) |
| Date | January 2026 |
| Author | Automation Specialist / AI Transformation Lead |
| Status | Draft for Review |
| Target Delivery | 4 Weeks from Approval |
| Priority | High — Strategic Initiative |

---

## 1. Executive Summary

The Competitive Intelligence Bot (CI-Bot) MVP is a Slack-based tool delivering daily curated market intelligence on AI capabilities and automation developments in advertising technology. This initial release focuses on serving **Executive Leadership and Product Team** with high-signal, low-noise competitive intelligence that directly informs strategic decisions for AMP and Zero-Day Payments positioning.

### 1.1 MVP Scope Summary

| In Scope (MVP) | Out of Scope (V2) |
|----------------|-------------------|
| Daily Slack digest to #ci-intel channel | Google Sheets competitive database |
| Tier 1 publication monitoring (4 sources) | Tier 2 deep-dive sources |
| AI-powered relevance filtering | Historical trend analytics dashboard |
| Manual threat scoring (editor review) | Automated threat scoring model |
| AMP + Zero-Day threat categorization | Custom category configuration |
| Weekly summary digest | Quarterly board-ready reports |

---

## 2. Problem Statement

### 2.1 Current State

- Executive and Product leadership lack systematic visibility into competitor AI capabilities
- Critical market developments are discovered reactively (often via customer conversations)
- No centralized intelligence correlating external developments with AMP/Zero-Day roadmap
- Manual publication monitoring is inconsistent and time-prohibitive for senior leadership

### 2.2 Strategic Risk

Without proactive intelligence, Alkimi risks: (1) delayed response to competitive threats against AMP's unified campaign management value proposition, and (2) erosion of Zero-Day Payments differentiation as traditional players experiment with accelerated settlement.

---

## 3. User Personas

### 3.1 Primary Users (MVP Focus)

| Persona | Role & Context | Key Needs from CI-Bot |
|---------|----------------|----------------------|
| **Executive Leadership** | CEO, CTO, VP Sales — Strategic decision-makers requiring high-level market awareness without information overload | 5-minute daily scan; clear threat/opportunity signals; strategic implications highlighted; no noise |
| **Product Team** | Head of Product, Product Managers — Building AMP roadmap and prioritizing features against competitive landscape | Feature-level competitive analysis; AI capability benchmarking; validation of roadmap priorities; threat assessment for existing features |

### 3.2 Secondary Users (V2 Expansion)

Sales Team, Marketing Team, and AdOps will be served in V2 with tailored content and additional channels. MVP will provide view-only access to the primary channel for awareness.

---

## 4. Functional Requirements

### 4.1 Source Monitoring (Tier 1 Only)

| Source | Coverage & Rationale |
|--------|---------------------|
| **AdExchanger** | adexchanger.com — Primary source for programmatic and AI news; technical depth suitable for Product team analysis |
| **Digiday** | digiday.com — Candid industry reporting; strong AI section; agency adoption trends relevant to AMP positioning |
| **Ad Age** | adage.com — Mainstream coverage of AI-powered media buying; Google Performance Max developments; brand-side tools |
| **Adweek** | adweek.com/category/artificial-intelligence/ — Dedicated AI vertical; agent-to-agent media buying; DSP automation coverage |

### 4.2 Content Processing

#### FR-2.1: Article Ingestion

- Ingest articles via RSS feeds (primary) with web scraping fallback
- Extract: headline, publication date, author, full text, source URL
- Deduplicate across sources using headline similarity matching
- Daily processing window: 12:00 AM - 6:00 AM to capture previous day's content

#### FR-2.2: AI Relevance Classification

LLM-based filtering with the following topic taxonomy:

| Category | Keywords/Signals | Alkimi Relevance |
|----------|------------------|------------------|
| Campaign Automation | Auto-optimization, AI bidding, budget pacing, workflow automation | Direct AMP competitor signal |
| Cross-DSP Tools | Multi-platform, unified dashboard, cross-channel, platform-agnostic | Core AMP value prop threat |
| AI Reporting/Analytics | Natural language insights, conversational BI, automated reporting | AMP chat interface competitor |
| Payment Innovation | Real-time settlement, faster payments, blockchain, publisher payments | Zero-Day Payments threat |
| Web3 Advertising | Token-gated, wallet targeting, crypto audiences, decentralized | Alkimi Exchange positioning |

#### FR-2.3: Threat Categorization (MVP - Manual)

For MVP, an editor (Automation Specialist) will review AI-filtered articles and assign:

- **Threat Level:** HIGH (red) / MEDIUM (yellow) / LOW (green) / OPPORTUNITY (blue)
- **Product Impact:** AMP / Zero-Day Payments / Both / General Market
- **Action Recommendation:** Watch / Discuss / Urgent Response

---

## 5. Slack Integration Specifications

### 5.1 Channel Configuration

| Channel | Purpose & Members |
|---------|-------------------|
| `#ci-intel-leadership` | Primary channel for Executive + Product team; daily digest + weekly summary; private channel |
| `#ci-intel-alerts` | HIGH priority alerts only; immediate notification; @channel mentions enabled |

### 5.2 Daily Digest Format

Delivered at **8:00 AM local time** (Monday-Friday). Designed for <3 minute executive scan.

**Example Daily Digest:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🤖 CI-Bot Daily Brief | Mon, Jan 6, 2026
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔴 HIGH | AMP Threat
TTD Launches "Kokai" AI Campaign Automation
New AI layer automates bid optimization and budget
allocation across channels. Direct overlap with AMP's
unified optimization value prop.
⚡ Action: Discuss | 📰 AdExchanger

🟡 MEDIUM | Zero-Day Watch
Magnite Pilots "Express Pay" for Publishers
Testing 7-day payment terms (vs 60-90 day standard).
Traditional rails, limited scale. Not blockchain-based.
⚡ Action: Watch | 📰 Digiday

🔵 OPPORTUNITY | Market Validation
Survey: 67% of Agencies Want Unified DSP Tools
Digiday+ research shows strong demand for cross-
platform management. Key data point for AMP sales.
⚡ Action: Share with Sales | 📰 Digiday

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Today: 47 articles scanned | 3 surfaced | 1 high priority
```

### 5.3 Weekly Summary Format

Delivered **Friday 4:00 PM**. Aggregated view for weekly leadership review.

**Example Weekly Summary:**

```
📊 CI-Bot Weekly Summary | Jan 6-10, 2026

📈 WEEKLY VOLUME
Articles Scanned: 234 | Relevant: 12 | High Priority: 3

⚔️ THREAT SUMMARY
• AMP: 4 items (TTD, Google, Basis active)
• Zero-Day: 2 items (Magnite, PubMatic testing)

🔥 KEY TREND: Agent-to-agent media buying (3 mentions)

💬 Suggested topic for Monday strategy sync
```

---

## 6. Competitive Threat Framework

The MVP will track specific competitors and signals relevant to Alkimi's two primary products:

### 6.1 AMP Competitive Landscape

| Competitor | Threat Type | Watch For | Priority |
|------------|-------------|-----------|----------|
| The Trade Desk | AI automation, Kokai platform | Cross-channel optimization, unified workflows | Critical |
| Google DV360 | Native AI capabilities | Performance Max expansion, automated bidding | Critical |
| Mediaocean / Basis | Multi-DSP management | Unified dashboards, workflow tools | High |
| Adverity / Funnel.io | AI reporting/analytics | Natural language insights, automated reporting | Medium |

### 6.2 Zero-Day Payments Competitive Landscape

| Competitor | Threat Type | Watch For | Priority |
|------------|-------------|-----------|----------|
| Magnite | Accelerated payments | Express Pay expansion, publisher adoption | High |
| PubMatic | Payment terms innovation | Faster settlement programs, financing | High |
| Index Exchange | Transparency initiatives | Fee transparency, supply path clarity | Medium |
| Brave Ads / Permission.io | Web3 alternative | Crypto-native advertising adoption | Medium |

---

## 7. Technical Architecture (MVP)

### 7.1 System Components

1. **RSS Aggregator:** Feedparser-based collection from Tier 1 sources (Python)
2. **LLM Processor:** Claude API for relevance classification and summarization
3. **Simple Storage:** SQLite database for article tracking and deduplication
4. **Slack Bot:** Bolt framework for message formatting and delivery
5. **Scheduler:** Cron job for daily 6:00 AM processing, 8:00 AM delivery

### 7.2 Data Flow

```
RSS Feeds → Aggregator → LLM Filter → Editor Review Queue → Threat Assignment → Slack Formatter → Channel Delivery
```

---

## 8. Success Metrics

| Metric | MVP Target (4 weeks) | Measurement |
|--------|---------------------|-------------|
| Daily Digest Open Rate | >80% of primary users | Slack read receipts |
| Signal-to-Noise Ratio | <5 items per daily digest | Average items surfaced |
| Actionable Intelligence | >50% items discussed in meetings | User survey |
| Executive Satisfaction | NPS >40 | Week 4 survey |

---

## 9. Implementation Timeline

| Week | Deliverables | Owner | Dependencies |
|------|--------------|-------|--------------|
| Week 1 | RSS integration for 4 sources; SQLite schema; basic ingestion pipeline | Automation Specialist | Claude API access |
| Week 2 | LLM classification prompts; relevance filtering; editor review interface | Automation Specialist | Taxonomy approval from Product |
| Week 3 | Slack bot setup; message formatting; channel configuration; scheduling | Automation Specialist | Slack workspace admin access |
| Week 4 | Testing with primary users; feedback incorporation; documentation; launch | Automation Specialist + Product | Executive availability for testing |

---

## 10. MVP User Stories

### US-MVP-001: Daily Executive Brief

**As** a CEO, **I want** a daily Slack digest of competitive AI developments **so that** I can stay informed without reading multiple publications.

**Acceptance Criteria:**
1. Digest arrives by 8:00 AM on business days
2. Each item includes: headline, 2-sentence summary, threat level, source
3. Maximum 5 items per digest (high signal-to-noise)
4. Scannable in under 3 minutes

**Priority:** P0

---

### US-MVP-002: Product Threat Assessment

**As** a Product Manager, **I want** competitive items tagged by product impact (AMP/Zero-Day) **so that** I can quickly identify threats to my roadmap.

**Acceptance Criteria:**
1. Each item tagged with impacted product
2. Threat level clearly visible (color-coded)
3. Action recommendation included

**Priority:** P0

---

### US-MVP-003: Weekly Summary

**As** an Executive, **I want** a weekly summary of competitive trends **so that** I can prepare for leadership discussions.

**Acceptance Criteria:**
1. Delivered Friday 4:00 PM
2. Includes: volume stats, threat breakdown by product, top trend
3. Suggests discussion topic for leadership sync

**Priority:** P1

---

## 11. Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| RSS feed changes break ingestion | Missing articles for 1+ sources | Monitor feed health; fallback to web scraping; alert on failures |
| LLM hallucinations in summaries | Inaccurate intelligence; trust erosion | Always link to source; editor review for HIGH items; retrieval-augmented generation |
| Alert fatigue from low relevance | Users ignore digests | Strict relevance threshold; limit to 5 items/day; feedback loop |
| Editor bottleneck delays digest | Late or missing daily briefings | Clear SLA (review by 7:30 AM); backup reviewer assigned |

---

## 12. Open Questions

- [ ] Confirm Slack channel naming convention with IT
- [ ] Determine if Digiday+ subscription needed for full article access
- [ ] Validate Claude API rate limits support 4-source daily processing
- [ ] Identify backup editor for vacation/sick coverage

---

## 13. Appendix: LLM Classification Prompt (Draft)

```
You are a competitive intelligence analyst for Alkimi, an AdTech company with two key products:
1. AMP (Advertiser Management Platform) - unified multi-DSP campaign management with AI reporting
2. Zero-Day Payments - blockchain-based instant publisher settlement

Analyze the following article and determine:
1. RELEVANCE (1-5): How relevant is this to AI/automation in advertising?
2. CATEGORY: Campaign Automation | Cross-DSP Tools | AI Reporting | Payment Innovation | Web3 Advertising | Other
3. PRODUCT_IMPACT: AMP | Zero-Day | Both | General
4. SUMMARY: 2-sentence summary focusing on competitive implications for Alkimi

Article:
{article_text}

Respond in JSON format.
```

---

*End of MVP Document*

*See CI-Bot V2 PRD for future state capabilities including Google Sheets integration, team-specific channels, and automated threat scoring.*
