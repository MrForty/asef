# Web Experience

## When to load

Creating, redesigning or reviewing a website or app UI. For a local fix, load only the affected checks; preserve the established design. This guide supplements the active module, never adds a route or mandatory approval round.

## Design contract

Record once in `SPEC.md` UI, or link the existing design system:

| Decision | Required evidence |
|---|---|
| Audience and action | Who uses this page, their question or task, the primary action and its real destination |
| Content and hierarchy | Page/section order from real content, meaningful headings, exact key copy; mark missing client assets or facts `OPEN` |
| Visual direction | One coherent direction tied to brand, audience and content; reference what to learn, never clone a reference site |
| Design tokens | Typography roles and fallback fonts, color roles, spacing scale, grid/width, image treatment, interaction and motion rules |
| Responsive behavior | How content reflows, navigation changes, text wraps and controls remain usable; include long content and error states |

For substantial new UI, implement one representative page or flow at narrow and wide widths before repeating the pattern. Inspect it, correct the direction, then reuse its primitives. Offer alternatives only if uncertainty warrants them; do not generate three full sites by default.

## Originality gate

- Derive composition from this content and audience. If swapping the logo and nouns makes the page fit an unrelated business unchanged, revise hierarchy, copy or imagery.
- Remove interchangeable slogans, invented testimonials, client logos, metrics and empty decorative sections. Use verified content; visible draft placeholders cannot pass publication QA.
- Gradients, oversized heroes, pill labels, glass panels and identical card grids are choices, never defaults. Keep one only when it serves hierarchy, brand or interaction; novelty alone is not a requirement.
- Use purposeful, licensed imagery with suitable crop and alternatives. Prefer client assets; do not require image generation or a proprietary service.
- Originality never justifies unfamiliar basic controls, illegible text, scroll hijacking, excessive animation or replacing a working design system without scope authority.

## Website delivery

Apply to public content pages, not private app screens. Record applicable items in `SPEC.md` Website delivery; use `N/A` with a reason for the rest.

- Map page purpose, navigation, stable URLs, content source and editor ownership. Add a CMS only for a real editing workflow; prefer existing tooling or static output when sufficient.
- Specify titles/descriptions, semantic headings, canonical URLs, crawl/index intent, share previews and sitemap when useful. Structured data must match visible verified content. Protect private content with authorization, not robots rules.
- Preserve inbound links; map redirects when URLs change. Test navigation, error pages, downloads and primary actions. A form must deliver to its actual destination with server-side validation, abuse handling and success/failure feedback; simulated success is not completion.
- Identify analytics, embeds and consent requirements from project constraints before adding tracking. Keep secrets server-side; expose no personal data in URLs or logs.

## Verification

- Render at narrow and wide widths plus a content-driven breakpoint; check overflow, zoom, long text, keyboard order, visible focus, labels, contrast and reduced motion. Use semantic HTML and native controls first. Default target: WCAG 2.2 AA; claim only the criteria actually checked.
- Compare the view with the design contract and baseline using screenshots; check content, assets, links, empty/loading/error/success states and console/network errors, not only compilation.
- Set measurable performance targets for the target device/network; check loading, responsiveness and layout stability. Optimize images/fonts and ship only required JavaScript. Report lab conditions separately from field data; no score or ranking guarantees.
- Without browser or execution, use the host fallbacks in `CONTEXT-MANAGER.md`; visual and runtime criteria stay `OPEN`.

References, consulted on demand: [WCAG](https://www.w3.org/WAI/WCAG22/quickref/), [Search fundamentals](https://developers.google.com/search/docs/fundamentals/seo-starter-guide), [Web Vitals](https://web.dev/articles/vitals). Verify current requirements before making compliance or threshold claims.
