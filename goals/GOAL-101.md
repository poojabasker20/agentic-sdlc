Goal: A Smarter, More Welcoming Greeting Experience for International Customers

Background & Problem Statement
As we expand our services across Europe (especially Spain, France, Germany, and the Nordics), our partner teams and client portals are telling us that our current greeting service feels cold, generic, and too Anglo-centric. Right now, every user gets a flat English greeting regardless of who they are, where they are calling from, or what time of day it is.

We want to transform the greeting service into an intelligent, personalized first touchpoint for international users that feels natural, polite, and culturally aware.

What We Want to Deliver:

1. Speak the Customer's Language:
   - We need to support our major European markets (Spanish, French, German, and Swedish, along with English).
   - The greetings shouldn't just be static translations — they should be time-aware so users get a cheerful "Good morning", "Good afternoon", or "Good evening" in their native tongue.

2. Make VIPs and Professionals Feel Recognized:
   - Clients want to address their users respectfully with formal titles or salutations (like Dr., Professor, Herr, Madame, Señor, etc.) without having to manually concatenate strings on the frontend.

3. Seamless Language Detection:
   - The caller app should be able to explicitly choose a language or let the system pick it up automatically from user preferences and browser settings.
   - If we aren't sure or if the language isn't specified, smoothly fall back to English.

4. Business Insights & Usage Tracking:
   - The product team needs visibility into how many users are asking for greetings in French vs Spanish vs German so we know where to invest in further localization.

5. Friendly and Helpful Fallbacks:
   - If an unsupported language is requested, don't crash or return blank text — give client developers a clear, polite explanation of what languages are available.

Key Expectations & Boundaries:

- Zero Disruptions: Thousands of existing services already use our current greeting endpoint. We cannot break existing integrations or change existing behavior for legacy callers.
- Fast and Responsive: Greetings appear on initial page loads and dashboards, so response times must stay instantaneous.
