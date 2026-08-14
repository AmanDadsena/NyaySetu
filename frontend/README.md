# Nyaysetu — frontend

Next.js 16 (App Router), React 19, Tailwind v4. See the [root README](../README.md)
for what the project is and how the backend answers.

```bash
npm install
npm run dev        # http://localhost:3000
```

Expects the API at `http://localhost:8000`, or wherever `NEXT_PUBLIC_API_URL`
points.

## Worth knowing before changing things

**This is not the Next.js you may remember.** Version 16 has breaking changes
against older conventions; read the relevant guide under
`node_modules/next/dist/docs/` before reaching for a pattern from memory. See
[AGENTS.md](AGENTS.md).

**Language is resolved server-side** from a cookie, so a Tamil visitor never
sees a frame of English. Translations live in `src/lib/i18n/translations.ts` —
100 keys, complete across all eight locales. `en` is the source of truth and
defines the key set; every other locale is a `Partial` of it, so a missing key
falls back to English at lookup rather than breaking the build.

**The toolkit works offline.** `src/lib/toolkit/offline.ts` holds the lookup
tables fetched once and cached, with the deadline arithmetic repeated in the
browser. It is deliberate duplication of the Python, and
`backend/scripts/check_offline_parity.py` fails if the two ever disagree — run
it after touching either side.

**Sign-in is attached to actions, not routes.** Every page stays browsable;
pressing a button that does work redirects to `/login?next=…` and the sign-in
page says what it was for. See `src/lib/auth/AuthGate.tsx`.

## Checks

```bash
npx tsc --noEmit
npm run build
```
