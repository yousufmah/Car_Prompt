# Car Listing API Research
*Research conducted: 2026-02-26*

## Executive Summary

For CarPrompt to be useful, we need access to real car listings. Below are the best API options for UK and US markets, with recommendations for MVP vs. production.

## Primary Options

### 1. Marketcheck API (US/Canada/UK)
**Best for:** Production-ready, comprehensive coverage
**Coverage:** US, Canada, UK
**Data:** New/used/certified/auction/private listings
**Update frequency:** Daily
**Pricing:** Pay-per-call (see below)
**API Types:**
- **Inventory Search API:** $0.002/call - search by criteria
- **Dealer API:** $0.0025/call - dealer inventories
- **Private Party API:** $0.01/call - private seller listings
- **Auction API:** $0.008/call - auction listings
**Pros:**
- Most comprehensive coverage
- UK data available
- Real-time updates
- Clean, normalized data
**Cons:**
- Cost adds up with high volume
- Requires API key and payment
**Best for:** Production when budget allows

### 2. eBay Motors API (Global)
**Best for:** Large volume, auction & fixed price
**Coverage:** Global (eBay Motors listings)
**API:** eBay Browse API (part of eBay Developers Program)
**Requirements:**
- Production approval required (contract with eBay)
- Standard eligibility requirements
- Rate limits apply
**Pros:**
- Massive inventory (millions of listings)
- Global coverage
- Includes auction and fixed price
**Cons:**
- Complex approval process
- Must comply with eBay policies
- Not UK-specific (but includes UK)
**Best for:** Established companies with legal/resources

### 3. Edmunds API (US Only)
**Best for:** Vehicle specs and pricing, NOT listings
**Coverage:** US only
**API Types:**
- Vehicle API: Specs, equipment, options
- Dealer API: Dealer info, ratings, reviews
- Editorial API: Reviews, articles
**Important:** **Dealer inventories NOT available**
**Pros:**
- Excellent vehicle specification data
- Free tier available
- Good for enhancing listings with specs
**Cons:**
- No actual listings/inventory data
- US only
**Best for:** Supplementing listing data with specs

### 4. AutoTrader UK (No Public API)
**Reality:** AutoTrader.co.uk dominates UK market but has no public API
**Options:**
1. **Partnership:** Direct partnership possible for established businesses
2. **Scraping:** Technically possible but legally risky (ToS violation)
3. **Affiliate:** Possibly through affiliate programs (not API)
**Verdict:** Not feasible for startup MVP

### 5. Cars.com / CarGurus / TrueCar (US)
**Similar situation:** No public APIs or restricted access
**Typically:** Require established partnerships
**Not viable** for early-stage startup

## UK-Specific Considerations

### UK Market Landscape
1. **AutoTrader:** ~500k listings, dominant player
2. **Motors.co.uk:** ~200k listings (owned by AutoTrader)
3. **PistonHeads:** Niche/performance (Haymarket)
4. **Gumtree:** Private sellers (owned by eBay)
5. **Facebook Marketplace:** Growing for private sales

### UK API Options Assessment
1. **Marketcheck (UK):** Best bet - has UK coverage
2. **eBay UK:** Through eBay API (includes Gumtree listings?)
3. **Direct dealer feeds:** Individual dealerships may provide CSV/XML
4. **Specialist aggregators:** May exist but hard to find

## MVP Strategy Recommendations

### Phase 1: Mock Data (Current)
✅ **Implemented:** `seed.py` with 20 realistic listings
✅ **Good for:** Development, testing, demo
✅ **Cost:** $0
**Use until:** Ready for production launch

### Phase 2: Hybrid Approach
1. **Marketcheck API** for core search results
2. **Cache results** to reduce API calls
3. **Fallback to mock data** during development
4. **Implement rate limiting** to control costs

**Estimated Monthly Cost:**
- 1,000 searches/day × $0.002 = $2/day = $60/month
- Plus additional calls for details

### Phase 3: Multiple Sources
1. **Marketcheck** primary
2. **eBay Motors** secondary (if approved)
3. **Direct dealer integrations** (long-term)

## Technical Implementation Plan

### 1. API Abstraction Layer
```python
class ListingProvider:
    def search(self, filters) -> List[CarListing]:
        # Switch between mock/Marketcheck/eBay
        pass
```

### 2. Caching Strategy
- Redis cache for frequent searches
- TTL: 1-6 hours (car prices don't change minute-to-minute)
- Geographic caching (by postcode region)

### 3. Cost Optimization
- Batch similar searches
- Pagination limits (show top 20, not all 500)
- Lazy loading of details

### 4. Fallback System
```python
try:
    return marketcheck.search(filters)
except (APIError, RateLimit):
    return mock_provider.search(filters)  # With disclaimer
```

## Legal & Compliance

### Important Considerations
1. **Terms of Service:** Must comply with each API's ToS
2. **Data Usage:** How listings are displayed/attributed
3. **Privacy:** User search data handling
4. **Attribution:** Required by some APIs (e.g., "Powered by Marketcheck")
5. **Commercial Use:** Ensure proper licensing

### UK-Specific
- GDPR compliance for user data
- Distance selling regulations if facilitating sales
- Consumer rights information

## Action Plan

### Immediate (Week 1-2)
1. [ ] Sign up for Marketcheck free trial
2. [ ] Test API with sample searches
3. [ ] Implement abstraction layer in `backend/app/providers/`
4. [ ] Add caching (Redis or SQLite cache)
5. [ ] Create "demo mode" toggle (mock vs real)

### Short-term (Month 1)
1. [ ] Implement proper error handling
2. [ ] Add rate limiting
3. [ ] Monitor API costs
4. [ ] Apply for eBay Developers Program (optional)

### Long-term (Month 2-3)
1. [ ] Evaluate additional data sources
2. [ ] Consider direct dealer partnerships
3. [ ] Explore UK-specific providers
4. [ ] Implement advanced caching (predictive)

## Cost Projections

| Stage | Searches/Day | Cost/Day | Cost/Month | Notes |
|-------|--------------|----------|------------|-------|
| MVP | 100 | $0.20 | $6 | Initial launch |
| Growth | 1,000 | $2.00 | $60 | Steady traffic |
| Scale | 10,000 | $20.00 | $600 | Popular service |

**Note:** Costs scale linearly with usage. Need business model to cover.

## Conclusion

**Recommended path:**
1. **Start with Marketcheck API** - most straightforward
2. **Keep mock data** for development/fallback
3. **Implement smart caching** to control costs
4. **Monitor usage** and optimize

**UK focus:** Marketcheck has UK coverage, making it viable for CarPrompt's target market.

**Next step:** Get Marketcheck API key and test integration.